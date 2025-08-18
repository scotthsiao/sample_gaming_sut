#!/usr/bin/env python3
"""
Test execution script for the dice gambling game Robot Framework test suite.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def run_command(command, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    project_root = get_project_root()
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"Requirements file not found: {requirements_file}")
        return False
    
    returncode, stdout, stderr = run_command([
        sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
    ])
    
    if returncode != 0:
        print(f"Failed to install dependencies: {stderr}")
        return False
    
    print("Dependencies installed successfully")
    return True


def run_robot_tests(test_suite=None, tags=None, variables=None, output_dir=None):
    """Run Robot Framework tests."""
    project_root = get_project_root()
    
    # Default output directory
    if not output_dir:
        output_dir = project_root / "results"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build robot command
    command = [
        "robot",
        "--outputdir", str(output_dir),
        "--loglevel", "INFO",
        "--report", "report.html",
        "--log", "log.html",
    ]
    
    # Add tags if specified
    if tags:
        for tag in tags:
            command.extend(["--include", tag])
    
    # Add variables if specified
    if variables:
        for var_name, var_value in variables.items():
            command.extend(["--variable", f"{var_name}:{var_value}"])
    
    # Add test suite or default to all tests
    if test_suite:
        test_path = project_root / "tests" / test_suite
        if not test_path.exists():
            print(f"Test suite not found: {test_path}")
            return False
        command.append(str(test_path))
    else:
        command.append(str(project_root / "tests"))
    
    # Run the tests
    print("Running Robot Framework tests...")
    returncode, stdout, stderr = run_command(command, cwd=project_root)
    
    # Print results
    print("\n" + "="*60)
    print("TEST EXECUTION COMPLETE")
    print("="*60)
    
    if stdout:
        print("STDOUT:")
        print(stdout)
    
    if stderr:
        print("STDERR:")
        print(stderr)
    
    print(f"\nTest results saved to: {output_dir}")
    print(f"Return code: {returncode}")
    
    # Robot Framework return codes:
    # 0: All tests passed
    # 1-249: Number of failed tests (max 249)
    # 250: 250 or more failures
    # 251: Help or version information printed
    # 252: Invalid test data or command line options
    # 253: Test execution stopped by user
    # 255: Unexpected internal error
    
    if returncode == 0:
        print("✅ All tests passed!")
    elif 1 <= returncode <= 250:
        print(f"❌ {returncode} test(s) failed")
    else:
        print(f"❌ Test execution error (code {returncode})")
    
    return returncode == 0


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Run dice gambling game Robot Framework tests"
    )
    
    parser.add_argument(
        "--suite", "-s",
        help="Specific test suite to run (e.g., connection_tests.robot)"
    )
    
    parser.add_argument(
        "--tags", "-t",
        nargs="+",
        help="Tags to include in test execution (e.g., smoke critical)"
    )
    
    parser.add_argument(
        "--install-deps", "-i",
        action="store_true",
        help="Install dependencies before running tests"
    )
    
    parser.add_argument(
        "--server-url",
        default="ws://localhost:8767",
        help="Dice game server URL (default: ws://localhost:8767)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for test results"
    )
    
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Test environment (default: dev)"
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            print("Failed to install dependencies")
            return 1
    
    # Prepare variables
    variables = {
        "SERVER_URL": args.server_url,
        "TEST_ENV": args.env,
    }
    
    # Convert output dir to Path if provided
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    # Run the tests
    success = run_robot_tests(
        test_suite=args.suite,
        tags=args.tags,
        variables=variables,
        output_dir=output_dir
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())