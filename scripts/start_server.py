#!/usr/bin/env python3
"""
Run the Tornado-based game server
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tornado_game_server import main

if __name__ == "__main__":
    main()