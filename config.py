"""
Configuration settings for the Gaming System
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    """Server configuration settings"""
    host: str = "localhost"
    port: int = 8765
    max_connections: int = 100
    ping_interval: int = 20
    ping_timeout: int = 10
    max_message_size: int = 1024 * 1024  # 1MB
    
    # Security settings
    session_timeout: int = 1800  # 30 minutes
    rate_limit_messages: int = 100  # per minute
    bcrypt_rounds: int = 12
    
    # Game settings
    max_bets_per_round: int = 10
    min_bet_amount: int = 1
    max_bet_amount: int = 1000
    default_user_balance: int = 1000
    stale_round_timeout: int = 600  # 10 minutes
    
    # Room settings
    default_room_count: int = 10
    max_room_capacity: int = 50
    
    # Cleanup intervals
    cleanup_interval: int = 300  # 5 minutes
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Create configuration from environment variables"""
        return cls(
            host=os.getenv('GAME_HOST', cls.host),
            port=int(os.getenv('GAME_PORT', str(cls.port))),
            max_connections=int(os.getenv('GAME_MAX_CONNECTIONS', str(cls.max_connections))),
            session_timeout=int(os.getenv('GAME_SESSION_TIMEOUT', str(cls.session_timeout))),
            max_bets_per_round=int(os.getenv('GAME_MAX_BETS_PER_ROUND', str(cls.max_bets_per_round))),
            min_bet_amount=int(os.getenv('GAME_MIN_BET', str(cls.min_bet_amount))),
            max_bet_amount=int(os.getenv('GAME_MAX_BET', str(cls.max_bet_amount))),
            default_user_balance=int(os.getenv('GAME_DEFAULT_BALANCE', str(cls.default_user_balance)))
        )


@dataclass
class ClientConfig:
    """Client configuration settings"""
    server_url: str = "ws://localhost:8765"
    connection_timeout: int = 10
    reconnect_attempts: int = 3
    reconnect_delay: int = 5
    
    @classmethod
    def from_env(cls) -> 'ClientConfig':
        """Create configuration from environment variables"""
        return cls(
            server_url=os.getenv('GAME_SERVER_URL', cls.server_url),
            connection_timeout=int(os.getenv('GAME_CONNECTION_TIMEOUT', str(cls.connection_timeout))),
            reconnect_attempts=int(os.getenv('GAME_RECONNECT_ATTEMPTS', str(cls.reconnect_attempts)))
        )


@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "game_server.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create configuration from environment variables"""
        return cls(
            level=os.getenv('GAME_LOG_LEVEL', cls.level),
            file_path=os.getenv('GAME_LOG_FILE', cls.file_path)
        )


# Global configuration instances
server_config = ServerConfig.from_env()
client_config = ClientConfig.from_env()
logging_config = LoggingConfig.from_env()