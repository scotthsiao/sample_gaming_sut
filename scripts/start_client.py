#!/usr/bin/env python3
"""
Main entry point for the game client
"""
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.game_client import main

if __name__ == "__main__":
    asyncio.run(main())