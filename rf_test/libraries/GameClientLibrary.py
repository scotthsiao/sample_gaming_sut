import struct
import uuid
import time
from typing import Dict, Any, Optional, Tuple
from robot.api.deco import keyword, library
from robot.api import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.protocol_client import ProtocolClient

# Import Protocol Buffers messages
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from proto import game_messages_pb2 as pb
except ImportError:
    logger.error("Failed to import Protocol Buffers. Make sure game_messages_pb2.py is generated.")
    raise


# Command IDs as defined in the functional specification
class Commands:
    # Client to Server
    C2S_LOGIN_REQ = 0x0001
    C2S_ROOM_JOIN_REQ = 0x0002
    C2S_SNAPSHOT_REQ = 0x0003
    C2S_BET_PLACEMENT_REQ = 0x0004
    C2S_BET_FINISHED_REQ = 0x0005
    C2S_RECKON_RESULT_REQ = 0x0006
    
    # Server to Client
    S2C_LOGIN_RSP = 0x1001
    S2C_ROOM_JOIN_RSP = 0x1002
    S2C_SNAPSHOT_RSP = 0x1003
    S2C_BET_PLACEMENT_RSP = 0x1004
    S2C_BET_FINISHED_RSP = 0x1005
    S2C_RECKON_RESULT_RSP = 0x1006
    S2C_ERROR_RSP = 0x9999


@library
class GameClientLibrary:
    """Robot Framework library for testing the dice gambling game system."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        self.client = ProtocolClient()
        self.session_token = None
        self.user_id = None
        self.current_room = None
        self.user_balance = 0
        self.active_round_id = None
        
    @keyword
    def connect_to_game_server(self, server_url: str, timeout: int = 10) -> bool:
        """Establish WebSocket connection to the dice gambling game server."""
        logger.info(f"Connecting to game server: {server_url}")
        success = self.client.connect(server_url, timeout)
        if success:
            logger.info("Successfully connected to game server")
            return success
        else:
            error_msg = f"Connection failed to server: {server_url}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    @keyword
    def disconnect_from_server(self) -> bool:
        """Close WebSocket connection."""
        logger.info("Disconnecting from game server")
        self.client.disconnect()
        self._clear_session_data()
        return True
    
    @keyword
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user with the game server using Protocol Buffers."""
        logger.info(f"Logging in user: {username}")
        
        # Create Protocol Buffers login request
        login_request = pb.LoginRequest()
        login_request.username = username
        login_request.password = password
        payload = login_request.SerializeToString()
        
        if not self.client.send_packet(Commands.C2S_LOGIN_REQ, payload):
            raise Exception("Failed to send login request")
        
        # Wait for response
        response = self.client.wait_for_packet(timeout=10)
        if not response:
            raise Exception("No response received for login")
        
        command_id, response_payload = response
        
        if command_id == Commands.S2C_LOGIN_RSP:
            # Parse Protocol Buffers login response
            try:
                login_response = pb.LoginResponse()
                login_response.ParseFromString(response_payload)
                
                if login_response.success:
                    self.user_id = login_response.user_id
                    self.user_balance = login_response.balance
                    self.session_token = login_response.session_token
                    
                    logger.info(f"Login successful for user: {username}")
                    return {
                        'status': 'success',
                        'user_id': self.user_id,
                        'balance': self.user_balance,
                        'session_token': self.session_token
                    }
                else:
                    error_msg = f"Login failed: {login_response.message}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Failed to parse login response: {e}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        elif command_id == Commands.S2C_ERROR_RSP:
            # Parse error response
            try:
                error_response = pb.ErrorResponse()
                error_response.ParseFromString(response_payload)
                error_msg = f"Login failed with error code: {error_response.error_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
            except:
                # Fallback to original parsing if protobuf fails
                error_code = struct.unpack('<I', response_payload[:4])[0] if len(response_payload) >= 4 else 0
                error_msg = f"Login failed with error code: {error_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            raise Exception(f"Unexpected response command: {command_id:#x}")
    
    @keyword
    def join_game_room(self, room_id: int = 1) -> Dict[str, Any]:
        """Join a game room."""
        if not self.session_token:
            raise Exception("User must be logged in to join room")
        
        logger.info(f"Joining game room: {room_id}")
        
        # Create Protocol Buffers room join request
        room_request = pb.RoomJoinRequest()
        room_request.room_id = room_id
        payload = room_request.SerializeToString()
        
        if not self.client.send_packet(Commands.C2S_ROOM_JOIN_REQ, payload):
            raise Exception("Failed to send room join request")
        
        response = self.client.wait_for_packet(timeout=10)
        if not response:
            raise Exception("No response received for room join")
        
        command_id, response_payload = response
        
        if command_id == Commands.S2C_ROOM_JOIN_RSP:
            try:
                room_response = pb.RoomJoinResponse()
                room_response.ParseFromString(response_payload)
                
                if room_response.success:
                    self.current_room = room_id
                    
                    logger.info(f"Successfully joined room: {room_id}")
                    return {
                        'status': 'success',
                        'room_id': room_response.room_id,
                        'player_count': room_response.player_count,
                        'jackpot_pool': room_response.jackpot_pool
                    }
                else:
                    error_msg = f"Failed to join room: {room_response.message}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Failed to parse room join response: {e}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            raise Exception(f"Unexpected response command: {command_id:#x}")
    
    @keyword
    def get_game_snapshot(self) -> Dict[str, Any]:
        """Retrieve current game state snapshot."""
        if not self.session_token:
            raise Exception("User must be logged in")
        
        logger.info("Requesting game snapshot")
        
        # Create Protocol Buffers snapshot request (empty message)
        snapshot_request = pb.SnapshotRequest()
        payload = snapshot_request.SerializeToString()
        
        if not self.client.send_packet(Commands.C2S_SNAPSHOT_REQ, payload):
            raise Exception("Failed to send snapshot request")
        
        response = self.client.wait_for_packet(timeout=10)
        if not response:
            raise Exception("No response received for snapshot")
        
        command_id, response_payload = response
        
        if command_id == Commands.S2C_SNAPSHOT_RSP:
            try:
                snapshot_response = pb.SnapshotResponse()
                snapshot_response.ParseFromString(response_payload)
                
                self.user_balance = snapshot_response.user_balance
                
                logger.info("Game snapshot received successfully")
                return {
                    'user_balance': snapshot_response.user_balance,
                    'current_room': snapshot_response.current_room,
                    'jackpot_pool': snapshot_response.jackpot_pool,
                    'round_status': snapshot_response.round_status
                }
            except Exception as e:
                error_msg = f"Failed to parse snapshot response: {e}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            raise Exception(f"Unexpected response command: {command_id:#x}")
    
    @keyword
    def place_bet(self, dice_face: int, amount: int, round_id: str = None) -> Dict[str, Any]:
        """Place a bet on dice outcome."""
        if not self.session_token or not self.current_room:
            raise Exception("User must be logged in and in a room")
        
        if not (1 <= dice_face <= 6):
            raise Exception("Dice face must be between 1 and 6")
        
        if not (1 <= amount <= 1000):
            raise Exception("Bet amount must be between 1 and 1000")
        
        if amount > self.user_balance:
            raise Exception("Insufficient balance for bet")
        
        # Store round_id if provided for subsequent bets
        if round_id:
            self.active_round_id = round_id
        
        logger.info(f"Placing bet: {amount} on dice face {dice_face}")
        
        # Create Protocol Buffers bet placement request
        bet_request = pb.BetPlacementRequest()
        bet_request.dice_face = dice_face
        bet_request.amount = amount
        if round_id:
            bet_request.round_id = round_id
        payload = bet_request.SerializeToString()
        
        if not self.client.send_packet(Commands.C2S_BET_PLACEMENT_REQ, payload):
            raise Exception("Failed to send bet placement request")
        
        response = self.client.wait_for_packet(timeout=10)
        if not response:
            raise Exception("No response received for bet placement")
        
        command_id, response_payload = response
        
        if command_id == Commands.S2C_BET_PLACEMENT_RSP:
            try:
                bet_response = pb.BetPlacementResponse()
                bet_response.ParseFromString(response_payload)
                
                if bet_response.success:
                    self.user_balance = bet_response.remaining_balance
                    # Store the round_id returned by server for subsequent operations
                    if bet_response.round_id:
                        self.active_round_id = bet_response.round_id
                    
                    logger.info(f"Bet placed successfully: {bet_response.bet_id}")
                    return {
                        'status': 'success',
                        'bet_id': bet_response.bet_id,
                        'dice_face': dice_face,
                        'amount': amount,
                        'remaining_balance': bet_response.remaining_balance,
                        'round_id': bet_response.round_id if bet_response.round_id else self.active_round_id
                    }
                else:
                    error_msg = f"Failed to place bet: {bet_response.message}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Failed to parse bet placement response: {e}"
                logger.error(error_msg)
                raise Exception(error_msg)
        elif command_id == Commands.S2C_ERROR_RSP:
            # Parse error response
            try:
                error_response = pb.ErrorResponse()
                error_response.ParseFromString(response_payload)
                error_msg = f"Bet placement failed with error code: {error_response.error_code}, message: {error_response.error_message}"
                logger.error(error_msg)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Failed to parse error response: {e}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            raise Exception(f"Unexpected response command: {command_id:#x}")
    
    @keyword
    def finish_betting(self, round_id: str = None) -> Dict[str, Any]:
        """Signal that betting is finished for the round."""
        if not round_id:
            round_id = self.active_round_id
        
        if not round_id:
            raise Exception("No active round to finish")
        
        logger.info(f"Finishing betting for round: {round_id}")
        
        # Create Protocol Buffers bet finished request
        bet_finished_request = pb.BetFinishedRequest()
        bet_finished_request.round_id = round_id
        payload = bet_finished_request.SerializeToString()
        
        if not self.client.send_packet(Commands.C2S_BET_FINISHED_REQ, payload):
            raise Exception("Failed to send bet finished request")
        
        response = self.client.wait_for_packet(timeout=10)
        if not response:
            raise Exception("No response received for bet finished")
        
        command_id, response_payload = response
        
        if command_id == Commands.S2C_BET_FINISHED_RSP:
            try:
                bet_finished_response = pb.BetFinishedResponse()
                bet_finished_response.ParseFromString(response_payload)
                
                if bet_finished_response.success:
                    logger.info("Betting finished successfully")
                    return {'status': 'success', 'round_id': round_id}
                else:
                    error_msg = f"Failed to finish betting: {bet_finished_response.message}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Failed to parse bet finished response: {e}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            raise Exception(f"Unexpected response command: {command_id:#x}")
    
    @keyword
    def get_game_result(self, round_id: str = None) -> Dict[str, Any]:
        """Get the game result for a round."""
        if not round_id:
            round_id = self.active_round_id
        
        if not round_id:
            raise Exception("No active round to get result for")
        
        logger.info(f"Getting game result for round: {round_id}")
        
        # Create Protocol Buffers result request
        result_request = pb.ReckonResultRequest()
        result_request.round_id = round_id
        payload = result_request.SerializeToString()
        
        if not self.client.send_packet(Commands.C2S_RECKON_RESULT_REQ, payload):
            raise Exception("Failed to send result request")
        
        response = self.client.wait_for_packet(timeout=10)
        if not response:
            raise Exception("No response received for game result")
        
        command_id, response_payload = response
        
        if command_id == Commands.S2C_RECKON_RESULT_RSP:
            try:
                result_response = pb.ReckonResultResponse()
                result_response.ParseFromString(response_payload)
                
                self.user_balance = result_response.new_balance
                
                logger.info(f"Game result: dice={result_response.dice_result}, winnings={result_response.total_winnings}")
                return {
                    'dice_result': result_response.dice_result,
                    'total_winnings': result_response.total_winnings,
                    'new_balance': result_response.new_balance,
                    'updated_jackpot': result_response.updated_jackpot_pool,
                    'round_id': round_id
                }
            except Exception as e:
                error_msg = f"Failed to parse game result response: {e}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            raise Exception(f"Unexpected response command: {command_id:#x}")
    
    @keyword
    def get_connection_status(self) -> bool:
        """Check if connection is active."""
        return self.client.connected
    
    @keyword
    def get_user_balance(self) -> int:
        """Get current user balance."""
        return self.user_balance
    
    @keyword
    def get_current_room(self) -> Optional[int]:
        """Get current room ID."""
        return self.current_room
    
    @keyword
    def get_session_token(self) -> Optional[str]:
        """Get current session token."""
        return self.session_token
    
    def _clear_session_data(self):
        """Clear all session-related data."""
        self.session_token = None
        self.user_id = None
        self.current_room = None
        self.user_balance = 0
        self.active_round_id = None