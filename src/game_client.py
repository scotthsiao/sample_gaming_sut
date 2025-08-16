import asyncio
import websockets
import struct
import time
import logging
from typing import Dict, Optional, List
import argparse

# Import generated protobuf messages
try:
    from proto import game_messages_pb2 as pb
except ImportError:
    print("Error: Protocol buffer files not generated. Run: protoc --python_out=. --pyi_out=. proto/game_messages.proto")
    import sys
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Command ID constants
C2S_LOGIN_REQ = 0x0001
S2C_LOGIN_RSP = 0x1001
C2S_ROOM_JOIN_REQ = 0x0002
S2C_ROOM_JOIN_RSP = 0x1002
C2S_SNAPSHOT_REQ = 0x0003
S2C_SNAPSHOT_RSP = 0x1003
C2S_BET_PLACEMENT_REQ = 0x0004
S2C_BET_PLACEMENT_RSP = 0x1004
C2S_BET_FINISHED_REQ = 0x0005
S2C_BET_FINISHED_RSP = 0x1005
C2S_RECKON_RESULT_REQ = 0x0006
S2C_RECKON_RESULT_RSP = 0x1006
S2C_ERROR_RSP = 0x9999


class GameClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.websocket = None
        self.authenticated = False
        self.user_id = None
        self.balance = 0
        self.current_room = None
        self.session_token = None

    async def connect(self) -> bool:
        """Connect to the game server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info(f"Connected to {self.server_url}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from server")

    async def login(self, username: str, password: str) -> bool:
        """Authenticate with the server"""
        if not self.websocket:
            logger.error("Not connected to server")
            return False

        request = pb.LoginRequest()
        request.username = username
        request.password = password

        await self.send_message(C2S_LOGIN_REQ, request)
        response_data = await self.receive_message()

        if response_data['command_id'] == S2C_LOGIN_RSP:
            response = pb.LoginResponse()
            response.ParseFromString(response_data['payload'])

            if response.success:
                self.authenticated = True
                self.user_id = response.user_id
                self.balance = response.balance
                self.session_token = response.session_token
                logger.info(f"Login successful! User ID: {self.user_id}, Balance: {self.balance}")
                return True
            else:
                logger.error(f"Login failed: {response.message}")
                return False
        elif response_data['command_id'] == S2C_ERROR_RSP:
            error = pb.ErrorResponse()
            error.ParseFromString(response_data['payload'])
            logger.error(f"Login error: {error.error_message}")
            return False
        else:
            logger.error("Unexpected response to login")
            return False

    async def join_room(self, room_id: int) -> bool:
        """Join a game room"""
        if not self.authenticated:
            logger.error("Must be logged in to join room")
            return False

        request = pb.RoomJoinRequest()
        request.room_id = room_id

        await self.send_message(C2S_ROOM_JOIN_REQ, request)
        response_data = await self.receive_message()

        if response_data['command_id'] == S2C_ROOM_JOIN_RSP:
            response = pb.RoomJoinResponse()
            response.ParseFromString(response_data['payload'])

            if response.success:
                self.current_room = response.room_id
                logger.info(f"Joined room {response.room_id} with {response.player_count} players")
                logger.info(f"Jackpot pool: {response.jackpot_pool}")
                return True
            else:
                logger.error(f"Failed to join room: {response.message}")
                return False
        elif response_data['command_id'] == S2C_ERROR_RSP:
            error = pb.ErrorResponse()
            error.ParseFromString(response_data['payload'])
            logger.error(f"Room join error: {error.error_message}")
            return False
        else:
            logger.error("Unexpected response to room join")
            return False

    async def get_snapshot(self) -> Optional[Dict]:
        """Get current game state snapshot"""
        if not self.authenticated:
            logger.error("Must be logged in to get snapshot")
            return None

        request = pb.SnapshotRequest()
        await self.send_message(C2S_SNAPSHOT_REQ, request)
        response_data = await self.receive_message()

        if response_data['command_id'] == S2C_SNAPSHOT_RSP:
            response = pb.SnapshotResponse()
            response.ParseFromString(response_data['payload'])

            active_bets = []
            for bet in response.active_bets:
                active_bets.append({
                    'dice_face': bet.dice_face,
                    'amount': bet.amount,
                    'bet_id': bet.bet_id,
                    'round_id': bet.round_id
                })

            snapshot = {
                'user_balance': response.user_balance,
                'active_bets': active_bets,
                'current_room': response.current_room,
                'jackpot_pool': response.jackpot_pool,
                'round_status': response.round_status
            }

            self.balance = response.user_balance
            return snapshot

        elif response_data['command_id'] == S2C_ERROR_RSP:
            error = pb.ErrorResponse()
            error.ParseFromString(response_data['payload'])
            logger.error(f"Snapshot error: {error.error_message}")
            return None
        else:
            logger.error("Unexpected response to snapshot request")
            return None

    async def place_bet(self, dice_face: int, amount: int, round_id: str = "") -> Optional[str]:
        """Place a bet on dice outcome"""
        if not self.authenticated:
            logger.error("Must be logged in to place bet")
            return None

        request = pb.BetPlacementRequest()
        request.dice_face = dice_face
        request.amount = amount
        request.round_id = round_id

        await self.send_message(C2S_BET_PLACEMENT_REQ, request)
        response_data = await self.receive_message()

        if response_data['command_id'] == S2C_BET_PLACEMENT_RSP:
            response = pb.BetPlacementResponse()
            response.ParseFromString(response_data['payload'])

            if response.success:
                self.balance = response.remaining_balance
                logger.info(f"Bet placed! Bet ID: {response.bet_id}, Remaining balance: {self.balance}")
                return response.round_id
            else:
                logger.error(f"Bet failed: {response.message}")
                return None
        elif response_data['command_id'] == S2C_ERROR_RSP:
            error = pb.ErrorResponse()
            error.ParseFromString(response_data['payload'])
            logger.error(f"Bet placement error: {error.error_message}")
            return None
        else:
            logger.error("Unexpected response to bet placement")
            return None

    async def finish_betting(self, round_id: str) -> bool:
        """Signal end of betting phase"""
        if not self.authenticated:
            logger.error("Must be logged in to finish betting")
            return False

        request = pb.BetFinishedRequest()
        request.round_id = round_id
        await self.send_message(C2S_BET_FINISHED_REQ, request)

        response_data = await self.receive_message()
        if response_data['command_id'] == S2C_BET_FINISHED_RSP:
            response = pb.BetFinishedResponse()
            response.ParseFromString(response_data['payload'])
            
            if response.success:
                logger.info("Betting phase completed successfully")
                return True
            else:
                logger.error(f"Failed to finish betting: {response.message}")
                return False
        elif response_data['command_id'] == S2C_ERROR_RSP:
            error = pb.ErrorResponse()
            error.ParseFromString(response_data['payload'])
            logger.error(f"Finish betting error: {error.error_message}")
            return False
        else:
            logger.error("Unexpected response to finish betting")
            return False

    async def get_results(self, round_id: str) -> Optional[Dict]:
        """Request game results"""
        if not self.authenticated:
            logger.error("Must be logged in to get results")
            return None

        request = pb.ReckonResultRequest()
        request.round_id = round_id
        await self.send_message(C2S_RECKON_RESULT_REQ, request)

        response_data = await self.receive_message()
        if response_data['command_id'] == S2C_RECKON_RESULT_RSP:
            response = pb.ReckonResultResponse()
            response.ParseFromString(response_data['payload'])

            self.balance = response.new_balance

            bet_results = []
            for bet_result in response.bet_results:
                bet_results.append({
                    'bet_id': bet_result.bet_id,
                    'dice_face': bet_result.dice_face,
                    'bet_amount': bet_result.bet_amount,
                    'won': bet_result.won,
                    'payout': bet_result.payout
                })

            results = {
                'dice_result': response.dice_result,
                'total_winnings': response.total_winnings,
                'new_balance': response.new_balance,
                'jackpot_pool': response.updated_jackpot_pool,
                'bet_results': bet_results
            }

            return results
        elif response_data['command_id'] == S2C_ERROR_RSP:
            error = pb.ErrorResponse()
            error.ParseFromString(response_data['payload'])
            logger.error(f"Get results error: {error.error_message}")
            return None
        else:
            logger.error("Unexpected response to get results")
            return None

    async def send_message(self, command_id: int, message):
        """Send a Protocol Buffers message to server"""
        if not self.websocket:
            raise RuntimeError("Not connected to server")

        payload = message.SerializeToString()
        header = struct.pack('<II', command_id, len(payload))
        await self.websocket.send(header + payload)

    async def receive_message(self) -> Dict:
        """Receive and parse a message from server"""
        if not self.websocket:
            raise RuntimeError("Not connected to server")

        # Receive header
        header_data = await self.websocket.recv()
        if len(header_data) < 8:
            raise ValueError("Invalid header size")

        command_id, length = struct.unpack('<II', header_data[:8])
        payload = header_data[8:]

        # Receive remaining payload if needed
        while len(payload) < length:
            additional_data = await self.websocket.recv()
            payload += additional_data

        return {
            'command_id': command_id,
            'payload': payload
        }

    async def play_game_session(self, bets: List[tuple]) -> Dict:
        """Play a complete game session with multiple bets
        
        Args:
            bets: List of (dice_face, amount) tuples
            
        Returns:
            Dictionary with game results
        """
        if not self.authenticated or not self.current_room:
            logger.error("Must be logged in and in a room to play")
            return {}

        # Start with empty round_id - server will create one
        round_id = ""
        
        logger.info(f"Starting game session")
        
        # Place all bets
        for i, (dice_face, amount) in enumerate(bets):
            result_round_id = await self.place_bet(dice_face, amount, round_id)
            if not result_round_id:
                logger.error("Failed to place bet, aborting session")
                return {}
            if i == 0:  # First bet returns the actual round ID
                round_id = result_round_id
                logger.info(f"Server created round ID: {round_id}")

        # Finish betting phase
        if not await self.finish_betting(round_id):
            logger.error("Failed to finish betting phase")
            return {}

        # Get results
        results = await self.get_results(round_id)
        if results:
            logger.info(f"Game session completed:")
            logger.info(f"  Dice result: {results['dice_result']}")
            logger.info(f"  Total winnings: {results['total_winnings']}")
            logger.info(f"  New balance: {results['new_balance']}")
            logger.info(f"  Jackpot pool: {results['jackpot_pool']}")
            
            for bet_result in results['bet_results']:
                status = "WON" if bet_result['won'] else "LOST"
                logger.info(f"  Bet on {bet_result['dice_face']}: ${bet_result['bet_amount']} - {status} (payout: ${bet_result['payout']})")
        
        return results or {}


async def interactive_client():
    """Interactive client for manual testing"""
    client = GameClient("ws://localhost:8765")
    
    if not await client.connect():
        return

    try:
        print("=== Game Client Interactive Mode ===")
        
        # Login
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        if not await client.login(username, password):
            return
        
        # Join room
        room_id = int(input("Room ID (1-10): ").strip())
        if not await client.join_room(room_id):
            return
        
        # Game loop
        while True:
            print("\n=== Game Menu ===")
            print("1. View current status")
            print("2. Place bet")
            print("3. Play quick game (3 bets)")
            print("4. Quit")
            
            choice = input("Choose option: ").strip()
            
            if choice == "1":
                snapshot = await client.get_snapshot()
                if snapshot:
                    print(f"Balance: ${snapshot['user_balance']}")
                    print(f"Room: {snapshot['current_room']}")
                    print(f"Jackpot: ${snapshot['jackpot_pool']}")
                    print(f"Active bets: {len(snapshot['active_bets'])}")
                    
            elif choice == "2":
                try:
                    dice_face = int(input("Dice face (1-6): "))
                    amount = int(input("Bet amount: "))
                    round_id = await client.place_bet(dice_face, amount)
                    if round_id:
                        print(f"Bet placed in round {round_id}")
                except ValueError:
                    print("Invalid input")
                    
            elif choice == "3":
                # Quick game with 3 random bets
                import random
                bets = [(random.randint(1, 6), random.randint(10, 100)) for _ in range(3)]
                print(f"Playing quick game with bets: {bets}")
                await client.play_game_session(bets)
                
            elif choice == "4":
                break
            else:
                print("Invalid choice")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        await client.disconnect()


async def demo_session():
    """Automated demo session"""
    client = GameClient("ws://localhost:8765")
    
    if not await client.connect():
        return

    try:
        # Login with demo user
        if not await client.login("testuser1", "password123"):
            return
        
        # Join room 1
        if not await client.join_room(1):
            return
        
        # Play a demo game
        demo_bets = [
            (3, 100),  # Bet $100 on dice showing 3
            (6, 50),   # Bet $50 on dice showing 6
            (1, 25)    # Bet $25 on dice showing 1
        ]
        
        print("=== Demo Game Session ===")
        results = await client.play_game_session(demo_bets)
        
        if results:
            print("\n=== Demo Completed Successfully ===")
        else:
            print("\n=== Demo Failed ===")
            
    except Exception as e:
        logger.error(f"Demo session error: {e}")
    finally:
        await client.disconnect()


async def main():
    """Main client entry point"""
    parser = argparse.ArgumentParser(description='Game Client')
    parser.add_argument('--server', default='ws://localhost:8765', help='Server URL')
    parser.add_argument('--demo', action='store_true', help='Run automated demo')
    parser.add_argument('--interactive', action='store_true', help='Run interactive client')
    
    args = parser.parse_args()
    
    if args.demo:
        await demo_session()
    elif args.interactive:
        await interactive_client()
    else:
        print("Use --demo for automated demo or --interactive for manual testing")


if __name__ == "__main__":
    asyncio.run(main())