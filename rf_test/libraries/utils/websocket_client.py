import json
import logging
import time
import threading
from typing import Optional, Dict, Any, Callable
import websocket


class WebSocketClient:
    def __init__(self):
        self.ws = None
        self.url = None
        self.connected = False
        self.message_queue = []
        self.response_callbacks = {}
        self.logger = logging.getLogger(__name__)
        
    def connect(self, url: str, timeout: int = 10) -> bool:
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
        if self.ws:
            self.ws.close()
            self.connected = False
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        try:
            self.ws.send(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Send message failed: {e}")
            return False
    
    def wait_for_message(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.message_queue:
                return self.message_queue.pop(0)
            time.sleep(0.1)
        return None
    
    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.message_queue.append(data)
            self.logger.debug(f"Received message: {data}")
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON received: {message}")
    
    def _on_error(self, ws, error):
        self.logger.error(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        self.logger.info("WebSocket connection closed")
    
    def _on_open(self, ws):
        self.connected = True
        self.logger.info("WebSocket connection established")