#!/bin/bash

# Jenkins Agent Setup Script for sample_gaming_sut
# This script prepares a Jenkins agent with all required dependencies

echo "🔧 Setting up Jenkins Agent for sample_gaming_sut"
echo "=================================================="

# Function to detect OS and WSL
detect_os() {
    # Check if running in WSL
    if grep -qi microsoft /proc/version 2>/dev/null || grep -qi wsl /proc/version 2>/dev/null; then
        echo "🔍 WSL (Windows Subsystem for Linux) detected"
        
        # Determine WSL distribution
        if [ -f /etc/debian_version ]; then
            echo "wsl-ubuntu"
        elif [ -f /etc/redhat-release ]; then
            echo "wsl-rhel"
        else
            echo "wsl-linux"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "ubuntu"
        elif [ -f /etc/redhat-release ]; then
            echo "rhel"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to install Python on different systems
install_python() {
    local os=$1
    
    echo "📦 Installing Python 3..."
    
    case $os in
        "ubuntu"|"wsl-ubuntu")
            echo "Installing Python on Ubuntu/WSL Ubuntu..."
            if [[ $os == "wsl-ubuntu" ]]; then
                echo "⚠️  WSL detected: Some packages may require Windows interop"
            fi
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv python3-dev
            ;;
        "rhel"|"wsl-rhel")
            echo "Installing Python on RHEL/WSL RHEL..."
            if [[ $os == "wsl-rhel" ]]; then
                echo "⚠️  WSL detected: Some packages may require Windows interop"
            fi
            sudo yum install -y python3 python3-pip python3-devel
            # For RHEL 8+
            sudo dnf install -y python3 python3-pip python3-devel 2>/dev/null || true
            ;;
        "linux"|"wsl-linux")
            echo "Installing Python on generic Linux/WSL..."
            if [[ $os == "wsl-linux" ]]; then
                echo "⚠️  WSL detected: Manual installation may be required"
                echo "Please install Python 3.8+ using your distribution's package manager:"
                echo "  - Debian/Ubuntu: sudo apt-get install python3 python3-pip python3-venv"
                echo "  - RHEL/CentOS: sudo yum install python3 python3-pip"
                echo "  - Fedora: sudo dnf install python3 python3-pip"
                exit 1
            fi
            echo "❌ Generic Linux detected. Please install Python 3.8+ manually."
            exit 1
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                brew install python@3.11
            else
                echo "❌ Homebrew not found. Please install Homebrew first:"
                echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        *)
            echo "❌ Unsupported OS: $os. Please install Python 3.8+ manually."
            exit 1
            ;;
    esac
}

# Function to install Protocol Buffers compiler
install_protobuf() {
    local os=$1
    
    echo "📦 Installing Protocol Buffers compiler..."
    
    case $os in
        "ubuntu"|"wsl-ubuntu")
            echo "Installing protobuf on Ubuntu/WSL Ubuntu..."
            sudo apt-get install -y protobuf-compiler
            ;;
        "rhel"|"wsl-rhel")
            echo "Installing protobuf on RHEL/WSL RHEL..."
            sudo yum install -y protobuf-compiler
            # For RHEL 8+
            sudo dnf install -y protobuf-compiler 2>/dev/null || true
            ;;
        "linux"|"wsl-linux")
            if [[ $os == "wsl-linux" ]]; then
                echo "⚠️  WSL detected: Please install protobuf manually:"
                echo "  - Debian/Ubuntu: sudo apt-get install protobuf-compiler"
                echo "  - RHEL/CentOS: sudo yum install protobuf-compiler"
                echo "  - Fedora: sudo dnf install protobuf-compiler"
                exit 1
            fi
            echo "❌ Generic Linux: Please install protobuf-compiler manually"
            exit 1
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                brew install protobuf
            else
                echo "❌ Homebrew not found for protobuf installation"
                exit 1
            fi
            ;;
        *)
            echo "❌ Unsupported OS: $os"
            echo "Please install protobuf-compiler manually"
            exit 1
            ;;
    esac
}

# Function to verify installations
verify_installation() {
    echo "🔍 Verifying installations..."
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version)
        echo "✅ Python found: $PYTHON_VERSION"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_VERSION=$(python --version)
        if echo "$PYTHON_VERSION" | grep -q "Python 3"; then
            echo "✅ Python found: $PYTHON_VERSION"
        else
            echo "❌ Python 3 required, found: $PYTHON_VERSION"
            return 1
        fi
    else
        echo "❌ Python not found"
        return 1
    fi
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1; then
        echo "✅ pip3 found: $(pip3 --version)"
    elif command -v pip >/dev/null 2>&1; then
        echo "✅ pip found: $(pip --version)"
    else
        echo "❌ pip not found"
        return 1
    fi
    
    # Check protoc
    if command -v protoc >/dev/null 2>&1; then
        echo "✅ protoc found: $(protoc --version)"
    else
        echo "❌ protoc not found"
        return 1
    fi
    
    # Check venv module
    if python3 -m venv --help >/dev/null 2>&1 || python -m venv --help >/dev/null 2>&1; then
        echo "✅ venv module available"
    else
        echo "❌ venv module not available"
        return 1
    fi
    
    return 0
}

# Main execution
main() {
    echo "Starting Jenkins agent setup..."
    
    # Detect operating system
    OS=$(detect_os)
    echo "🔍 Detected OS: $OS"
    
    # Check if tools are already installed
    echo "🔍 Checking existing installations..."
    
    PYTHON_MISSING=false
    PROTOC_MISSING=false
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
        echo "⚠️  Python not found"
        PYTHON_MISSING=true
    elif command -v python >/dev/null 2>&1; then
        PYTHON_VERSION=$(python --version 2>&1)
        if ! echo "$PYTHON_VERSION" | grep -q "Python 3"; then
            echo "⚠️  Python 3 required, found: $PYTHON_VERSION"
            PYTHON_MISSING=true
        fi
    fi
    
    # Check protoc
    if ! command -v protoc >/dev/null 2>&1; then
        echo "⚠️  Protocol Buffers compiler not found"
        PROTOC_MISSING=true
    fi
    
    # Install missing components
    if [ "$PYTHON_MISSING" = true ]; then
        install_python $OS
    else
        echo "✅ Python already installed"
    fi
    
    if [ "$PROTOC_MISSING" = true ]; then
        install_protobuf $OS
    else
        echo "✅ Protocol Buffers compiler already installed"
    fi
    
    # Verify everything is working
    if verify_installation; then
        echo ""
        echo "🎉 Jenkins agent setup completed successfully!"
        echo "=================================================="
        echo ""
        echo "The agent is now ready to run the sample_gaming_sut pipeline."
        echo ""
        echo "Available commands:"
        echo "  - Python: $(which python3 || which python)"
        echo "  - pip: $(which pip3 || which pip)"
        echo "  - protoc: $(which protoc)"
        echo ""
        echo "You can now run the Jenkins pipeline with actions:"
        echo "  - start: Pull code and start server"
        echo "  - stop: Stop running server"
        echo "  - restart: Restart with latest code"
        echo "  - status: Check server status"
        echo ""
    else
        echo ""
        echo "❌ Setup failed! Some components are missing."
        echo "Please check the error messages above and install missing dependencies manually."
        exit 1
    fi
}

# Run main function
main "$@"