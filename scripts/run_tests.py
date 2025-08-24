#!/usr/bin/env python3
"""
Main entry point for running tests
"""
import sys
import os

# Add current directory to path for protobuf imports
sys.path.insert(0, os.path.dirname(__file__))

from tests.test_game_system import run_all_tests

if __name__ == "__main__":
    print("Running comprehensive test suite for gaming system...")
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)