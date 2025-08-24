# Jenkins Setup for sample_gaming_sut

This directory contains Jenkins pipeline configuration for automated deployment and management of the Tornado game server using **Docker-in-Docker** for complete process isolation and centralized configuration management.

## 📁 Files

- **`server_jenkinsfile`** - Main Jenkins pipeline with Docker-in-Docker support
- **`docker-compose.yml`** - Docker Compose configuration for Jenkins container
- **`README.md`** - This documentation

## 🔧 Key Features

- **Docker-in-Docker**: Game servers run in completely isolated containers
- **Process Persistence**: Servers survive Jenkins job completion
- **Configuration Management**: Uses centralized `config.yaml` for all settings
- **Port Mapping**: Host port 8768 → Container port 8767
- **File Copying**: Avoids Windows volume mounting issues
- **Complete Automation**: Pull code → Setup → Deploy → Verify

## 🚀 Quick Start

### Option 1: Docker Setup (Recommended for Isolation)

For Jenkins running in Docker containers:

```bash
# Clone repository
git clone https://github.com/scotthsiao/sample_gaming_sut.git
cd sample_gaming_sut/jenkins

# Start Jenkins with Docker Compose
docker-compose up -d

# Access Jenkins at http://localhost:8080
# See DOCKER_SETUP.md for complete guide
```

### Option 2: Native Setup (Direct Installation)

For Jenkins running directly on host systems:

```bash
# Download and run the setup script
curl -sSL https://raw.githubusercontent.com/scotthsiao/sample_gaming_sut/main/jenkins/setup_jenkins_agent.sh | bash

# Or if you have the repository cloned:
cd jenkins
chmod +x setup_jenkins_agent.sh
./setup_jenkins_agent.sh
```

### 2. Create Jenkins Pipeline Job

1. **Create New Item** in Jenkins
2. Choose **"Pipeline"** job type
3. Name it something like `sample_gaming_sut_server`

### 3. Configure Pipeline

In the job configuration:

1. **Pipeline Definition**: Choose "Pipeline script from SCM"
2. **SCM**: Choose "Git"
3. **Repository URL**: `https://github.com/scotthsiao/sample_gaming_sut.git`
4. **Branch**: `*/main`
5. **Script Path**: `jenkins/server_jenkinsfile`

### 4. Run the Pipeline

The pipeline supports these actions:
- **`start`** - Pull latest code and start server
- **`stop`** - Stop the running server  
- **`restart`** - Stop and restart with latest code
- **`status`** - Check server status and logs

## 🛠️ Requirements

### System Requirements
- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Protocol Buffers**: `protoc` compiler
- **Network**: Access to GitHub and port 8767

### Jenkins Agent Requirements
- **Jenkins**: 2.400+ with Pipeline plugin
- **Git**: For repository cloning
- **Shell Access**: bash (Linux/macOS) or cmd (Windows)

## 📊 Pipeline Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| ACTION | `start` | Action to perform: start/stop/restart/status |
| SERVER_PORT | `8767` | Internal container port (Docker-in-Docker) |
| MAX_CONNECTIONS | `200` | Maximum concurrent connections |

**Docker-in-Docker Configuration:**
- **Host Port**: 8768 (externally accessible)
- **Container Port**: 8767 (internal)
- **Network**: `dockers_jenkins-network` (isolated)
- **Process Isolation**: Complete separation from Jenkins process

## 🔧 Manual Agent Setup

If the automatic setup script doesn't work, install manually:

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv protobuf-compiler
```

### RHEL/CentOS/Rocky Linux
```bash
# RHEL 7
sudo yum install -y python3 python3-pip protobuf-compiler

# RHEL 8+
sudo dnf install -y python3 python3-pip protobuf-compiler
```

### macOS
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 protobuf
```

### Windows

#### Native Windows
1. Install Python 3.8+ from [python.org](https://python.org)
2. Install Protocol Buffers from [releases](https://github.com/protocolbuffers/protobuf/releases)
3. Add both to system PATH

#### WSL (Windows Subsystem for Linux)
```bash
# WSL Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv protobuf-compiler

# WSL RHEL/CentOS
sudo yum install -y python3 python3-pip protobuf-compiler

# Or use the setup script (recommended)
curl -sSL https://raw.githubusercontent.com/scotthsiao/sample_gaming_sut/main/jenkins/setup_jenkins_agent.sh | bash
```

## 📁 Pipeline Workflow

### Start Action Flow (Docker-in-Docker)
1. **Checkout Code** - Pull latest from GitHub
2. **Setup Environment** - Create Python venv, install dependencies, compile proto files
3. **Stop Existing Containers** - Clean up any existing game server containers
4. **Start Docker Container** - Create new isolated container with Python 3.11
5. **Copy Files** - Copy project files to container (avoids volume mount issues)
6. **Install Dependencies** - Install requirements.txt inside container
7. **Start Server** - Launch Tornado server inside container
8. **Verify Status** - Confirm container and server are running

### Stop Action Flow
1. **Stop Server** - Gracefully shutdown server process
2. **Server Status** - Confirm server is stopped

### Restart Action Flow
1. **Checkout Code** - Pull latest from GitHub  
2. **Setup Environment** - Refresh dependencies
3. **Stop Server** - Stop existing server
4. **Start Server** - Start server with new code
5. **Server Status** - Verify new server is running

### Status Action Flow
1. **Server Status** - Check process status, logs, and network ports

## 🗂️ File Locations & Docker Integration

**Jenkins Workspace Files:**
| File | Purpose |
|------|---------|
| `tornado_server.pid` | Docker container ID (not process PID) |
| `tornado_server.log` | Server output and error logs |
| `venv/` | Python virtual environment (for Jenkins) |
| `requirements.txt` | Python dependencies |
| `proto/game_messages.proto` | Protocol Buffers schema |

**Docker Container Structure:**
```
/app/ (inside container)
├── requirements.txt
├── run_tornado_server.py
├── src/
├── proto/
└── [all project files]
```

**Configuration Management:**
- `config.yaml` → Master configuration file
- `generated_config.robot` → Auto-generated Robot Framework settings
- Jenkins pipeline uses `config_loader.py` for dynamic configuration

## 🔍 Monitoring

### Server Status Information
- **Container Status**: Docker container running state and ID
- **Network Ports**: Host port 8768 → Container port 8767 mapping
- **Container Logs**: Server output from Docker container
- **Process Isolation**: Game server completely isolated from Jenkins
- **Configuration**: Dynamic settings from `config.yaml`

### Log Management
- Logs are automatically archived as Jenkins artifacts
- Old log files are cleaned up (keeps last 5)
- Log rotation prevents disk space issues

## 🚨 Troubleshooting

### Common Issues

**"python3: not found"**
- Run the setup script: `./setup_jenkins_agent.sh`
- Or install Python manually (see Manual Setup)

**"protoc: not found"**  
- Install Protocol Buffers compiler
- Ubuntu: `sudo apt-get install protobuf-compiler`
- macOS: `brew install protobuf`

**"requirements.txt not found"**
- Ensure the GitHub repository has been cloned correctly
- Check the workspace directory structure

**"Port already in use"**
- Another Docker container is using port 8768
- Run the pipeline with ACTION=stop first
- Check: `docker ps` for running containers
- Force cleanup: `docker stop game-server-instance && docker rm game-server-instance`

**Permission denied errors**
- Ensure Jenkins container has Docker access
- Check Docker daemon is running: `docker ps`
- Verify Docker-in-Docker permissions
- Check that ports 8768 are not restricted by firewall

**WSL-specific issues**
- **"python3: not found" in WSL**: Install Python in WSL, not Windows
- **Jenkins can't access WSL**: Ensure Jenkins runs in WSL context
- **Port binding issues**: WSL networking may require Windows firewall configuration
- **File permissions**: WSL and Windows file permissions can conflict

### Debug Commands

Check agent setup:
```bash
# Verify Python
python3 --version || python --version

# Verify protoc
protoc --version

# Verify pip
pip3 --version || pip --version

# Check ports
netstat -tlnp | grep 8767
```

Check server status:
```bash
# Look for Docker containers
docker ps | grep game-server

# Check container logs
docker logs game-server-instance

# Verify network connectivity (host port)
telnet localhost 8768

# Access container shell
docker exec -it game-server-instance bash
```

## 🔐 Security Considerations

- **Repository Access**: Uses HTTPS (no credentials needed for public repo)
- **Network Ports**: Server binds to configurable port (default 8767)
- **Process Management**: Proper PID tracking and cleanup
- **Log Security**: Logs are stored in Jenkins workspace (access controlled)

## 📈 Performance Tuning

### Server Configuration
- Adjust `MAX_CONNECTIONS` based on expected load
- Monitor memory usage with high connection counts
- Use `SERVER_PORT` parameter for multiple instances

### Jenkins Configuration
- Use dedicated agents for server deployment
- Configure build retention to manage disk space
- Set appropriate timeouts for your environment

## 🔄 Integration Examples

### Automated Deployment
```groovy
// Trigger deployment on code changes
pipeline {
    triggers {
        pollSCM('H/5 * * * *')  // Check every 5 minutes
    }
}
```

### Multi-Environment Setup
```groovy
// Deploy to different environments
parameters {
    choice(
        name: 'ENVIRONMENT',
        choices: ['dev', 'staging', 'prod'],
        description: 'Target environment'
    )
}
```

### Integration with Tests
```groovy
// Run tests after deployment
post {
    success {
        build job: 'sample_gaming_sut_tests'
    }
}
```

## 📞 Support

For issues with:
- **Pipeline Configuration**: Check Jenkins logs and this README
- **Server Issues**: Check `tornado_server.log` and application documentation  
- **Agent Setup**: Run setup script with verbose output
- **General Questions**: Refer to main project documentation

---

*Happy deploying! 🚀*