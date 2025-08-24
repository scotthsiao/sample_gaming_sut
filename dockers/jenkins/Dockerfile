# Jenkins Docker Image with Python and Protocol Buffers Support
# For sample_gaming_sut project automation

FROM jenkins/jenkins:lts

# Switch to root to install packages
USER root

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3.11

# Update package lists and install dependencies
RUN apt-get update && apt-get install -y \
    # Python and development tools
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # Protocol Buffers compiler
    protobuf-compiler \
    # Build tools
    build-essential \
    # Network tools for debugging
    curl \
    wget \
    netcat-openbsd \
    # Git (usually included but ensure it's there)
    git \
    # Docker CLI (for Docker-in-Docker scenarios)
    docker.io \
    # Additional useful tools
    vim \
    nano \
    htop \
    screen \
    at \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python command (some scripts might use 'python')
RUN ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip and install common Python packages (bypass external management for Docker)
RUN python3 -m pip install --break-system-packages --upgrade pip
RUN python3 -m pip install --break-system-packages \
    wheel \
    setuptools \
    virtualenv \
    # Common packages for the gaming project
    tornado \
    websockets \
    protobuf \
    bcrypt \
    python-dateutil

# Create a directory for Jenkins tools and scripts
RUN mkdir -p /usr/local/jenkins-tools
COPY setup_jenkins_docker.sh /usr/local/jenkins-tools/
RUN chmod +x /usr/local/jenkins-tools/*

# Create workspace directory with proper permissions
RUN mkdir -p /opt/sample_gaming_sut && chown jenkins:jenkins /opt/sample_gaming_sut

# Verify installations
RUN python3 --version \
    && pip3 --version \
    && protoc --version \
    && echo "All tools installed successfully"

# Add jenkins user to docker group
RUN usermod -aG docker jenkins || groupadd docker && usermod -aG docker jenkins

# Switch back to jenkins user
USER jenkins

# Install recommended Jenkins plugins
RUN jenkins-plugin-cli --plugins \
    git \
    workflow-aggregator \
    pipeline-stage-view \
    build-timeout \
    timestamper \
    ws-cleanup \
    docker-workflow \
    github \
    blueocean

# Create initial directories with proper permissions
RUN mkdir -p /var/jenkins_home/workspace

# Expose Jenkins port
EXPOSE 8080 50000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/login || exit 1

# Labels for image identification
LABEL maintainer="sample_gaming_sut" \
      description="Jenkins with Python 3 and Protocol Buffers for sample_gaming_sut" \
      python.version="3.11" \
      protobuf.installed="true" \
      docker.support="true"