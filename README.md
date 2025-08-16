# Gaming System - Dice Gambling Game

A real-time WebSocket-based dice gambling game system implemented in Python with Protocol Buffers.

## Features

- **Real-time Communication**: WebSocket-based client-server architecture
- **Protocol Buffers**: Efficient binary message serialization
- **Secure Authentication**: bcrypt password hashing and session management
- **Multi-room Support**: Join different game rooms with individual jackpot pools
- **Dice Gambling**: Place bets on six-sided dice outcomes with 6x payouts
- **Rate Limiting**: Built-in protection against spam and abuse
- **Comprehensive Testing**: Full test suite covering all components

## System Architecture

The system consists of several key components organized in a clean directory structure:

```
sample_gaming_sut/
├── proto/                     # Protocol Buffer definitions
│   └── game_messages.proto    # Message definitions for client-server communication
├── src/                       # Source code
│   ├── models.py              # Data models for users, rooms, game rounds, and bets
│   ├── game_engine.py         # Core game logic and state management
│   ├── tornado_game_server.py # Primary WebSocket server using Tornado
│   ├── game_server.py         # Alternative WebSocket server using websockets library
│   └── game_client.py         # Client implementation with interactive and demo modes
├── tests/                     # Test suite
│   ├── test_game_system.py    # Comprehensive unittest test suite
│   └── test_game_system_pytest.py # Pytest version of test suite
├── run_tornado_server.py      # Primary server entry point (Tornado-based)
├── run_server.py              # Alternative server entry point (websockets-based)
├── run_client.py              # Client entry point
├── run_tests.py               # Test runner entry point
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Protocol Buffers compiler (`protoc`)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd sample_gaming_sut
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Compile Protocol Buffers**:
   ```bash
   protoc --python_out=. --pyi_out=. proto/game_messages.proto
   ```

4. **Verify installation**:
   ```bash
   python run_tests.py
   ```

## Quick Start

### Running the Server

**Primary Server (Tornado-based):**
```bash
# Basic server startup (runs on port 8767 by default)
python run_tornado_server.py

# With custom configuration
python run_tornado_server.py --host 0.0.0.0 --port 8767 --max-connections 200
```

**Alternative Server (websockets-based):**
```bash
# Basic server startup (runs on port 8765 by default)
python run_server.py

# With custom configuration
python run_server.py --host 0.0.0.0 --port 8765 --max-connections 200
```

**Server Comparison:**

| Feature | Tornado Server (Primary) | Websockets Server |
|---------|---------------------------|-------------------|
| Port | 8767 (default) | 8765 (default) |
| Payout Calculation | ✅ Fixed and working correctly | ✅ Working correctly |
| Event Loop Handling | ✅ Proper async integration | ✅ Good |
| Shutdown (Ctrl+C) | ✅ Works reliably | ✅ Works reliably |
| Client Compatibility | ✅ Full compatibility | ✅ Full compatibility |
| Production Ready | ✅ Yes | ✅ Yes |
| Performance | ✅ Good | ✅ Good |

**Why use the Tornado server?**
The Tornado-based server is the primary implementation with proper async event loop integration and has been thoroughly tested for reliability. Both servers now have correct payout calculations and proper shutdown handling.

**Stopping the Server:**
- Press `Ctrl+C` to gracefully shutdown the server
- On Windows: If Ctrl+C doesn't work, you can close the terminal window
- Alternative: Use Task Manager to end the Python process if needed

### Running the Client

```bash
# Interactive mode (connects to primary Tornado server by default)
python run_client.py --interactive

# Automated demo (connects to primary Tornado server by default)
python run_client.py --demo

# Connect to custom server address (Tornado server)
python run_client.py --server ws://localhost:8767 --demo

# Connect to alternative websockets server
python run_client.py --server ws://localhost:8765 --demo
```

## Game Rules

### Dice Gambling Mechanics

- Players place bets on which face (1-6) a six-sided die will show
- Each bet costs the specified amount from the player's balance
- If the bet wins, the payout is 6x the bet amount
- If the bet loses, the player loses the bet amount
- 1% of total bets per round goes to the room's jackpot pool

### Betting Limits

- Minimum bet: $1
- Maximum bet: $1000
- Maximum 10 bets per round
- Players start with $1000 balance

### Game Flow

1. **Login**: Authenticate with username/password
2. **Join Room**: Enter a game room (1-10 available)
3. **Place Bets**: Bet on dice outcomes for the current round
4. **Finish Betting**: Signal end of betting phase
5. **Get Results**: Receive dice result and calculate winnings

## API Reference

### Client Commands

| Command | Description |
|---------|-------------|
| Login | Authenticate user credentials |
| Join Room | Enter a specific game room |
| Place Bet | Bet on dice outcome with round ID |
| Finish Betting | End betting phase for current round |
| Get Results | Calculate and receive game results |
| Get Snapshot | View current game state |

### Message Types

All messages use Protocol Buffers with binary serialization:

- `LoginRequest/Response`: User authentication
- `RoomJoinRequest/Response`: Room management
- `BetPlacementRequest/Response`: Bet placement with round ID
- `BetFinishedRequest/Response`: End betting phase with round ID
- `ReckonResultRequest/Response`: Game results with round ID
- `SnapshotRequest/Response`: Current state
- `ErrorResponse`: Error handling

## Configuration

### Environment Variables

```bash
# Server configuration (Tornado server - primary)
GAME_HOST=localhost
GAME_PORT=8767
GAME_MAX_CONNECTIONS=100
GAME_SESSION_TIMEOUT=1800

# Alternative server configuration (websockets server)
# GAME_PORT=8765

# Game settings
GAME_MAX_BETS_PER_ROUND=10
GAME_MIN_BET=1
GAME_MAX_BET=1000
GAME_DEFAULT_BALANCE=1000

# Client configuration
GAME_SERVER_URL=ws://localhost:8767
GAME_CONNECTION_TIMEOUT=10

# Logging
GAME_LOG_LEVEL=INFO
GAME_LOG_FILE=game_server.log
```

### Default Test Users

The system includes pre-configured test users:
- `testuser1` / `password123`
- `testuser2` / `password123`
- `alice` / `alicepass`
- `bob` / `bobpass`
- `charlie` / `charliepass`

## Development

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run unittest version
python -m unittest tests/test_game_system.py -v

# Run pytest version
pytest tests/test_game_system_pytest.py -v

# Run specific test categories
pytest tests/test_game_system_pytest.py::TestGameEngine -v
```

### Code Quality

```bash
# Format code
black src/ tests/ *.py

# Lint code
flake8 src/ tests/ *.py

# Type checking
mypy src/ tests/ *.py
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .[dev]
```

## Security Features

- **Password Hashing**: bcrypt with 12 rounds
- **Session Management**: UUID-based tokens with expiration
- **Rate Limiting**: 100 messages per minute per user
- **Input Validation**: Comprehensive validation of all user inputs
- **Connection Management**: Automatic cleanup of stale connections

## Monitoring and Logging

- **Structured Logging**: Detailed logs for all game events
- **Error Tracking**: Comprehensive error handling and reporting
- **Performance Monitoring**: Connection and game state metrics
- **Cleanup Tasks**: Automatic cleanup of expired sessions and stale rounds

## Production Deployment

### Docker Support

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN protoc --python_out=. --pyi_out=. proto/game_messages.proto
EXPOSE 8767
CMD ["python", "run_tornado_server.py", "--host", "0.0.0.0"]
```

### Performance Considerations

- Use `uvloop` for better performance on Linux/macOS
- Configure appropriate connection limits
- Monitor memory usage for long-running sessions
- Set up log rotation for production environments

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For issues and questions:
- Check the test suite for usage examples
- Review the functional specification document
- Open an issue on the repository
