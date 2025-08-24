# WSL Setup Guide for Jenkins Pipeline

This guide explains how to set up and use the Jenkins pipeline in Windows Subsystem for Linux (WSL) environments.

## 🔍 WSL Detection and Handling

The Jenkins pipeline and setup script automatically detect WSL environments by checking:
- `/proc/version` contains "microsoft" or "wsl"
- Provides WSL-specific installation instructions
- Handles WSL networking considerations

## 🚀 Quick WSL Setup

### Option 1: Automated Setup (Recommended)
```bash
# Run in WSL terminal
curl -sSL https://raw.githubusercontent.com/scotthsiao/sample_gaming_sut/main/jenkins/setup_jenkins_agent.sh | bash
```

### Option 2: Manual Setup

#### Ubuntu/Debian WSL
```bash
# Update package list
sudo apt-get update

# Install Python 3 and tools
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

# Install Protocol Buffers compiler
sudo apt-get install -y protobuf-compiler

# Verify installations
python3 --version
pip3 --version
protoc --version
```

#### RHEL/CentOS/Rocky Linux WSL
```bash
# Install Python 3 and tools
sudo yum install -y python3 python3-pip python3-devel

# For RHEL 8+/Rocky Linux
sudo dnf install -y python3 python3-pip python3-devel

# Install Protocol Buffers compiler
sudo yum install -y protobuf-compiler
# Or for RHEL 8+
sudo dnf install -y protobuf-compiler

# Verify installations
python3 --version
pip3 --version
protoc --version
```

## 🏗️ Jenkins in WSL Scenarios

### Scenario 1: Jenkins Running in WSL
**Setup**: Jenkins server and agents run inside WSL

**Advantages**:
- Native Linux environment
- Direct Python/protoc access
- Simple networking

**Configuration**:
```bash
# Install Jenkins in WSL
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins

# Start Jenkins
sudo systemctl start jenkins
```

### Scenario 2: Jenkins on Windows, Agent in WSL
**Setup**: Jenkins server on Windows, agents connect from WSL

**Advantages**:
- Windows Jenkins GUI
- WSL execution environment
- Best of both worlds

**Configuration**:
1. **Windows Jenkins Server**: Install Jenkins on Windows
2. **WSL Agent Setup**:
   ```bash
   # In WSL, install Java for Jenkins agent
   sudo apt-get install -y default-jre-headless
   
   # Download agent jar (replace URL with your Jenkins URL)
   wget http://your-jenkins:8080/jnlpJars/agent.jar
   
   # Run agent (replace with your secret and agent name)
   java -jar agent.jar -jnlpUrl http://your-jenkins:8080/computer/wsl-agent/slave-agent.jnlp -secret your-secret
   ```

### Scenario 3: Windows Jenkins, WSL via Remote
**Setup**: Jenkins on Windows executes commands in WSL remotely

**Configuration**:
```groovy
// In Jenkinsfile, execute WSL commands
bat 'wsl -d Ubuntu python3 --version'
bat 'wsl -d Ubuntu curl -sSL setup_script.sh | bash'
```

## 🌐 Networking Considerations

### Port Access from Windows
When server runs in WSL, access from Windows:
```bash
# WSL 2: Server binds to WSL IP
# Windows access: http://WSL_IP:8767

# Check WSL IP
ip addr show eth0

# Access from Windows browser
# Use: http://172.x.x.x:8767
```

### Firewall Configuration
```bash
# Windows Firewall: Allow port 8767
# PowerShell (as Administrator):
New-NetFirewallRule -DisplayName "WSL Server" -Direction Inbound -Protocol TCP -LocalPort 8767 -Action Allow

# Or disable Windows Firewall for private networks
```

### WSL 2 vs WSL 1 Networking
- **WSL 1**: Direct Windows network integration
- **WSL 2**: Separate network namespace, requires port forwarding

## 🔧 WSL-Specific Pipeline Behavior

### Environment Detection
```bash
# Pipeline automatically detects WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "WSL detected - using WSL-specific setup"
fi
```

### Installation Messages
When WSL is detected, the pipeline provides:
- WSL-specific installation commands
- WSL distribution detection (Ubuntu, RHEL)
- Interop warnings where applicable

### Path Handling
```bash
# WSL paths work normally
/home/user/workspace/sample_gaming_sut

# Windows paths accessible via /mnt/
/mnt/c/Users/User/Projects/
```

## 🚨 Common WSL Issues and Solutions

### 1. "python3: not found"
**Problem**: Python installed on Windows, not in WSL

**Solution**:
```bash
# Install Python IN WSL, not Windows
sudo apt-get install -y python3 python3-pip python3-venv
```

### 2. Jenkins Can't Find WSL Commands
**Problem**: Jenkins running on Windows can't execute WSL commands

**Solution**:
```groovy
// Use wsl command prefix
bat 'wsl python3 --version'
// Or run Jenkins agent inside WSL
```

### 3. Port Binding Issues
**Problem**: Server starts but not accessible from Windows

**Solution**:
```bash
# Check WSL IP
hostname -I

# Bind to all interfaces
python run_tornado_server.py --host 0.0.0.0 --port 8767

# Configure Windows firewall
New-NetFirewallRule -DisplayName "WSL Server" -Direction Inbound -Protocol TCP -LocalPort 8767 -Action Allow
```

### 4. File Permission Errors
**Problem**: WSL/Windows file permission conflicts

**Solution**:
```bash
# Set WSL file permissions
chmod +x scripts/*

# Or use WSL-native paths
cd /home/user/project  # Instead of /mnt/c/Users/...
```

### 5. Git Line Ending Issues
**Problem**: Git converts line endings between Windows/WSL

**Solution**:
```bash
# Configure Git in WSL
git config --global core.autocrlf input
git config --global core.eol lf

# Or in repository
echo "* text=auto eol=lf" > .gitattributes
```

## 🎯 Best Practices for WSL

### 1. Use WSL-Native Paths
```bash
# Good: WSL filesystem
/home/user/jenkins/workspace/

# Avoid: Windows filesystem via WSL
/mnt/c/Users/User/jenkins/
```

### 2. Install Dependencies in WSL
```bash
# Install all tools in WSL environment
sudo apt-get install python3 python3-pip protobuf-compiler

# Don't rely on Windows installations
```

### 3. Configure WSL Memory
```bash
# ~/.wslconfig (Windows user home)
[wsl2]
memory=4GB
processors=2
```

### 4. Use WSL 2 for Better Performance
```powershell
# Check WSL version
wsl -l -v

# Upgrade to WSL 2
wsl --set-version Ubuntu 2
```

### 5. Jenkins Agent Configuration
```xml
<!-- For WSL agents, set working directory -->
<workingDirectory>/home/jenkins</workingDirectory>
<javaPath>/usr/bin/java</javaPath>
```

## 🔍 Debugging WSL Issues

### Check WSL Environment
```bash
# Verify WSL version
cat /proc/version

# Check network configuration
ip addr show

# Check available tools
which python3 pip3 protoc java
```

### Test Server Connectivity
```bash
# Start server in WSL
python3 run_tornado_server.py --host 0.0.0.0 --port 8767

# Test from WSL
curl ws://localhost:8767

# Test from Windows
# Use WSL IP: ws://172.x.x.x:8767
```

### Jenkins Pipeline Debug
```groovy
// Add debug steps to pipeline
stage('Debug WSL') {
    steps {
        sh '''
            echo "WSL Detection:"
            cat /proc/version || true
            echo "Python location:"
            which python3 || which python || echo "Not found"
            echo "Network config:"
            hostname -I
        '''
    }
}
```

## 📚 Additional Resources

- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Jenkins on WSL](https://www.jenkins.io/doc/tutorials/tutorial-for-installing-jenkins-on-AWS/)
- [WSL Networking](https://docs.microsoft.com/en-us/windows/wsl/networking)
- [WSL File System](https://docs.microsoft.com/en-us/windows/wsl/filesystems)

---

*WSL makes Linux development on Windows seamless! 🐧🪟*