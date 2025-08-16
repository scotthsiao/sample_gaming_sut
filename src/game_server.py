import asyncio
import websockets
import struct
import logging
import signal
import sys
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
        logging.FileHandler('game_server.log'),
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
ERROR_INSUFFICIENT_BALANCE = 1002
ERROR_INVALID_ROOM = 1003
ERROR_INVALID_BET = 1004
ERROR_SERVER_ERROR = 1005
ERROR_RATE_LIMIT = 1006


class GameServer:
    def __init__(self, host='localhost', port=8765, max_connections=100):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.game_state = GameState()
        self.game_engine = GameEngine(self.game_state)
        self.running = False
        self.cleanup_task = None
        
        # Rate limiting: user_id -> (last_message_time, message_count)
        self.rate_limits: Dict[int, tuple] = {}
        
        self.command_handlers = {
            C2S_LOGIN_REQ: self.handle_login_request,
            C2S_ROOM_JOIN_REQ: self.handle_room_join_request,
            C2S_SNAPSHOT_REQ: self.handle_snapshot_request,
            C2S_BET_PLACEMENT_REQ: self.handle_bet_placement_request,
            C2S_BET_FINISHED_REQ: self.handle_bet_finished_request,
            C2S_RECKON_RESULT_REQ: self.handle_reckon_result_request,
        }

    async def start_server(self):
        """Start the WebSocket server"""
        self.running = True
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self.periodic_cleanup())
        
        logger.info(f"Starting game server on {self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            max_size=1024*1024,  # 1MB max message size
            ping_interval=20,
            ping_timeout=10
        ):
            logger.info("Game server started successfully")
            
            # Wait for shutdown signal
            await self.wait_for_shutdown()

    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shutdown the server"""
        logger.info("Shutting down game server...")
        self.running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Game server shutdown complete")

    async def handle_client(self, websocket):
        """Handle a WebSocket client connection"""
        client_addr = websocket.remote_address
        logger.info(f"New client connected: {client_addr}")
        
        try:
            # Add connection to game state
            await self.game_state.add_connection(websocket, 0)  # Will be updated on login
            
            async for message in websocket:
                if isinstance(message, bytes):
                    await self.process_message(websocket, message)
                else:
                    logger.warning(f"Received non-binary message from {client_addr}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_addr} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            await self.game_state.remove_connection(websocket)

    async def process_message(self, websocket, raw_data: bytes):
        """Process incoming binary message"""
        try:
            # Parse packet header
            if len(raw_data) < 8:
                await self.send_error(websocket, ERROR_INVALID_FORMAT, "Invalid packet size")
                return
            
            command_id, length = struct.unpack('<II', raw_data[:8])
            
            if len(raw_data) != 8 + length:
                await self.send_error(websocket, ERROR_INVALID_FORMAT, "Packet length mismatch")
                return
            
            payload = raw_data[8:]
            
            # Check rate limiting for authenticated users
            user = await self.game_state.get_user_by_connection(websocket)
            if user and not await self.check_rate_limit(user.user_id):
                await self.send_error(websocket, ERROR_RATE_LIMIT, "Rate limit exceeded")
                return
            
            # Route to appropriate handler
            if command_id in self.command_handlers:
                await self.command_handlers[command_id](websocket, payload)
            else:
                await self.send_error(websocket, ERROR_INVALID_FORMAT, f"Unknown command: {command_id:04x}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error(websocket, ERROR_SERVER_ERROR, f"Server error: {str(e)}")

    async def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits (100 messages per minute)"""
        current_time = datetime.now()
        
        if user_id in self.rate_limits:
            last_time, count = self.rate_limits[user_id]
            if (current_time - last_time).total_seconds() < 60:
                if count >= 100:
                    return False
                self.rate_limits[user_id] = (last_time, count + 1)
            else:
                self.rate_limits[user_id] = (current_time, 1)
        else:
            self.rate_limits[user_id] = (current_time, 1)
        
        return True

    async def handle_login_request(self, websocket, payload: bytes):
        """Handle user login request"""
        try:
            request = pb.LoginRequest()
            request.ParseFromString(payload)
            
            # Validate credentials
            user = await self.game_state.authenticate_user(request.username, request.password)
            
            response = pb.LoginResponse()
            if user:
                response.success = True
                response.message = "Login successful"
                response.session_token = user.session_token
                response.user_id = user.user_id
                response.balance = user.balance
                
                # Update connection mapping
                await self.game_state.add_connection(websocket, user.user_id)
                
                logger.info(f"User {user.username} logged in successfully")
            else:
                response.success = False
                response.message = "Invalid credentials or user already logged in"
                logger.warning(f"Failed login attempt for username: {request.username}")
            
            await self.send_response(websocket, S2C_LOGIN_RSP, response)
            
        except DecodeError:
            await self.send_error(websocket, ERROR_INVALID_FORMAT, "Invalid message format")
        except Exception as e:
            logger.error(f"Error in login handler: {e}")
            await self.send_error(websocket, ERROR_SERVER_ERROR, "Login failed")

    async def handle_room_join_request(self, websocket, payload: bytes):
        """Handle room join request"""
        try:
            user = await self.game_state.get_user_by_connection(websocket)
            if not user:
                await self.send_error(websocket, ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            request = pb.RoomJoinRequest()
            request.ParseFromString(payload)
            
            success = await self.game_state.join_room(user.user_id, request.room_id)
            
            response = pb.RoomJoinResponse()
            if success:
                room = await self.game_state.get_room(request.room_id)
                response.success = True
                response.message = "Joined room successfully"
                response.room_id = request.room_id
                response.player_count = room.get_player_count() if room else 0
                response.jackpot_pool = room.jackpot_pool if room else 0
                
                logger.info(f"User {user.username} joined room {request.room_id}")
            else:
                response.success = False
                response.message = "Failed to join room (room full or invalid)"
            
            await self.send_response(websocket, S2C_ROOM_JOIN_RSP, response)
            
        except DecodeError:
            await self.send_error(websocket, ERROR_INVALID_FORMAT, "Invalid message format")
        except Exception as e:
            logger.error(f"Error in room join handler: {e}")
            await self.send_error(websocket, ERROR_SERVER_ERROR, "Room join failed")

    async def handle_snapshot_request(self, websocket, payload: bytes):
        """Handle game state snapshot request"""
        try:
            user = await self.game_state.get_user_by_connection(websocket)
            if not user:
                await self.send_error(websocket, ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            snapshot = await self.game_engine.get_user_snapshot(user.user_id)
            if not snapshot:
                await self.send_error(websocket, ERROR_SERVER_ERROR, "Failed to get snapshot")
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
            
            await self.send_response(websocket, S2C_SNAPSHOT_RSP, response)
            
        except Exception as e:
            logger.error(f"Error in snapshot handler: {e}")
            await self.send_error(websocket, ERROR_SERVER_ERROR, "Snapshot failed")

    async def handle_bet_placement_request(self, websocket, payload: bytes):
        """Handle bet placement request"""
        try:
            user = await self.game_state.get_user_by_connection(websocket)
            if not user:
                await self.send_error(websocket, ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            request = pb.BetPlacementRequest()
            request.ParseFromString(payload)
            
            success, message, bet_id = await self.game_engine.place_bet(
                user.user_id, request.dice_face, request.amount, request.round_id or None
            )
            
            response = pb.BetPlacementResponse()
            response.success = success
            response.message = message
            response.remaining_balance = user.balance
            
            if success and bet_id:
                response.bet_id = bet_id
                # Get the round ID from the bet
                if request.round_id:
                    response.round_id = request.round_id
                else:
                    # Find the active round for this user
                    for round_obj in self.game_state.active_rounds.values():
                        if round_obj.user_id == user.user_id:
                            response.round_id = round_obj.round_id
                            break
            
            await self.send_response(websocket, S2C_BET_PLACEMENT_RSP, response)
            
        except DecodeError:
            await self.send_error(websocket, ERROR_INVALID_FORMAT, "Invalid message format")
        except Exception as e:
            logger.error(f"Error in bet placement handler: {e}")
            await self.send_error(websocket, ERROR_SERVER_ERROR, "Bet placement failed")

    async def handle_bet_finished_request(self, websocket, payload: bytes):
        """Handle bet finished request"""
        try:
            user = await self.game_state.get_user_by_connection(websocket)
            if not user:
                await self.send_error(websocket, ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            request = pb.BetFinishedRequest()
            request.ParseFromString(payload)
            
            success, message = await self.game_engine.finish_betting(user.user_id, request.round_id)
            
            response = pb.BetFinishedResponse()
            response.success = success
            response.message = message
            response.round_id = request.round_id
            
            await self.send_response(websocket, S2C_BET_FINISHED_RSP, response)
            
        except DecodeError:
            await self.send_error(websocket, ERROR_INVALID_FORMAT, "Invalid message format")
        except Exception as e:
            logger.error(f"Error in bet finished handler: {e}")
            await self.send_error(websocket, ERROR_SERVER_ERROR, "Bet finished failed")

    async def handle_reckon_result_request(self, websocket, payload: bytes):
        """Handle result calculation request"""
        try:
            user = await self.game_state.get_user_by_connection(websocket)
            if not user:
                await self.send_error(websocket, ERROR_AUTH_REQUIRED, "Authentication required")
                return
            
            request = pb.ReckonResultRequest()
            request.ParseFromString(payload)
            
            success, message, results = await self.game_engine.calculate_results(user.user_id, request.round_id)
            
            if not success:
                await self.send_error(websocket, ERROR_INVALID_BET, message)
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
            
            await self.send_response(websocket, S2C_RECKON_RESULT_RSP, response)
            
        except DecodeError:
            await self.send_error(websocket, ERROR_INVALID_FORMAT, "Invalid message format")
        except Exception as e:
            logger.error(f"Error in result calculation handler: {e}")
            await self.send_error(websocket, ERROR_SERVER_ERROR, "Result calculation failed")

    async def send_response(self, websocket, command_id: int, message):
        """Send a Protocol Buffers response message"""
        try:
            payload = message.SerializeToString()
            header = struct.pack('<II', command_id, len(payload))
            await websocket.send(header + payload)
        except Exception as e:
            logger.error(f"Error sending response: {e}")

    async def send_error(self, websocket, error_code: int, error_message: str):
        """Send an error response"""
        try:
            error = pb.ErrorResponse()
            error.error_code = error_code
            error.error_message = error_message
            error.details = ""
            await self.send_response(websocket, S2C_ERROR_RSP, error)
        except Exception as e:
            logger.error(f"Error sending error response: {e}")

    async def periodic_cleanup(self):
        """Periodic cleanup task"""
        while self.running:
            try:
                # Clean up expired sessions
                await self.game_state.cleanup_expired_sessions()
                
                # Clean up stale rounds
                await self.game_engine.cleanup_stale_rounds()
                
                # Clean up rate limits (remove old entries)
                current_time = datetime.now()
                expired_users = [
                    user_id for user_id, (last_time, _) in self.rate_limits.items()
                    if (current_time - last_time).total_seconds() > 3600  # 1 hour
                ]
                for user_id in expired_users:
                    del self.rate_limits[user_id]
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying


def setup_signal_handlers(server):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        asyncio.create_task(server.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main server entry point"""
    parser = argparse.ArgumentParser(description='Game Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8765, help='Server port')
    parser.add_argument('--max-connections', type=int, default=100, help='Maximum connections')
    
    args = parser.parse_args()
    
    server = GameServer(args.host, args.port, args.max_connections)
    setup_signal_handlers(server)
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())