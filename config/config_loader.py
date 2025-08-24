#!/usr/bin/env python3
"""
Configuration loader for sample_gaming_sut
Single source of truth for all server connection settings
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration loader and manager"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to config.yaml in the same directory as this script
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def get_active_environment(self) -> str:
        """Get the currently active environment"""
        return self._config.get('active', {}).get('environment', 'development')
    
    def get_active_deployment_mode(self) -> str:
        """Get the currently active deployment mode"""
        return self._config.get('active', {}).get('deployment_mode', 'docker_in_docker')
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration with environment overrides applied"""
        base_config = self._config.get('server', {})
        
        # Apply environment-specific overrides
        env = self.get_active_environment()
        env_config = self._config.get('environments', {}).get(env, {}).get('server', {})
        
        # Merge configurations (environment overrides base)
        merged_config = {**base_config, **env_config}
        return merged_config
    
    def get_server_url(self) -> str:
        """Get the appropriate server URL based on active deployment mode"""
        server_config = self.get_server_config()
        deployment_mode = self.get_active_deployment_mode()
        
        # Get URL template for deployment mode
        deployment_config = self._config.get('deployment', {}).get(deployment_mode, {})
        url_template = deployment_config.get('url_template', 'ws://localhost:8767')
        
        # Format URL with server config values
        return url_template.format(**server_config)
    
    def get_host_port(self) -> int:
        """Get the port that should be used for external connections"""
        server_config = self.get_server_config()
        deployment_mode = self.get_active_deployment_mode()
        
        if deployment_mode == 'docker_in_docker':
            return server_config.get('docker_host_port', 8768)
        else:
            return server_config.get('jenkins_direct_port', 8767)
    
    def get_internal_port(self) -> int:
        """Get the port used inside containers/processes"""
        return self.get_server_config().get('internal_port', 8767)
    
    def get_jenkins_pipeline_vars(self) -> Dict[str, str]:
        """Get variables for Jenkins pipeline"""
        server_config = self.get_server_config()
        return {
            'SERVER_HOST': server_config.get('host', '0.0.0.0'),
            'SERVER_PORT': str(server_config.get('internal_port', 8767)),
            'EXTERNAL_HOST': server_config.get('external_host', 'localhost'),
            'HOST_PORT': str(self.get_host_port()),
            'MAX_CONNECTIONS': str(server_config.get('max_connections', 200))
        }
    
    def get_robot_framework_vars(self) -> Dict[str, str]:
        """Get variables for Robot Framework"""
        server_config = self.get_server_config()
        return {
            'SERVER_URL': self.get_server_url(),
            'TIMEOUT': str(server_config.get('timeout', 30)),
            'CONNECTION_TIMEOUT': str(server_config.get('connection_timeout', 10))
        }
    
    def export_robot_vars(self, output_file: str = None) -> str:
        """Export Robot Framework variables to a .robot file"""
        if output_file is None:
            output_file = Path(__file__).parent.parent / "rf_test" / "generated_config.robot"
        
        vars_dict = self.get_robot_framework_vars()
        
        content = "*** Variables ***\n"
        content += "# Generated configuration - DO NOT EDIT MANUALLY\n"
        content += "# This file is generated from config.yaml\n\n"
        
        for key, value in vars_dict.items():
            content += f"${{{key}}}\t{value}\n"
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        return str(output_file)
    
    def print_summary(self):
        """Print configuration summary"""
        print("=== Configuration Summary ===")
        print(f"Environment: {self.get_active_environment()}")
        print(f"Deployment Mode: {self.get_active_deployment_mode()}")
        print(f"Server URL: {self.get_server_url()}")
        print(f"Host Port: {self.get_host_port()}")
        print(f"Internal Port: {self.get_internal_port()}")
        print()
        
        print("Jenkins Pipeline Variables:")
        for key, value in self.get_jenkins_pipeline_vars().items():
            print(f"  {key}={value}")
        print()
        
        print("Robot Framework Variables:")
        for key, value in self.get_robot_framework_vars().items():
            print(f"  {key}={value}")


def main():
    """CLI interface for configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configuration manager for sample_gaming_sut')
    parser.add_argument('--summary', action='store_true', help='Print configuration summary')
    parser.add_argument('--export-robot', action='store_true', help='Export Robot Framework variables')
    parser.add_argument('--config', help='Path to config.yaml file')
    
    args = parser.parse_args()
    
    config = Config(args.config)
    
    if args.summary:
        config.print_summary()
    
    if args.export_robot:
        output_file = config.export_robot_vars()
        print(f"Robot Framework variables exported to: {output_file}")
    
    if not args.summary and not args.export_robot:
        config.print_summary()


if __name__ == '__main__':
    main()