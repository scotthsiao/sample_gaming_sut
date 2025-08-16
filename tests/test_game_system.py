import unittest
import asyncio
import threading
import time
import websockets
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


class TestUser(unittest.TestCase):
    """Test User model functionality"""
    
    def test_create_user(self):
        """Test user creation with password hashing"""
        user = User.create_user(1, "testuser", "password123", 1000)
        
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.balance, 1000)
        self.assertIsNotNone(user.password_hash)
        self.assertTrue(user.verify_password("password123"))
        self.assertFalse(user.verify_password("wrongpassword"))
    
    def test_session_token_generation(self):
        """Test session token generation and validation"""
        user = User.create_user(1, "testuser", "password123")
        
        token = user.generate_session_token()
        self.assertIsNotNone(token)
        self.assertEqual(user.session_token, token)
        self.assertFalse(user.is_session_expired())
        
        # Test expired session
        user.last_activity = datetime.now() - timedelta(seconds=1801)
        self.assertTrue(user.is_session_expired())


class TestRoom(unittest.TestCase):
    """Test Room model functionality"""
    
    def test_room_creation(self):
        """Test room creation and basic operations"""
        room = Room(1, "Test Room", 5)
        
        self.assertEqual(room.room_id, 1)
        self.assertEqual(room.name, "Test Room")
        self.assertEqual(room.max_capacity, 5)
        self.assertEqual(room.get_player_count(), 0)
    
    def test_player_management(self):
        """Test adding and removing players"""
        room = Room(1, "Test Room", 2)
        
        # Add players
        self.assertTrue(room.add_player(1))
        self.assertTrue(room.add_player(2))
        self.assertEqual(room.get_player_count(), 2)
        
        # Try to add player when room is full
        self.assertFalse(room.add_player(3))
        
        # Remove player
        room.remove_player(1)
        self.assertEqual(room.get_player_count(), 1)
        self.assertNotIn(1, room.current_players)


class TestGameRound(unittest.TestCase):
    """Test GameRound model functionality"""
    
    def test_round_creation(self):
        """Test game round creation"""
        round_obj = GameRound.create_round(1, 1)
        
        self.assertEqual(round_obj.user_id, 1)
        self.assertEqual(round_obj.room_id, 1)
        self.assertEqual(round_obj.status, GameRoundStatus.BETTING_PHASE)
        self.assertEqual(len(round_obj.bets), 0)
    
    def test_bet_management(self):
        """Test adding bets to a round"""
        round_obj = GameRound.create_round(1, 1)
        bet = BetData.create_bet(1, round_obj.round_id, 3, 100)
        
        round_obj.add_bet(bet)
        self.assertEqual(len(round_obj.bets), 1)
        self.assertEqual(round_obj.bets[0].dice_face, 3)
        self.assertEqual(round_obj.bets[0].amount, 100)
    
    def test_result_calculation(self):
        """Test calculating round results"""
        round_obj = GameRound.create_round(1, 1)
        
        # Add some bets
        bet1 = BetData.create_bet(1, round_obj.round_id, 3, 100)  # Will win
        bet2 = BetData.create_bet(1, round_obj.round_id, 6, 50)   # Will lose
        round_obj.add_bet(bet1)
        round_obj.add_bet(bet2)
        
        # Calculate results with dice showing 3
        total_winnings = round_obj.calculate_results(3)
        
        self.assertEqual(round_obj.dice_result, 3)
        self.assertEqual(total_winnings, 600)  # 100 * 6
        self.assertTrue(bet1.won)
        self.assertFalse(bet2.won)
        self.assertEqual(bet1.payout, 600)
        self.assertEqual(bet2.payout, 0)


class TestGameEngine(unittest.TestCase):
    """Test GameEngine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game_state = GameState()
        self.game_engine = GameEngine(self.game_state)
        
        # Create test user
        self.user = User.create_user(1, "testuser", "password123", 1000)
        self.game_state.users[1] = self.user
        self.user.current_room = 1
    
    def test_place_bet_success(self):
        """Test successful bet placement"""
        async def run_test():
            success, message, bet_id = await self.game_engine.place_bet(1, 3, 100)
            
            self.assertTrue(success)
            self.assertEqual(message, "Bet placed successfully")
            self.assertIsNotNone(bet_id)
            self.assertEqual(self.user.balance, 900)  # 1000 - 100
        
        asyncio.run(run_test())
    
    def test_place_bet_insufficient_balance(self):
        """Test bet placement with insufficient balance"""
        async def run_test():
            # Set user balance to 50, then try to bet 100 (within max limit but exceeds balance)
            self.user.balance = 50
            success, message, bet_id = await self.game_engine.place_bet(1, 3, 100)
            
            self.assertFalse(success)
            self.assertEqual(message, "Insufficient balance")
            self.assertIsNone(bet_id)
            self.assertEqual(self.user.balance, 50)  # Unchanged
        
        asyncio.run(run_test())
    
    def test_place_bet_invalid_dice_face(self):
        """Test bet placement with invalid dice face"""
        async def run_test():
            success, message, bet_id = await self.game_engine.place_bet(1, 7, 100)
            
            self.assertFalse(success)
            self.assertEqual(message, "Invalid dice face (must be 1-6)")
            self.assertIsNone(bet_id)
        
        asyncio.run(run_test())
    
    def test_place_bet_invalid_amount(self):
        """Test bet placement with invalid bet amount"""
        async def run_test():
            # Test amount too high
            success, message, bet_id = await self.game_engine.place_bet(1, 3, 2000)
            
            self.assertFalse(success)
            self.assertEqual(message, "Invalid bet amount (1-1000)")
            self.assertIsNone(bet_id)
            
            # Test amount too low
            success, message, bet_id = await self.game_engine.place_bet(1, 3, 0)
            
            self.assertFalse(success)
            self.assertEqual(message, "Invalid bet amount (1-1000)")
            self.assertIsNone(bet_id)
        
        asyncio.run(run_test())
    
    @patch('random.SystemRandom.randint')
    def test_calculate_results_winning_bet(self, mock_randint):
        """Test result calculation with winning bet"""
        mock_randint.return_value = 3  # Fixed dice result
        
        async def run_test():
            # Place bet and finish betting
            success, _, bet_id = await self.game_engine.place_bet(1, 3, 100)
            self.assertTrue(success)
            
            # Get the round ID
            round_id = None
            for r in self.game_state.active_rounds.values():
                if r.user_id == 1:
                    round_id = r.round_id
                    break
            
            self.assertIsNotNone(round_id)
            
            success, _ = await self.game_engine.finish_betting(1, round_id)
            self.assertTrue(success)
            
            # Calculate results
            success, message, results = await self.game_engine.calculate_results(1, round_id)
            
            self.assertTrue(success)
            self.assertEqual(results['dice_result'], 3)
            self.assertEqual(results['total_winnings'], 600)  # 100 * 6
            self.assertEqual(results['new_balance'], 1500)  # 1000 - 100 + 600
        
        asyncio.run(run_test())
    
    def test_get_user_snapshot(self):
        """Test getting user snapshot"""
        async def run_test():
            # Place a bet first
            await self.game_engine.place_bet(1, 3, 100)
            
            snapshot = await self.game_engine.get_user_snapshot(1)
            
            self.assertIsNotNone(snapshot)
            self.assertEqual(snapshot['user_balance'], 900)
            self.assertEqual(len(snapshot['active_bets']), 1)
            self.assertEqual(snapshot['current_room'], 1)
            self.assertEqual(snapshot['round_status'], GameRoundStatus.BETTING_PHASE.value)
        
        asyncio.run(run_test())


class TestGameState(unittest.TestCase):
    """Test GameState functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game_state = GameState()
    
    def test_user_authentication(self):
        """Test user authentication"""
        async def run_test():
            # Test authentication with default user
            user = await self.game_state.authenticate_user("testuser1", "password123")
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "testuser1")
            self.assertIsNotNone(user.session_token)
            
            # Test invalid credentials
            user = await self.game_state.authenticate_user("testuser1", "wrongpassword")
            self.assertIsNone(user)
        
        asyncio.run(run_test())
    
    def test_room_management(self):
        """Test room join/leave functionality"""
        async def run_test():
            # Create a test user
            user = User.create_user(100, "testuser", "password123")
            self.game_state.users[100] = user
            
            # Join room
            success = await self.game_state.join_room(100, 1)
            self.assertTrue(success)
            self.assertEqual(user.current_room, 1)
            
            room = await self.game_state.get_room(1)
            self.assertIn(100, room.current_players)
            
            # Leave room
            await self.game_state.leave_room(100)
            self.assertIsNone(user.current_room)
            self.assertNotIn(100, room.current_players)
        
        asyncio.run(run_test())


class TestProtocolBuffers(unittest.TestCase):
    """Test Protocol Buffers serialization/deserialization"""
    
    def test_login_request_serialization(self):
        """Test LoginRequest message serialization"""
        request = pb.LoginRequest()
        request.username = "testuser"
        request.password = "testpass"
        
        # Serialize and deserialize
        data = request.SerializeToString()
        request2 = pb.LoginRequest()
        request2.ParseFromString(data)
        
        self.assertEqual(request2.username, "testuser")
        self.assertEqual(request2.password, "testpass")
    
    def test_bet_placement_request(self):
        """Test BetPlacementRequest message"""
        request = pb.BetPlacementRequest()
        request.dice_face = 3
        request.amount = 100
        request.round_id = "test-round-123"
        
        data = request.SerializeToString()
        request2 = pb.BetPlacementRequest()
        request2.ParseFromString(data)
        
        self.assertEqual(request2.dice_face, 3)
        self.assertEqual(request2.amount, 100)
        self.assertEqual(request2.round_id, "test-round-123")
    
    def test_reckon_result_response(self):
        """Test ReckonResultResponse message with bet results"""
        response = pb.ReckonResultResponse()
        response.dice_result = 4
        response.total_winnings = 300
        response.new_balance = 1300
        response.updated_jackpot_pool = 50
        response.round_id = "test-round-456"
        
        # Add bet results
        bet_result = response.bet_results.add()
        bet_result.bet_id = "bet-123"
        bet_result.dice_face = 4
        bet_result.bet_amount = 50
        bet_result.won = True
        bet_result.payout = 300
        bet_result.round_id = "test-round-456"
        
        data = response.SerializeToString()
        response2 = pb.ReckonResultResponse()
        response2.ParseFromString(data)
        
        self.assertEqual(response2.dice_result, 4)
        self.assertEqual(response2.total_winnings, 300)
        self.assertEqual(len(response2.bet_results), 1)
        self.assertTrue(response2.bet_results[0].won)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.server = None
        self.server_task = None
        self.port = 8766  # Use different port for testing
    
    def tearDown(self):
        """Clean up after integration tests"""
        if self.server_task:
            self.server_task.cancel()
    
    def test_client_server_communication(self):
        """Test basic client-server communication"""
        async def run_test():
            # Start server
            server = GameServer('localhost', self.port, 10)
            server_task = asyncio.create_task(server.start_server())
            
            try:
                # Wait a bit for server to start
                await asyncio.sleep(0.5)
                
                # Create and connect client
                client = GameClient(f"ws://localhost:{self.port}")
                
                if await client.connect():
                    # Test login
                    login_success = await client.login("testuser1", "password123")
                    self.assertTrue(login_success)
                    
                    # Test joining room
                    room_success = await client.join_room(1)
                    self.assertTrue(room_success)
                    
                    # Test getting snapshot
                    snapshot = await client.get_snapshot()
                    self.assertIsNotNone(snapshot)
                    self.assertEqual(snapshot['user_balance'], 1000)
                    
                    await client.disconnect()
                else:
                    self.fail("Failed to connect to server")
                    
            finally:
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass
        
        # Run the async test
        asyncio.run(run_test())
    
    def test_complete_game_flow(self):
        """Test a complete game flow from login to results"""
        async def run_test():
            # Start server
            server = GameServer('localhost', self.port, 10)
            server_task = asyncio.create_task(server.start_server())
            
            try:
                # Wait for server to start
                await asyncio.sleep(0.5)
                
                # Create client and play a game
                client = GameClient(f"ws://localhost:{self.port}")
                
                if await client.connect():
                    # Login and join room
                    await client.login("testuser1", "password123")
                    await client.join_room(1)
                    
                    # Play a complete game session
                    bets = [(3, 100), (6, 50)]
                    results = await client.play_game_session(bets)
                    
                    # Verify results
                    self.assertIsNotNone(results)
                    self.assertIn('dice_result', results)
                    self.assertIn('total_winnings', results)
                    self.assertIn('new_balance', results)
                    self.assertEqual(len(results['bet_results']), 2)
                    
                    # Verify dice result is in valid range
                    self.assertTrue(1 <= results['dice_result'] <= 6)
                    
                    await client.disconnect()
                else:
                    self.fail("Failed to connect to server")
                    
            finally:
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass
        
        asyncio.run(run_test())


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game_state = GameState()
        self.game_engine = GameEngine(self.game_state)
    
    def test_invalid_user_operations(self):
        """Test operations with invalid user IDs"""
        async def run_test():
            # Try to place bet with non-existent user
            success, message, bet_id = await self.game_engine.place_bet(999, 3, 100)
            self.assertFalse(success)
            self.assertEqual(message, "User not found")
            
            # Try to get snapshot for non-existent user
            snapshot = await self.game_engine.get_user_snapshot(999)
            self.assertIsNone(snapshot)
        
        asyncio.run(run_test())
    
    def test_bet_validation_errors(self):
        """Test bet validation error scenarios"""
        async def run_test():
            # Create test user
            user = User.create_user(1, "testuser", "password123", 100)
            self.game_state.users[1] = user
            user.current_room = 1
            
            # Test invalid dice face
            success, message, _ = await self.game_engine.place_bet(1, 0, 50)
            self.assertFalse(success)
            self.assertIn("Invalid dice face", message)
            
            # Test invalid bet amount (too low)
            success, message, _ = await self.game_engine.place_bet(1, 3, 0)
            self.assertFalse(success)
            self.assertIn("Invalid bet amount", message)
            
            # Test invalid bet amount (too high)
            success, message, _ = await self.game_engine.place_bet(1, 3, 1001)
            self.assertFalse(success)
            self.assertIn("Invalid bet amount", message)
            
            # Test insufficient balance
            success, message, _ = await self.game_engine.place_bet(1, 3, 150)
            self.assertFalse(success)
            self.assertEqual(message, "Insufficient balance")
        
        asyncio.run(run_test())


class TestConcurrency(unittest.TestCase):
    """Test concurrent operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game_state = GameState()
        self.game_engine = GameEngine(self.game_state)
    
    def test_concurrent_bet_placement(self):
        """Test placing bets concurrently"""
        async def run_test():
            # Create test users
            for i in range(5):
                user = User.create_user(i + 1, f"user{i+1}", "password123", 1000)
                self.game_state.users[i + 1] = user
                user.current_room = 1
            
            # Place bets concurrently
            tasks = []
            for i in range(5):
                task = self.game_engine.place_bet(i + 1, 3, 100)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # All bets should succeed
            for success, message, bet_id in results:
                self.assertTrue(success, f"Bet failed: {message}")
                self.assertIsNotNone(bet_id)
        
        asyncio.run(run_test())


def run_all_tests():
    """Run all test suites"""
    test_suites = [
        TestUser,
        TestRoom, 
        TestGameRound,
        TestGameEngine,
        TestGameState,
        TestProtocolBuffers,
        TestErrorHandling,
        TestConcurrency,
        TestIntegration  # Run integration tests last
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_suites:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running comprehensive test suite for gaming system...")
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)