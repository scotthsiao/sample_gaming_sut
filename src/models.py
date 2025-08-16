from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum
import uuid
import bcrypt
import asyncio


class GameRoundStatus(Enum):
    NO_ACTIVE_ROUND = 0
    BETTING_PHASE = 1
    WAITING_RESULTS = 2


@dataclass
class User:
    user_id: int
    username: str
    password_hash: str
    balance: int
    session_token: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.now)
    current_room: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_user(cls, user_id: int, username: str, password: str, balance: int = 1000):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        return cls(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            balance=balance
        )

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def generate_session_token(self) -> str:
        self.session_token = str(uuid.uuid4())
        self.last_activity = datetime.now()
        return self.session_token

    def update_activity(self):
        self.last_activity = datetime.now()

    def is_session_expired(self, timeout_seconds: int = 1800) -> bool:
        if not self.session_token:
            return True
        return (datetime.now() - self.last_activity).total_seconds() > timeout_seconds


@dataclass
class Room:
    room_id: int
    name: str
    max_capacity: int = 50
    current_players: Set[int] = field(default_factory=set)
    jackpot_pool: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def add_player(self, user_id: int) -> bool:
        if len(self.current_players) >= self.max_capacity:
            return False
        self.current_players.add(user_id)
        self.last_activity = datetime.now()
        return True

    def remove_player(self, user_id: int):
        self.current_players.discard(user_id)
        self.last_activity = datetime.now()

    def get_player_count(self) -> int:
        return len(self.current_players)


@dataclass
class BetData:
    bet_id: str
    user_id: int
    round_id: str
    dice_face: int
    amount: int
    won: Optional[bool] = None
    payout: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_bet(cls, user_id: int, round_id: str, dice_face: int, amount: int):
        return cls(
            bet_id=str(uuid.uuid4()),
            user_id=user_id,
            round_id=round_id,
            dice_face=dice_face,
            amount=amount
        )


@dataclass
class GameRound:
    round_id: str
    user_id: int
    room_id: int
    bets: List[BetData] = field(default_factory=list)
    status: GameRoundStatus = GameRoundStatus.BETTING_PHASE
    dice_result: Optional[int] = None
    total_winnings: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None

    @classmethod
    def create_round(cls, user_id: int, room_id: int):
        return cls(
            round_id=str(uuid.uuid4()),
            user_id=user_id,
            room_id=room_id
        )

    def add_bet(self, bet: BetData):
        self.bets.append(bet)

    def finish_betting(self):
        self.status = GameRoundStatus.WAITING_RESULTS

    def calculate_results(self, dice_result: int) -> int:
        self.dice_result = dice_result
        total_winnings = 0
        
        for bet in self.bets:
            won = (bet.dice_face == dice_result)
            payout = bet.amount * 6 if won else 0
            
            bet.won = won
            bet.payout = payout
            total_winnings += payout
        
        self.total_winnings = total_winnings
        self.finished_at = datetime.now()
        return total_winnings


class GameState:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.rooms: Dict[int, Room] = {}
        self.active_rounds: Dict[str, GameRound] = {}
        self.connections: Dict[object, int] = {}  # WebSocket -> user_id
        self.user_connections: Dict[int, object] = {}  # user_id -> WebSocket
        self.next_user_id = 1
        self._lock = asyncio.Lock()
        
        # Initialize default rooms
        self._initialize_default_rooms()
        self._initialize_default_users()

    def _initialize_default_rooms(self):
        for i in range(1, 11):  # Create 10 default rooms
            room = Room(
                room_id=i,
                name=f"Room {i}",
                max_capacity=50
            )
            self.rooms[i] = room

    def _initialize_default_users(self):
        # Create some default test users
        test_users = [
            ("testuser1", "password123"),
            ("testuser2", "password123"),
            ("alice", "alicepass"),
            ("bob", "bobpass"),
            ("charlie", "charliepass")
        ]
        
        for username, password in test_users:
            user = User.create_user(self.next_user_id, username, password, 1000)
            self.users[self.next_user_id] = user
            self.next_user_id += 1

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        async with self._lock:
            for user in self.users.values():
                if user.username == username and user.verify_password(password):
                    # Check if user already has an active session
                    if user.session_token and not user.is_session_expired():
                        return None  # User already logged in
                    
                    user.generate_session_token()
                    return user
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    async def get_user_by_session(self, session_token: str) -> Optional[User]:
        async with self._lock:
            for user in self.users.values():
                if user.session_token == session_token and not user.is_session_expired():
                    user.update_activity()
                    return user
            return None

    async def join_room(self, user_id: int, room_id: int) -> bool:
        async with self._lock:
            user = self.users.get(user_id)
            room = self.rooms.get(room_id)
            
            if not user or not room:
                return False
            
            # Leave current room if any
            if user.current_room:
                current_room = self.rooms.get(user.current_room)
                if current_room:
                    current_room.remove_player(user_id)
            
            # Join new room
            if room.add_player(user_id):
                user.current_room = room_id
                return True
            return False

    async def leave_room(self, user_id: int):
        async with self._lock:
            user = self.users.get(user_id)
            if user and user.current_room:
                room = self.rooms.get(user.current_room)
                if room:
                    room.remove_player(user_id)
                user.current_room = None

    async def get_room(self, room_id: int) -> Optional[Room]:
        return self.rooms.get(room_id)

    async def add_connection(self, websocket, user_id: int):
        async with self._lock:
            self.connections[websocket] = user_id
            self.user_connections[user_id] = websocket

    async def remove_connection(self, websocket):
        async with self._lock:
            user_id = self.connections.pop(websocket, None)
            if user_id:
                self.user_connections.pop(user_id, None)
                # Leave room when disconnecting
                await self.leave_room(user_id)
                # Invalidate session
                user = self.users.get(user_id)
                if user:
                    user.session_token = None

    async def get_user_by_connection(self, websocket) -> Optional[User]:
        user_id = self.connections.get(websocket)
        if user_id:
            return self.users.get(user_id)
        return None

    async def create_game_round(self, user_id: int) -> Optional[GameRound]:
        async with self._lock:
            user = self.users.get(user_id)
            if not user or not user.current_room:
                return None
            
            # Check for existing active round
            for round_obj in self.active_rounds.values():
                if (round_obj.user_id == user_id and 
                    round_obj.status == GameRoundStatus.BETTING_PHASE):
                    return round_obj
            
            # Create new round
            game_round = GameRound.create_round(user_id, user.current_room)
            self.active_rounds[game_round.round_id] = game_round
            return game_round

    async def get_game_round(self, round_id: str) -> Optional[GameRound]:
        return self.active_rounds.get(round_id)

    async def finish_game_round(self, round_id: str):
        async with self._lock:
            self.active_rounds.pop(round_id, None)

    async def cleanup_expired_sessions(self):
        async with self._lock:
            expired_users = []
            for user in self.users.values():
                if user.is_session_expired():
                    expired_users.append(user)
            
            for user in expired_users:
                user.session_token = None
                if user.current_room:
                    await self.leave_room(user.user_id)