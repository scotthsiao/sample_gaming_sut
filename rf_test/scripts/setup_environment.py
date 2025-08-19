#!/usr/bin/env python3
"""
Environment setup script for the dice gambling game Robot Framework test suite.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def run_command(command, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"[OK] Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_pip():
    """Check if pip is available."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"[OK] pip available: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] pip not available")
        return False


def create_virtual_environment():
    """Create a virtual environment for the project."""
    project_root = get_project_root()
    venv_path = project_root / "venv"
    
    if venv_path.exists():
        print(f"[OK] Virtual environment already exists: {venv_path}")
        return True
    
    print("Creating virtual environment...")
    success = run_command([sys.executable, "-m", "venv", str(venv_path)])
    
    if success:
        print(f"[OK] Virtual environment created: {venv_path}")
        print("\nTo activate the virtual environment:")
        if os.name == 'nt':  # Windows
            print(f"  {venv_path / 'Scripts' / 'activate.bat'}")
        else:  # Unix/Linux/Mac
            print(f"  source {venv_path / 'bin' / 'activate'}")
        return True
    else:
        print("[ERROR] Failed to create virtual environment")
        return False


def install_requirements():
    """Install required packages."""
    project_root = get_project_root()
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"[ERROR] Requirements file not found: {requirements_file}")
        return False
    
    print("Installing requirements...")
    success = run_command([
        sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
    ])
    
    if success:
        print("[OK] Requirements installed successfully")
        return True
    else:
        print("[ERROR] Failed to install requirements")
        return False


def create_directories():
    """Create necessary directories."""
    project_root = get_project_root()
    
    directories = [
        "results",
        "results/reports",
        "results/logs", 
        "results/screenshots"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Directory created: {dir_path}")
    
    return True


def validate_test_data():
    """Validate that test data files exist and are valid."""
    project_root = get_project_root()
    
    required_files = [
        "data/test_data/users.yaml",
        "data/test_data/rooms.yaml", 
        "data/test_data/bet_types.yaml",
        "data/test_data/test_scenarios.yaml",
        "data/variables/global_vars.robot"
    ]
    
    all_valid = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"[OK] Test data file exists: {file_path}")
        else:
            print(f"[ERROR] Missing test data file: {file_path}")
            all_valid = False
    
    return all_valid


def validate_robot_framework():
    """Validate Robot Framework installation."""
    try:
        result = subprocess.run(["robot", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"[OK] Robot Framework: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Robot Framework not available")
        return False
    except FileNotFoundError:
        print("[ERROR] Robot Framework not found in PATH")
        return False


def setup_git_hooks():
    """Setup git hooks if .git directory exists."""
    project_root = get_project_root()
    git_dir = project_root.parent / ".git"  # Assuming rf_test is a subdirectory
    
    if not git_dir.exists():
        print("[INFO] No git repository found, skipping git hooks setup")
        return True
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # Create a simple pre-commit hook
    pre_commit_hook = hooks_dir / "pre-commit"
    hook_content = """#!/bin/sh
# Pre-commit hook for dice gambling game tests
echo "Running pre-commit checks..."

# Check if Robot Framework tests pass
if [ -f "rf_test/scripts/run_tests.py" ]; then
    echo "Running smoke tests..."
    python rf_test/scripts/run_tests.py --tags smoke
    if [ $? -ne 0 ]; then
        echo "Smoke tests failed. Commit aborted."
        exit 1
    fi
fi

echo "Pre-commit checks passed."
exit 0
"""
    
    with open(pre_commit_hook, 'w', encoding='utf-8') as f:
        f.write(hook_content)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod(pre_commit_hook, 0o755)
    
    print(f"[OK] Git pre-commit hook created: {pre_commit_hook}")
    return True


def main():
    """Main setup function."""
    print("=" * 60)
    print("DICE GAMBLING GAME TEST ENVIRONMENT SETUP")
    print("=" * 60)
    print()
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Check pip
    if not check_pip():
        success = False
    
    if not success:
        print("\n[ERROR] Environment setup failed due to missing prerequisites")
        return 1
    
    # Create directories
    print("\nCreating directories...")
    if not create_directories():
        success = False
    
    # Install requirements
    print("\nInstalling requirements...")
    if not install_requirements():
        success = False
    
    # Validate Robot Framework
    print("\nValidating Robot Framework...")
    if not validate_robot_framework():
        success = False
    
    # Validate test data
    print("\nValidating test data...")
    if not validate_test_data():
        success = False
    
    # Setup git hooks
    print("\nSetting up git hooks...")
    setup_git_hooks()  # This is optional, so don't fail if it doesn't work
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] ENVIRONMENT SETUP COMPLETED SUCCESSFULLY")
        print()
        print("Next steps:")
        print("1. Start the dice gambling game server")
        print("2. Run tests with: python scripts/run_tests.py")
        print("3. Generate reports with: python scripts/generate_report.py")
    else:
        print("[ERROR] ENVIRONMENT SETUP FAILED")
        print()
        print("Please fix the issues above and run the setup again.")
    
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())