import os
import yaml
import json
import random
import string
from typing import Dict, Any, List
from robot.api.deco import keyword, library
from robot.api import logger


@library
class TestDataLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_data')
        self.cached_data = {}
    
    @keyword
    def load_test_data(self, filename: str) -> Dict[str, Any]:
        """Load test data from YAML file."""
        if filename in self.cached_data:
            return self.cached_data[filename]
        
        file_path = os.path.join(self.data_dir, filename)
        logger.info(f"Loading test data from: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.cached_data[filename] = data
                logger.info(f"Successfully loaded test data: {filename}")
                return data
        except Exception as e:
            logger.error(f"Failed to load test data from {filename}: {e}")
            raise Exception(f"Failed to load test data: {e}")
    
    @keyword
    def get_user_credentials(self, user_type: str = 'default') -> Dict[str, str]:
        """Get user credentials by type."""
        users_data = self.load_test_data('users.yaml')
        
        if user_type in users_data:
            credentials = users_data[user_type]
            logger.info(f"Retrieved credentials for user type: {user_type}")
            return credentials
        else:
            logger.error(f"User type '{user_type}' not found in test data")
            raise Exception(f"User type '{user_type}' not found")
    
    @keyword
    def get_room_data(self, room_type: str = 'default') -> Dict[str, Any]:
        """Get room configuration by type."""
        rooms_data = self.load_test_data('rooms.yaml')
        
        if room_type in rooms_data:
            room_info = rooms_data[room_type]
            logger.info(f"Retrieved room data for type: {room_type}")
            return room_info
        else:
            logger.error(f"Room type '{room_type}' not found in test data")
            raise Exception(f"Room type '{room_type}' not found")
    
    @keyword
    def get_bet_types(self) -> List[Dict[str, Any]]:
        """Get available betting options."""
        bet_data = self.load_test_data('bet_types.yaml')
        logger.info("Retrieved available bet types")
        return bet_data.get('bet_types', [])
    
    @keyword
    def get_random_bet_type(self) -> Dict[str, Any]:
        """Get a random betting option."""
        bet_types = self.get_bet_types()
        if not bet_types:
            raise Exception("No bet types available")
        
        selected_bet = random.choice(bet_types)
        logger.info(f"Selected random bet type: {selected_bet.get('name')}")
        return selected_bet
    
    @keyword
    def generate_random_username(self, prefix: str = 'testuser') -> str:
        """Generate a random username."""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f"{prefix}_{suffix}"
        logger.info(f"Generated random username: {username}")
        return username
    
    @keyword
    def generate_random_password(self, length: int = 8) -> str:
        """Generate a random password."""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choices(characters, k=length))
        logger.info("Generated random password")
        return password
    
    @keyword
    def get_test_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Get test scenario configuration."""
        scenarios_data = self.load_test_data('test_scenarios.yaml')
        
        if scenario_name in scenarios_data:
            scenario = scenarios_data[scenario_name]
            logger.info(f"Retrieved test scenario: {scenario_name}")
            return scenario
        else:
            logger.error(f"Test scenario '{scenario_name}' not found")
            raise Exception(f"Test scenario '{scenario_name}' not found")
    
    @keyword
    def get_environment_config(self, env_name: str = 'dev') -> Dict[str, Any]:
        """Get environment-specific configuration."""
        config_file = f"{env_name}_config.yaml"
        
        try:
            config_data = self.load_test_data(config_file)
            logger.info(f"Retrieved environment config for: {env_name}")
            return config_data
        except:
            logger.warn(f"Environment config for '{env_name}' not found, using defaults")
            return {
                'server_host': 'localhost',
                'server_port': 8080,
                'timeout': 30
            }
    
    @keyword
    def validate_test_data_integrity(self) -> bool:
        """Validate that all required test data files exist and are valid."""
        required_files = ['users.yaml', 'rooms.yaml', 'bet_types.yaml', 'test_scenarios.yaml']
        
        for filename in required_files:
            try:
                self.load_test_data(filename)
                logger.info(f"Test data file validated: {filename}")
            except Exception as e:
                logger.error(f"Test data validation failed for {filename}: {e}")
                return False
        
        logger.info("All test data files validated successfully")
        return True
    
    @keyword
    def clear_cached_data(self):
        """Clear cached test data."""
        self.cached_data.clear()
        logger.info("Cached test data cleared")
    
    @keyword
    def create_mock_user(self, username: str = None, password: str = None) -> Dict[str, str]:
        """Create mock user credentials for testing."""
        mock_username = username or self.generate_random_username()
        mock_password = password or self.generate_random_password()
        
        mock_user = {
            'username': mock_username,
            'password': mock_password,
            'email': f"{mock_username}@test.com",
            'user_type': 'mock'
        }
        
        logger.info(f"Created mock user: {mock_username}")
        return mock_user