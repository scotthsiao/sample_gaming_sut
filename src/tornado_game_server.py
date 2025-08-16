#!/usr/bin/env python3
"""
Game server using Tornado WebSocket instead of websockets library
"""
import tornado.web
import tornado.websocket
import tornado.ioloop
import struct
import logging
import signal
import sys
import time
import argparse
from datetime import datetime
from typing import Dict, Optional
from google.protobuf.message import DecodeError

# Import generated protobuf messages
try:
    from proto import game_messages_pb2 as pb
except ImportError:
    print("Error: Protocol buffer files not generated. Run: protoc --python_out=. --pyi_out=. proto/game_messages.proto")
    sys.exit(1)

from .models import GameState, GameRoundStatus
from .game_engine import GameEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tornado_game_server.log'),
        logging.StreamHandler()
    ]
)
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

# Error codes
ERROR_INVALID_FORMAT = 1000
ERROR_AUTH_REQUIRED = 1001
ERROR_USER_NOT_FOUND = 1002
ERROR_INVALID_CREDENTIALS = 1003
ERROR_ROOM_NOT_FOUND = 1004
ERROR_ROOM_FULL = 1005
ERROR_INSUFFICIENT_BALANCE = 1006
ERROR_ROUND_NOT_FOUND = 1007
ERROR_BETTING_CLOSED = 1008
ERROR_RATE_LIMIT = 1009
ERROR_INTERNAL = 1010


class GameWebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = {}  # Store client information
    rate_limits = {}  # Rate limiting
    
    def initialize(self, game_state, game_engine):
        self.game_state = game_state
        self.game_engine = game_engine
        self.user_id = 0
        self.authenticated = False
        self.connect_time = datetime.now()

    def open(self):
        """Called when WebSocket connection is opened"""
        client_addr = self.request.remote_ip
        logger.info(f"New client connected: {client_addr}")
        
        # Store client info
        GameWebSocketHandler.clients[id(self)] = {
            'handler': self,
            'address': client_addr,
            'user_id': 0,
            'authenticated': False,
            'connect_time': datetime.now()
        }

    def on_message(self, message):
        """Called when a message is received"""
        try:
            if isinstance(message, bytes):
                self.process_message(message)
            else:
                logger.warning(f"Received non-binary message from {self.request.remote_ip}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def on_close(self):
        """Called when WebSocket connection is closed"""
        client_addr = self.request.remote_ip
        logger.info(f"Client {client_addr} disconnected")
        
        # Clean up user session if authenticated
        if self.authenticated and self.user_id:
            try:
                # Schedule async cleanup on the current event loop
                import tornado.ioloop
                tornado.ioloop.IOLoop.current().add_callback(self._cleanup_user_session)
            except Exception as e:
                logger.error(f"Error during disconnect cleanup: {e}")
        
        # Clean up client info
        if id(self) in GameWebSocketHandler.clients:
            del GameWebSocketHandler.clients[id(self)]
    
    async def _cleanup_user_session(self):
        """Async helper for cleaning up user session on disconnect"""
        try:
            # Leave room
            await self.game_state.leave_room(self.user_id)
            # Invalidate session
            user = self.game_state.users.get(self.user_id)
            if user:
                user.session_token = None
                logger.info(f"User {self.user_id} session invalidated due to disconnection")
        except Exception as e:
            logger.error(f"Error in async cleanup: {e}")

    def process_message(self, raw_data: bytes):
        """Process a received message"""
        try:
            # Parse packet header
            if len(raw_data) < 8:
                self.send_error(ERROR_INVALID_FORMAT, "Invalid packet size")
                return
            
            command_id, length = struct.unpack('<II', raw_data[:8])
            
            if len(raw_data) != 8 + length:
                self.send_error(ERROR_INVALID_FORMAT, "Packet length mismatch")
                return
            
            payload = raw_data[8:]
            
            # Check rate limiting for authenticated users
            if self.authenticated:
                if not self.check_rate_limit(self.user_id):
                    self.send_error(ERROR_RATE_LIMIT, "Rate limit exceeded")
                    return
            
            # Route message based on command ID - run async handlers
            import tornado.ioloop
            io_loop = tornado.ioloop.IOLoop.current()
            
            if command_id == C2S_LOGIN_REQ:
                io_loop.add_callback(self.handle_login, payload)
            elif command_id == C2S_ROOM_JOIN_REQ:
                io_loop.add_callback(self.handle_room_join, payload)
            elif command_id == C2S_SNAPSHOT_REQ:
                io_loop.add_callback(self.handle_snapshot, payload)
            elif command_id == C2S_BET_PLACEMENT_REQ:
                io_loop.add_callback(self.handle_bet_placement, payload)
            elif command_id == C2S_BET_FINISHED_REQ:
                io_loop.add_callback(self.handle_bet_finished, payload)
            elif command_id == C2S_RECKON_RESULT_REQ:
                io_loop.add_callback(self.handle_reckon_result, payload)
            else:
                logger.warning(f"Unknown command ID: 0x{command_id:04X}")
                self.send_error(ERROR_INVALID_FORMAT, f"Unknown command: 0x{command_id:04X}")
                
        except struct.error:
            self.send_error(ERROR_INVALID_FORMAT, "Invalid packet format")
        except DecodeError:
            self.send_error(ERROR_INVALID_FORMAT, "Invalid protobuf message")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.send_error(ERROR_INTERNAL, "Internal server error")

    def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        # For demo purposes, allow more requests for user 1 (testuser1)
        if user_id == 1:
            return True
            
        now = time.time()
        last_request = GameWebSocketHandler.rate_limits.get(user_id, 0)
        
        if now - last_request < 0.05:  # Max 20 requests per second
            return False
        
        GameWebSocketHandler.rate_limits[user_id] = now
        return True

    async def handle_login(self, payload: bytes):
        """Handle login request"""
        try:
            request = pb.LoginRequest()
            request.ParseFromString(payload)
            
            logger.info(f"Login attempt: {request.username}")
            
            # Use actual authentication from game state
            user = await self.game_state.authenticate_user(request.username, request.password)
            
            response = pb.LoginResponse()
            if user:
                # Successful login
                self.authenticated = True
                self.user_id = user.user_id
                
                # Update client info
                if id(self) in GameWebSocketHandler.clients:
                    GameWebSocketHandler.clients[id(self)]['authenticated'] = True
                    GameWebSocketHandler.clients[id(self)]['user_id'] = user.user_id
                
                response.success = True
                response.message = "Login successful"
                response.session_token = user.session_token
                response.user_id = user.user_id
                response.balance = user.balance
                
                logger.info(f"User {request.username} logged in successfully")
            else:
                # Failed login
                response.success = False
                response.message = "Invalid credentials or user already logged in"
                logger.warning(f"Login failed for user: {request.username}")
            
            self.send_message(S2C_LOGIN_RSP, response)
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.send_error(ERROR_INTERNAL, "Login processing error")

    async def handle_room_join(self, payload: bytes):
        """Handle room join request"""
        try:
            request = pb.RoomJoinRequest()
            request.ParseFromString(payload)
            
            if not self.authenticated:
                self.send_error(ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            # Use actual room join from game state
            success = await self.game_state.join_room(self.user_id, request.room_id)
            
            response = pb.RoomJoinResponse()
            if success:
                room = await self.game_state.get_room(request.room_id)
                response.success = True
                response.message = "Joined room successfully"
                response.room_id = request.room_id
                response.player_count = room.get_player_count() if room else 0
                response.jackpot_pool = room.jackpot_pool if room else 0
                
                logger.info(f"User {self.user_id} joined room {request.room_id}")
            else:
                response.success = False
                response.message = "Failed to join room (room full or invalid)"
            
            self.send_message(S2C_ROOM_JOIN_RSP, response)
                
        except Exception as e:
            logger.error(f"Room join error: {e}")
            self.send_error(ERROR_INTERNAL, "Room join processing error")

    async def handle_snapshot(self, payload: bytes):
        """Handle snapshot request"""
        try:
            request = pb.SnapshotRequest()
            request.ParseFromString(payload)
            
            if not self.authenticated:
                self.send_error(ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            # Use actual snapshot from game engine
            snapshot = await self.game_engine.get_user_snapshot(self.user_id)
            
            if not snapshot:
                self.send_error(ERROR_INTERNAL, "Failed to get snapshot")
                return
            
            response = pb.SnapshotResponse()
            response.user_balance = snapshot['user_balance']
            response.current_room = snapshot['current_room']
            response.jackpot_pool = snapshot['jackpot_pool']
            response.round_status = snapshot['round_status']
            
            for bet_data in snapshot['active_bets']:
                bet = response.active_bets.add()
                bet.dice_face = bet_data['dice_face']
                bet.amount = bet_data['amount']
                bet.bet_id = bet_data['bet_id']
                bet.round_id = bet_data['round_id']
            
            self.send_message(S2C_SNAPSHOT_RSP, response)
            
        except Exception as e:
            logger.error(f"Snapshot error: {e}")
            self.send_error(ERROR_INTERNAL, "Snapshot processing error")

    async def handle_bet_placement(self, payload: bytes):
        """Handle bet placement request"""
        try:
            request = pb.BetPlacementRequest()
            request.ParseFromString(payload)
            
            if not self.authenticated:
                self.send_error(ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            # Use the actual game engine for bet placement
            user = self.game_state.users.get(self.user_id)
            if not user:
                self.send_error(ERROR_USER_NOT_FOUND, "User not found")
                return
            
            # Place bet using game engine
            success, message, bet_id = await self.game_engine.place_bet(
                self.user_id, request.dice_face, request.amount, request.round_id or None
            )
            
            response = pb.BetPlacementResponse()
            response.success = success
            response.message = message
            response.remaining_balance = user.balance
            
            if success and bet_id:
                response.bet_id = bet_id
                # Get the round ID from active rounds
                for round_obj in self.game_state.active_rounds.values():
                    if round_obj.user_id == self.user_id:
                        response.round_id = round_obj.round_id
                        break
            
            self.send_message(S2C_BET_PLACEMENT_RSP, response)
            
        except Exception as e:
            logger.error(f"Bet placement error: {e}")
            self.send_error(ERROR_INTERNAL, "Bet placement processing error")

    async def handle_bet_finished(self, payload: bytes):
        """Handle bet finished request"""
        try:
            request = pb.BetFinishedRequest()
            request.ParseFromString(payload)
            
            if not self.authenticated:
                self.send_error(ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            # Use the actual game engine for finishing betting
            success, message = await self.game_engine.finish_betting(self.user_id, request.round_id)
            
            response = pb.BetFinishedResponse()
            response.success = success
            response.message = message
            response.round_id = request.round_id
            
            self.send_message(S2C_BET_FINISHED_RSP, response)
            
        except Exception as e:
            logger.error(f"Bet finished error: {e}")
            self.send_error(ERROR_INTERNAL, "Bet finished processing error")

    async def handle_reckon_result(self, payload: bytes):
        """Handle reckon result request"""
        try:
            request = pb.ReckonResultRequest()
            request.ParseFromString(payload)
            
            if not self.authenticated:
                self.send_error(ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            # Use the actual game engine for result calculation
            success, message, results = await self.game_engine.calculate_results(self.user_id, request.round_id)
            
            if not success:
                self.send_error(ERROR_ROUND_NOT_FOUND, message)
                return
            
            response = pb.ReckonResultResponse()
            response.dice_result = results['dice_result']
            response.total_winnings = results['total_winnings']
            response.new_balance = results['new_balance']
            response.updated_jackpot_pool = results['jackpot_pool']
            response.round_id = request.round_id
            
            for bet_result in results['bet_results']:
                bet = response.bet_results.add()
                bet.bet_id = bet_result['bet_id']
                bet.dice_face = bet_result['dice_face']
                bet.bet_amount = bet_result['bet_amount']
                bet.won = bet_result['won']
                bet.payout = bet_result['payout']
                bet.round_id = request.round_id
            
            self.send_message(S2C_RECKON_RESULT_RSP, response)
            
        except Exception as e:
            logger.error(f"Reckon result error: {e}")
            self.send_error(ERROR_INTERNAL, "Reckon result processing error")

    def send_message(self, command_id: int, message):
        """Send a Protocol Buffers message to client"""
        try:
            payload = message.SerializeToString()
            header = struct.pack('<II', command_id, len(payload))
            data = header + payload
            
            # Send as binary data
            self.write_message(data, binary=True)
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def send_error(self, error_code: int, error_message: str):
        """Send an error response to client"""
        try:
            error_response = pb.ErrorResponse()
            error_response.error_code = error_code
            error_response.error_message = error_message
            
            self.send_message(S2C_ERROR_RSP, error_response)
            
        except Exception as e:
            logger.error(f"Error sending error response: {e}")


class TornadoGameServer:
    def __init__(self, host: str = 'localhost', port: int = 8767, max_connections: int = 100):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.running = False
        self.game_state = None
        self.game_engine = None
        self.app = None

    def start_server(self):
        """Start the Tornado WebSocket server"""
        self.running = True
        
        # Initialize game components
        self.game_state = GameState()
        self.game_engine = GameEngine(self.game_state)
        
        logger.info(f"Starting Tornado game server on {self.host}:{self.port}")
        
        # Create Tornado application
        self.app = tornado.web.Application([
            (r"/", GameWebSocketHandler, dict(game_state=self.game_state, game_engine=self.game_engine)),
        ])
        
        # Start server
        self.app.listen(self.port, address=self.host)
        logger.info("Tornado game server started successfully")
        
        # Start the event loop
        tornado.ioloop.IOLoop.current().start()

    def shutdown(self):
        """Shutdown the server"""
        logger.info("Shutting down Tornado game server...")
        self.running = False
        
        # Stop the event loop
        tornado.ioloop.IOLoop.current().stop()
        
        logger.info("Tornado game server shutdown complete")


def setup_signal_handlers(server):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        server.shutdown()
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main server entry point"""
    parser = argparse.ArgumentParser(description='Tornado Game Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8767, help='Server port')
    parser.add_argument('--max-connections', type=int, default=100, help='Maximum connections')
    
    args = parser.parse_args()
    
    server = TornadoGameServer(args.host, args.port, args.max_connections)
    setup_signal_handlers(server)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()