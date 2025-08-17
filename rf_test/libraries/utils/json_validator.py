import json
import logging
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError


class JSONValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            self.logger.error(f"JSON validation failed: {e.message}")
            return False
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    def load_schema_from_file(self, schema_path: str) -> Optional[Dict[str, Any]]:
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load schema from {schema_path}: {e}")
            return None
    
    def validate_response_structure(self, response: Dict[str, Any], required_fields: list) -> bool:
        for field in required_fields:
            if field not in response:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True
    
    def validate_message_type(self, message: Dict[str, Any], expected_type: str) -> bool:
        message_type = message.get('type', '')
        if message_type != expected_type:
            self.logger.error(f"Expected message type '{expected_type}', got '{message_type}'")
            return False
        return True