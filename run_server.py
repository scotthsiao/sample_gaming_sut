#!/usr/bin/env python3
"""
Main entry point for the game server
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())