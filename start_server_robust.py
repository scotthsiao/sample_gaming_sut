#!/usr/bin/env python3
"""
Robust server starter that creates a truly detached process
This uses Python's subprocess and process group isolation
"""

import os
import sys
import subprocess
import signal
import time
import argparse
from pathlib import Path

def create_detached_process(command, log_file, pid_file):
    """Create a completely detached process using subprocess"""
    
    print(f"Creating detached process: {' '.join(command)}")
    print(f"Log file: {log_file}")
    print(f"PID file: {pid_file}")
    
    try:
        # Create new session - this should isolate from Jenkins
        process = subprocess.Popen(
            command,
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,  # This creates new process group and session
            cwd=os.getcwd()
        )
        
        # Write PID to file
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print(f"✅ Server started with PID: {process.pid}")
        print(f"Process is detached and should survive parent termination")
        
        # Don't wait for the process - let it run independently
        return process.pid
        
    except Exception as e:
        print(f"❌ Failed to start detached process: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Start detached tornado server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--port', default='8767', help='Server port')
    parser.add_argument('--max-connections', default='200', help='Max connections')
    parser.add_argument('--log-file', default='tornado_server.log', help='Log file path')
    parser.add_argument('--pid-file', default='tornado_server.pid', help='PID file path')
    parser.add_argument('--server-script', default='run_tornado_server.py', help='Server script path')
    
    args = parser.parse_args()
    
    # Build command
    command = [
        sys.executable,  # Use same Python executable
        args.server_script,
        '--host', args.host,
        '--port', args.port,
        '--max-connections', args.max_connections
    ]
    
    # Create detached process
    pid = create_detached_process(command, args.log_file, args.pid_file)
    
    if pid:
        # Give process time to initialize
        time.sleep(2)
        
        # Verify it's still running
        try:
            os.kill(pid, 0)  # Just check if process exists
            print(f"✅ Process {pid} is running successfully")
            return 0
        except OSError:
            print(f"❌ Process {pid} died during startup")
            if os.path.exists(args.log_file):
                print("--- Log contents ---")
                with open(args.log_file, 'r') as f:
                    print(f.read())
            return 1
    else:
        print("❌ Failed to start server")
        return 1

if __name__ == '__main__':
    sys.exit(main())