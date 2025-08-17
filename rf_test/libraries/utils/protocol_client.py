import struct
import logging
from typing import Optional, Dict, Any, Tuple
import websocket
import threading
import time


class ProtocolClient:
    """WebSocket client that handles Protocol Buffers message format with packet encapsulation."""
    
    def __init__(self):
        self.ws = None
        self.url = None
        self.connected = False
        self.message_queue = []
        self.response_callbacks = {}
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
    def connect(self, url: str, timeout: int = 10) -> bool:
        """Connect to the gaming server."""
        try:
            self.url = url
            self.ws = websocket.WebSocketApp(
                url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            self.connected = False
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()
            
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
                
            return self.connected
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server."""
        if self.ws:
            self.ws.close()
            self.connected = False
    
    def send_packet(self, command_id: int, payload: bytes) -> bool:
        """Send a packet with command ID, length, and payload."""
        if not self.connected:
            self.logger.error("Not connected to server")
            return False
        
        try:
            # Packet format: Command ID (4 bytes) + Length (4 bytes) + Payload
            length = len(payload)
            packet = struct.pack('<II', command_id, length) + payload
            
            self.ws.send(packet, opcode=websocket.ABNF.OPCODE_BINARY)
            self.logger.debug(f"Sent packet: command_id={command_id:#x}, length={length}")
            return True
        except Exception as e:
            self.logger.error(f"Send packet failed: {e}")
            return False
    
    def wait_for_packet(self, timeout: int = 5) -> Optional[Tuple[int, bytes]]:
        """Wait for a packet and return (command_id, payload)."""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            with self._lock:
                if self.message_queue:
                    return self.message_queue.pop(0)
            time.sleep(0.01)
        return None
    
    def _on_message(self, ws, message):
        """Handle incoming binary message."""
        try:
            if len(message) < 8:  # Minimum packet size (4 + 4 bytes)
                self.logger.error(f"Invalid packet size: {len(message)}")
                return
            
            # Unpack command ID and length
            command_id, length = struct.unpack('<II', message[:8])
            
            if len(message) != 8 + length:
                self.logger.error(f"Packet length mismatch: expected {8 + length}, got {len(message)}")
                return
            
            payload = message[8:]
            
            with self._lock:
                self.message_queue.append((command_id, payload))
            
            self.logger.debug(f"Received packet: command_id={command_id:#x}, length={length}")
            
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket error."""
        self.logger.error(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close."""
        self.connected = False
        self.logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
    
    def _on_open(self, ws):
        """Handle WebSocket open."""
        self.connected = True
        self.logger.info("WebSocket connection established")