#!/usr/bin/env python3
"""
Update Jenkins pipeline configuration from config.yaml
"""

import re
from pathlib import Path
from config_loader import Config


def update_jenkinsfile_variables(config: Config):
    """Update Jenkins pipeline variables"""
    jenkinsfile_path = Path(__file__).parent / "jenkins" / "server_jenkinsfile"
    
    if not jenkinsfile_path.exists():
        print(f"Jenkinsfile not found: {jenkinsfile_path}")
        return
    
    # Get configuration values
    jenkins_vars = config.get_jenkins_pipeline_vars()
    host_port = config.get_host_port()
    
    # Read current content
    with open(jenkinsfile_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update environment variables section
    patterns = [
        (r"SERVER_PORT = '[^']*'", f"SERVER_PORT = '{jenkins_vars['SERVER_PORT']}'"),
        (r"SERVER_HOST = '[^']*'", f"SERVER_HOST = '{jenkins_vars['SERVER_HOST']}'"),
        (r"MAX_CONNECTIONS = '[^']*'", f"MAX_CONNECTIONS = '{jenkins_vars['MAX_CONNECTIONS']}'"),
        (r"defaultValue: '[^']*',\s*description: 'Port for the Tornado server'", 
         f"defaultValue: '{jenkins_vars['SERVER_PORT']}', description: 'Port for the Tornado server'"),
        (r"defaultValue: '[^']*',\s*description: 'Maximum concurrent connections'",
         f"defaultValue: '{jenkins_vars['MAX_CONNECTIONS']}', description: 'Maximum concurrent connections'"),
    ]
    
    # Update Docker port mapping
    patterns.extend([
        (r'-p \d+:8767', f'-p {host_port}:8767'),
        (r'port \d+ found on host', f'port {host_port} found on host'),
        (r'host port \d+ ->', f'host port {host_port} ->'),
    ])
    
    # Apply patterns
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Write updated content
    with open(jenkinsfile_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated Jenkins pipeline configuration in {jenkinsfile_path}")


def update_docker_compose_ports(config: Config):
    """Update docker-compose port configurations"""
    compose_files = [
        Path(__file__).parent / "dockers" / "docker-compose.yml",
        Path(__file__).parent / "jenkins" / "docker-compose.yml"
    ]
    
    jenkins_direct_port = config.get_server_config().get('jenkins_direct_port', 8767)
    
    for compose_file in compose_files:
        if not compose_file.exists():
            continue
            
        with open(compose_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update Jenkins container port mapping
        content = re.sub(
            r'"8767:8767".*# Game server port',
            f'"{jenkins_direct_port}:{jenkins_direct_port}"    # Game server port (for testing)',
            content
        )
        
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated Docker Compose configuration in {compose_file}")


def main():
    """Update all configuration files from config.yaml"""
    config = Config()
    
    print("=== Updating Configuration Files ===")
    print(f"Active Environment: {config.get_active_environment()}")
    print(f"Active Deployment Mode: {config.get_active_deployment_mode()}")
    print(f"Server URL: {config.get_server_url()}")
    print()
    
    # Update Robot Framework configuration
    output_file = config.export_robot_vars()
    print(f"Updated Robot Framework: {output_file}")
    
    # Update Jenkins pipeline
    update_jenkinsfile_variables(config)
    print("Updated Jenkins pipeline configuration")
    
    # Update Docker Compose files
    update_docker_compose_ports(config)
    print("Updated Docker Compose configurations")
    
    print()
    print("=== Configuration Update Complete ===")
    print("All configuration files have been updated from config.yaml")
    print("Single source of truth is now active!")


if __name__ == '__main__':
    main()