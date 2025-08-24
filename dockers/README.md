# Docker Setup for sample_gaming_sut

Complete Docker environment for Jenkins automation with **centralized configuration management** and **Docker-in-Docker** support for process isolation.

## 🚀 Quick Start

```bash
# From the project root directory
cd dockers

# Build and start Jenkins
docker-compose up -d

# Check logs
docker-compose logs -f jenkins

# Get initial admin password
docker-compose logs jenkins 2>&1 | grep "initialAdminPassword"

# Access Jenkins at http://localhost:8080
```

## 🏗️ Architecture

### Services
- **jenkins**: Custom Jenkins with Python 3.11, Protocol Buffers, and Docker-in-Docker support
- **game-server**: Optional Python container for testing

### Volumes
- **jenkins_home**: Persistent Jenkins data (your existing volume structure)
- **docker.sock**: Docker-in-Docker support for isolated game server containers
- **Project mount**: Read-only access to source code at `/opt/sample_gaming_sut`

### Networks
- **jenkins-network**: Isolated network for service communication

### Configuration Management
- **Single Source of Truth**: All settings centralized in `config.yaml`
- **Dynamic Updates**: Configuration applied automatically via `update_jenkins_config.py`
- **Port Management**: Host port 8768 → Container port 8767 mapping
- **Environment-Specific**: Development/staging/production configurations

## 📁 Directory Structure

```
dockers/
├── docker-compose.yml          # Main orchestration file
├── jenkins/
│   ├── Dockerfile             # Custom Jenkins image with Python/protoc
│   └── setup_jenkins_docker.sh # Container verification script
└── README.md                  # This file
```

## 🔧 Configuration Details

### Jenkins Container
```yaml
services:
  jenkins:
    build: jenkins/Dockerfile    # Custom image with Python
    ports:
      - "8080:8080"             # Jenkins UI
      - "50000:50000"           # Jenkins agents  
      - "8767:8767"             # Game server port
    volumes:
      - jenkins_home:/var/jenkins_home  # Your existing volume
      - /var/run/docker.sock:/var/run/docker.sock  # Docker access
      - ../:/opt/sample_gaming_sut:ro   # Project source (read-only)
```

### Custom Jenkins Image Features
- **Python 3.11**: Latest Python with pip, venv, dev tools
- **Protocol Buffers**: protoc compiler pre-installed
- **Pre-installed packages**: tornado, websockets, protobuf, bcrypt
- **Jenkins plugins**: Git, Pipeline, Docker, Blue Ocean
- **Development tools**: vim, nano, htop, curl
- **Docker-in-Docker**: Full Docker client and daemon access
- **Configuration Tools**: config_loader.py and update_jenkins_config.py
- **Jenkins User**: Added to docker group for container management

## 🎯 Pipeline Integration

### Pipeline Configuration
1. **Create Pipeline Job** in Jenkins UI
2. **Repository URL**: `https://github.com/scotthsiao/sample_gaming_sut.git`
3. **Script Path**: `jenkins/server_jenkinsfile`
4. **Branch**: `*/main`

### Available Actions
- **start**: Pull latest code, apply config from `config.yaml`, start game server in isolated container
- **stop**: Stop running game server container and clean up
- **restart**: Restart with fresh code and updated configuration
- **status**: Check Docker container status, port mappings, and server logs

### Docker-in-Docker Process
1. **Configuration Loading**: Pipeline loads settings from `config.yaml`
2. **Container Creation**: Creates isolated Python 3.11 container
3. **File Copying**: Copies project files (avoids Windows volume mount issues)
4. **Dependency Installation**: Installs requirements.txt inside container
5. **Server Startup**: Launches Tornado server on port 8767 (container)
6. **Port Mapping**: Maps container port 8767 to host port 8768
7. **Process Isolation**: Game server completely isolated from Jenkins

## 📊 Verification

### Container Health Check
```bash
# Check container status
docker-compose ps

# Verify Python environment inside container
docker-compose exec jenkins python3 --version
docker-compose exec jenkins pip3 --version
docker-compose exec jenkins protoc --version

# Run full verification script
docker-compose exec jenkins /usr/local/jenkins-tools/setup_jenkins_docker.sh
```

### Access Points
- **Jenkins UI**: http://localhost:8080
- **Game Server** (when running via Docker-in-Docker): ws://localhost:8768
- **Game Server** (direct Jenkins): ws://localhost:8767 (legacy mode)
- **Jenkins Container Shell**: `docker-compose exec jenkins bash`
- **Game Server Container Shell**: `docker exec -it game-server-instance bash`

### Configuration Management
- **Master Config**: `/opt/sample_gaming_sut/config.yaml`
- **Generated Robot Framework Config**: `rf_test/generated_config.robot`
- **Pipeline Config Updates**: Automatic via `update_jenkins_config.py`
- **Port Configuration**: Dynamically set based on deployment mode

## 🔍 Volume Details

### jenkins_home Volume
Your existing Jenkins data structure is preserved:
```
jenkins_home/
├── config.xml
├── jobs/
├── plugins/
├── secrets/
├── workspace/
└── ...
```

### Project Source Mount
Project source is mounted read-only at `/opt/sample_gaming_sut`:
```
/opt/sample_gaming_sut/
├── requirements.txt
├── run_tornado_server.py
├── proto/
├── src/
└── rf_test/
```

## 🚨 Troubleshooting

### Common Issues

**"Build failed" on first run**
```bash
# Clean build
docker-compose build --no-cache jenkins
docker-compose up -d
```

**"Python not found" in pipeline**
```bash
# Verify Python installation
docker-compose exec jenkins python3 --version

# Run verification script
docker-compose exec jenkins /usr/local/jenkins-tools/setup_jenkins_docker.sh
```

**Port conflicts**
```bash
# If port 8080 is in use, modify docker-compose.yml:
ports:
  - "8081:8080"  # Use different host port
```

**Volume permissions**
```bash
# Fix Jenkins home permissions
docker-compose exec -u root jenkins chown -R jenkins:jenkins /var/jenkins_home
```

### Debug Commands

```bash
# Container logs
docker-compose logs jenkins

# Interactive shell
docker-compose exec jenkins bash

# Check mounted volumes
docker-compose exec jenkins ls -la /opt/sample_gaming_sut

# Network connectivity
docker-compose exec jenkins curl -I https://github.com
```

## 🔄 Development Workflow

### 1. Code Development
```bash
# Make changes in your local repository
git add .
git commit -m "Update server code"
git push origin main
```

### 2. Configuration Management
```bash
# Update configuration if needed
edit config.yaml

# Apply configuration changes
python update_jenkins_config.py

# Verify Robot Framework config
cat rf_test/generated_config.robot
```

### 3. Jenkins Pipeline (Docker-in-Docker)
```bash
# Trigger in Jenkins UI or via webhook
# Pipeline will:
# 1. Pull latest code from GitHub
# 2. Load configuration from config.yaml
# 3. Create isolated Docker container
# 4. Copy files and install dependencies
# 5. Start Tornado server (container:8767 → host:8768)
# 6. Verify container status and connectivity
```

### 4. Testing
```bash
# Run Robot Framework tests (auto-configured)
cd rf_test
robot tests/

# Tests connect to ws://localhost:8768 (Docker-in-Docker mode)
# Configuration automatically applied from config.yaml

# Optional: Direct container testing
docker exec -it game-server-instance bash
ps aux | grep tornado  # Check server process inside container
```

## 🛠️ Customization

### Adding Python Packages
Edit `jenkins/Dockerfile`:
```dockerfile
RUN python3 -m pip install \
    tornado \
    websockets \
    your-additional-package
```

### Configuration Customization
Edit `config.yaml` for centralized settings:
```yaml
server:
  host: "0.0.0.0"
  external_host: "localhost"
  internal_port: 8767
  docker_host_port: 8768  # Change this for different port
  max_connections: 200    # Adjust capacity

active:
  environment: "production"     # Switch environments
  deployment_mode: "docker_in_docker"  # or "jenkins_direct"

environments:
  production:
    server:
      max_connections: 500  # Production-specific overrides
```

### Jenkins Configuration
Modify environment variables in `docker-compose.yml`:
```yaml
environment:
  - JAVA_OPTS=-Xmx4g  # Increase memory
  - JENKINS_OPTS=--prefix=/jenkins  # Add URL prefix
```

### Additional Services
Add new services to `docker-compose.yml`:
```yaml
services:
  database:
    image: postgres:15
    environment:
      POSTGRES_DB: gaming
    networks:
      - jenkins-network
```

## 📈 Monitoring

### Resource Usage
```bash
# Container resource usage
docker stats jenkins

# Disk usage
docker system df

# Clean unused resources
docker system prune -a
```

### Log Management
```bash
# View recent logs
docker-compose logs --tail 100 jenkins

# Follow logs real-time
docker-compose logs -f jenkins

# Export logs
docker-compose logs jenkins > jenkins.log
```

## 🚀 Production Considerations

### Security
```yaml
# Use secrets for sensitive data
secrets:
  jenkins_admin_password:
    external: true
environment:
  - JENKINS_ADMIN_PASSWORD_FILE=/run/secrets/jenkins_admin_password
```

### Backup
```bash
# Backup Jenkins data
docker run --rm -v dockers_jenkins_home:/data -v $(pwd):/backup alpine \
  tar czf /backup/jenkins-backup.tar.gz -C /data .

# Restore Jenkins data
docker run --rm -v dockers_jenkins_home:/data -v $(pwd):/backup alpine \
  tar xzf /backup/jenkins-backup.tar.gz -C /data
```

### Scaling
```yaml
# Resource limits
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2'
```

## 📞 Support

### Get Help
```bash
# Run verification script for diagnostics
docker-compose exec jenkins /usr/local/jenkins-tools/setup_jenkins_docker.sh

# Check Jenkins system info
# Navigate to: Jenkins → Manage Jenkins → System Information
```

### Reset Environment
```bash
# Complete reset (removes all data)
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

**Your Docker Jenkins environment is now ready! 🎮🐳**

Access Jenkins at http://localhost:8080 and create your pipeline job pointing to `jenkins/server_jenkinsfile`.