import asyncio
import threading
import time
import websockets
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import our modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import User, Room, GameRound, BetData, GameState, GameRoundStatus
from src.game_engine import GameEngine
from src.game_server import GameServer
from src.game_client import GameClient
from proto import game_messages_pb2 as pb


# Test User model functionality
def test_create_user():
    """Test user creation with password hashing"""
    user = User.create_user(1, "testuser", "password123", 1000)
    
    assert user.user_id == 1
    assert user.username == "testuser"
    assert user.balance == 1000
    assert user.password_hash is not None
    assert user.verify_password("password123")
    assert not user.verify_password("wrongpassword")


def test_session_token_generation():
    """Test session token generation and validation"""
    user = User.create_user(1, "testuser", "password123")
    
    token = user.generate_session_token()
    assert token is not None
    assert user.session_token == token
    assert not user.is_session_expired()
    
    # Test expired session
    user.last_activity = datetime.now() - timedelta(seconds=1801)
    assert user.is_session_expired()


# Test Room model functionality
def test_room_add_player():
    """Test adding players to room"""
    room = Room(1, "Test Room", max_capacity=2)
    
    assert room.add_player(1)
    assert room.add_player(2)
    assert not room.add_player(3)  # Should fail due to capacity
    assert room.get_player_count() == 2


def test_room_remove_player():
    """Test removing players from room"""
    room = Room(1, "Test Room")
    room.add_player(1)
    room.add_player(2)
    
    room.remove_player(1)
    assert room.get_player_count() == 1
    assert 1 not in room.current_players
    assert 2 in room.current_players


# Test GameRound model functionality
def test_game_round_creation():
    """Test game round creation"""
    round_obj = GameRound.create_round(1, 1)
    
    assert round_obj.user_id == 1
    assert round_obj.room_id == 1
    assert round_obj.status == GameRoundStatus.BETTING_PHASE
    assert len(round_obj.bets) == 0
    assert round_obj.round_id is not None


def test_game_round_add_bet():
    """Test adding bets to game round"""
    round_obj = GameRound.create_round(1, 1)
    bet = BetData.create_bet(1, round_obj.round_id, 3, 100)
    
    round_obj.add_bet(bet)
    assert len(round_obj.bets) == 1
    assert round_obj.bets[0].dice_face == 3
    assert round_obj.bets[0].amount == 100


@patch('random.SystemRandom.randint')
def test_game_round_calculate_results(mock_randint):
    """Test result calculation for game round"""
    mock_randint.return_value = 3  # Fixed dice result
    
    round_obj = GameRound.create_round(1, 1)
    bet1 = BetData.create_bet(1, round_obj.round_id, 3, 100)  # Will win
    bet2 = BetData.create_bet(1, round_obj.round_id, 6, 50)   # Will lose
    round_obj.add_bet(bet1)
    round_obj.add_bet(bet2)
    
    # Calculate results with dice showing 3
    total_winnings = round_obj.calculate_results(3)
    
    assert total_winnings == 600  # 100 * 6 payout
    assert bet1.won is True
    assert bet1.payout == 600
    assert bet2.won is False
    assert bet2.payout == 0


# Fixtures for GameEngine tests
@pytest.fixture
def game_state():
    """Create a game state with test data"""
    state = GameState()
    
    # Add test users
    user1 = User.create_user(1, "testuser1", "password123", 1000)
    user2 = User.create_user(2, "testuser2", "password123", 1000)
    state.users[1] = user1
    state.users[2] = user2
    
    # Add test rooms
    room1 = Room(1, "Test Room 1")
    room2 = Room(2, "Test Room 2")
    state.rooms[1] = room1
    state.rooms[2] = room2
    
    return state


@pytest.fixture
def game_engine(game_state):
    """Create a game engine with test data"""
    return GameEngine(game_state)


@pytest.fixture
def user(game_state):
    """Get test user"""
    return game_state.users[1]


# Test GameEngine functionality
@pytest.mark.asyncio
async def test_place_bet_success(game_engine, user, game_state):
    """Test successful bet placement"""
    # User needs to join a room first
    await game_state.join_room(1, 1)
    
    success, message, bet_id = await game_engine.place_bet(1, 3, 100)
    
    assert success, f"Expected success but got: {message}"
    assert message == "Bet placed successfully"
    assert bet_id is not None
    assert user.balance == 900  # 1000 - 100


@pytest.mark.asyncio
async def test_place_bet_insufficient_balance(game_engine, user, game_state):
    """Test bet placement with insufficient balance"""
    # User needs to join a room first
    await game_state.join_room(1, 1)
    # Set user balance to 50, then try to bet 100 (within max limit but exceeds balance)
    user.balance = 50
    success, message, bet_id = await game_engine.place_bet(1, 3, 100)
    
    assert not success
    assert message == "Insufficient balance"
    assert bet_id is None
    assert user.balance == 50  # Unchanged


@pytest.mark.asyncio
async def test_place_bet_invalid_dice_face(game_engine):
    """Test bet placement with invalid dice face"""
    success, message, bet_id = await game_engine.place_bet(1, 7, 100)
    
    assert not success
    assert message == "Invalid dice face (must be 1-6)"
    assert bet_id is None


@pytest.mark.asyncio
async def test_place_bet_invalid_amount(game_engine):
    """Test bet placement with invalid bet amount"""
    # Test amount too high
    success, message, bet_id = await game_engine.place_bet(1, 3, 2000)
    
    assert not success
    assert message == "Invalid bet amount (1-1000)"
    assert bet_id is None
    
    # Test amount too low
    success, message, bet_id = await game_engine.place_bet(1, 3, 0)
    
    assert not success
    assert message == "Invalid bet amount (1-1000)"
    assert bet_id is None


@pytest.mark.asyncio
@patch('random.SystemRandom.randint')
async def test_calculate_results_winning_bet(mock_randint, game_engine, game_state):
    """Test result calculation with winning bet"""
    mock_randint.return_value = 3  # Fixed dice result
    
    # User needs to join a room first
    await game_state.join_room(1, 1)
    
    # Place bet and finish betting
    success, message, bet_id = await game_engine.place_bet(1, 3, 100)
    assert success, f"Expected success but got: {message}"
    
    # Get the round ID from active rounds
    user_rounds = [r for r in game_engine.game_state.active_rounds.values() if r.user_id == 1]
    assert len(user_rounds) == 1
    round_id = user_rounds[0].round_id
    
    # Finish betting
    success, message = await game_engine.finish_betting(1, round_id)
    assert success
    
    # Calculate results
    success, message, results = await game_engine.calculate_results(1, round_id)
    assert success, f"Expected success but got: {message}"
    assert results is not None
    assert results['dice_result'] == 3
    assert results['total_winnings'] == 600  # 100 * 6
    assert results['new_balance'] == 1500  # 900 + 600


@pytest.mark.asyncio
async def test_get_user_snapshot(game_engine, game_state):
    """Test getting user game state snapshot"""
    # User needs to join a room first
    await game_state.join_room(1, 1)
    
    # Place a bet first
    success, message, bet_id = await game_engine.place_bet(1, 3, 100)
    assert success, f"Expected success but got: {message}"
    
    snapshot = await game_engine.get_user_snapshot(1)
    assert snapshot is not None
    assert snapshot['user_balance'] == 900
    assert len(snapshot['active_bets']) == 1
    assert snapshot['active_bets'][0]['dice_face'] == 3
    assert snapshot['active_bets'][0]['amount'] == 100


# Test GameState functionality
@pytest.mark.asyncio
async def test_authenticate_user(game_state):
    """Test user authentication"""
    # Test valid credentials
    user = await game_state.authenticate_user("testuser1", "password123")
    assert user is not None
    assert user.username == "testuser1"
    assert user.session_token is not None
    
    # Test invalid credentials
    user = await game_state.authenticate_user("testuser1", "wrongpassword")
    assert user is None
    
    # Test non-existent user
    user = await game_state.authenticate_user("nonexistent", "password")
    assert user is None


@pytest.mark.asyncio
async def test_join_room(game_state):
    """Test room joining functionality"""
    user = game_state.users[1]
    
    # Test successful room join
    success = await game_state.join_room(1, 1)
    assert success
    assert user.current_room == 1
    assert 1 in game_state.rooms[1].current_players
    
    # Test joining another room (should leave previous room)
    success = await game_state.join_room(1, 2)
    assert success
    assert user.current_room == 2
    assert 1 not in game_state.rooms[1].current_players
    assert 1 in game_state.rooms[2].current_players


@pytest.mark.asyncio
async def test_create_game_round(game_state):
    """Test game round creation"""
    # User needs to join a room first to create game rounds
    await game_state.join_room(1, 1)
    
    round_obj = await game_state.create_game_round(1)
    assert round_obj is not None
    assert round_obj.user_id == 1
    assert round_obj.status == GameRoundStatus.BETTING_PHASE
    assert round_obj.round_id in game_state.active_rounds


# Integration tests would go here, but they require more complex setup
# These would test the full WebSocket server/client interaction
# For now, we'll focus on unit tests that can be easily converted

def test_error_codes():
    """Test error code constants"""
    # These would be imported from a constants module
    # For now, just verify they exist in the pb module
    assert hasattr(pb, 'ErrorResponse')


def test_protocol_messages():
    """Test protocol buffer message creation"""
    login_req = pb.LoginRequest()
    login_req.username = "test"
    login_req.password = "test"
    
    assert login_req.username == "test"
    assert login_req.password == "test"
    
    # Test serialization
    data = login_req.SerializeToString()
    assert len(data) > 0
    
    # Test deserialization
    login_req2 = pb.LoginRequest()
    login_req2.ParseFromString(data)
    assert login_req2.username == "test"
    assert login_req2.password == "test"