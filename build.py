#!/usr/bin/env python3
"""
Build script for the Gaming System
"""
import subprocess
import sys
import os

def compile_protobuf():
    """Compile protocol buffer files"""
    proto_dir = "proto"
    proto_file = "game_messages.proto"
    proto_path = os.path.join(proto_dir, proto_file)
    
    if not os.path.exists(proto_path):
        print(f"Error: {proto_path} not found")
        return False
    
    try:
        cmd = ["protoc", "--python_out=.", "--pyi_out=.", proto_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully compiled {proto_path}")
            return True
        else:
            print(f"❌ Failed to compile {proto_path}")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ protoc command not found. Please install Protocol Buffers compiler:")
        print("  - Linux/Mac: apt-get install protobuf-compiler or brew install protobuf")
        print("  - Windows: Download from https://github.com/protocolbuffers/protobuf/releases")
        return False

def main():
    """Main build function"""
    print("Building Gaming System...")
    
    if compile_protobuf():
        print("✅ Build completed successfully!")
        return True
    else:
        print("❌ Build failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)