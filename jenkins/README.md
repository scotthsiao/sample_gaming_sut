# Jenkins Setup for sample_gaming_sut

This directory contains Jenkins pipeline configuration for automated deployment and management of the Tornado game server.

## 📁 Files

- **`server_jenkinsfile`** - Main Jenkins pipeline for server control
- **`setup_jenkins_agent.sh`** - Script to prepare Jenkins agents with required dependencies
- **`README.md`** - This documentation

## 🚀 Quick Start

### 1. Prepare Jenkins Agent

First, ensure your Jenkins agent has the required dependencies:

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
| SERVER_PORT | `8767` | Port for the Tornado server |
| MAX_CONNECTIONS | `200` | Maximum concurrent connections |

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

### Start Action Flow
1. **Checkout Code** - Pull latest from GitHub
2. **Setup Environment** - Create venv, install dependencies, compile proto files
3. **Start Server** - Launch Tornado server in background
4. **Server Status** - Verify server is running

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

## 🗂️ File Locations

The pipeline creates these files in the Jenkins workspace:

| File | Purpose |
|------|---------|
| `tornado_server.pid` | Process ID of running server |
| `tornado_server.log` | Server output and error logs |
| `venv/` | Python virtual environment |
| `requirements.txt` | Python dependencies |
| `proto/game_messages.proto` | Protocol Buffers schema |

## 🔍 Monitoring

### Server Status Information
- **Process Status**: PID and running state
- **Network Ports**: Listening ports and connections
- **Recent Logs**: Last 10 lines of server output
- **System Processes**: All Python processes

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
- Another server instance is running
- Run the pipeline with ACTION=stop first
- Or choose a different SERVER_PORT

**Permission denied errors**
- Ensure Jenkins agent has write permissions to workspace
- Check that ports are not restricted by firewall

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
# Look for server processes
ps aux | grep tornado

# Check server logs
tail -f tornado_server.log

# Verify network connectivity
telnet localhost 8767
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