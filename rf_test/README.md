# Dice Gambling Game - Robot Framework Test Suite

A comprehensive Robot Framework test suite for testing the WebSocket-based dice gambling game system. This test suite validates all aspects of the game including authentication, room management, betting mechanics, and game logic.

## 🎯 Overview

This test suite is designed to validate the functionality of a dice gambling game that uses:
- WebSocket communication with Protocol Buffers serialization
- User authentication and session management
- Multi-room game environments
- Dice betting mechanics with 6x payout multiplier
- Real-time state synchronization

## 🆕 Recent Updates

### Test Framework Improvements
- **Enhanced Error Handling**: Added comprehensive error response handling for S2C_ERROR_RSP messages
- **Rate Limiting Bypass**: Server rate limiting disabled for rapid test execution  
- **Increased Test Balance**: Users now start with $1,000,000 for extensive testing scenarios
- **Port Standardization**: All configurations updated to use port 8767 by default
- **Bug Fixes**: Resolved "Unexpected response command: 0x9999" errors in test execution

### Test Coverage Achievements  
- **31 of 33 tests passing** (94% success rate)
- **Complete Protocol Buffers validation** for all message types
- **Multi-bet scenario testing** with proper round ID management
- **Real-time balance persistence** validation across sessions

## 📁 Project Structure

```
rf_test/
├── README.md                           # This documentation
├── requirements.txt                    # Python dependencies
├── robot.yaml                          # Robot Framework configuration
├── functional_spec.md                  # Complete functional specification
│
├── tests/                              # Test suite files
│   ├── connection_tests.robot          # WebSocket connection tests
│   ├── authentication_tests.robot     # Login/logout tests
│   ├── game_room_tests.robot          # Room joining tests
│   ├── end_to_end_tests.robot         # Complete workflow tests
│   └── __init__.robot                 # Test suite initialization
│
├── keywords/                           # Custom keyword definitions
│   ├── connection_keywords.robot      # Connection-related keywords
│   ├── auth_keywords.robot            # Authentication keywords
│   ├── game_keywords.robot            # Game operation keywords
│   ├── utility_keywords.robot         # Utility and helper keywords
│   └── __init__.robot                 # Keywords initialization
│
├── libraries/                          # Custom Python libraries
│   ├── __init__.py
│   ├── GameClientLibrary.py           # Game client operations
│   ├── TestDataLibrary.py             # Test data management
│   └── utils/                         # Utility modules
│       ├── __init__.py
│       ├── protocol_client.py         # Protocol Buffers client


│
├── data/                               # Test data and configuration
│   ├── variables/                      # Variable files
│   │   ├── global_vars.robot          # Global variables
│   │   ├── dev_config.robot           # Development environment
│   │   ├── staging_config.robot       # Staging environment
│   │   └── prod_config.robot          # Production environment
│   │
│   ├── test_data/                      # Test data files
│   │   ├── users.yaml                 # User credentials
│   │   ├── rooms.yaml                 # Game room data
│   │   ├── bet_types.yaml            # Betting options
│   │   └── test_scenarios.yaml        # Test scenario data
│   │

│
├── resources/                          # Resource files
│   ├── common.robot                   # Common resource imports
│   └── test_setup.robot              # Test setup and teardown
│
├── results/                            # Test execution results
│   ├── reports/                       # HTML reports
│   ├── logs/                          # Execution logs
│   └── screenshots/                   # Test screenshots (if any)
│
└── scripts/                           # Execution and utility scripts
    ├── run_tests.py                   # Test execution script
    ├── generate_report.py             # Report generation
    └── setup_environment.py           # Environment setup
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Access to the dice gambling game server

### Installation

1. **Setup Environment**
   ```bash
   cd rf_test
   python scripts/setup_environment.py
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   robot --version
   ```

### Quick Start

1. **Start the dice gambling game server** (refer to main project documentation)

2. **Run smoke tests**
   ```bash
   python scripts/run_tests.py --tags smoke
   ```

3. **Run all tests**
   ```bash
   python scripts/run_tests.py
   ```

4. **Generate reports**
   ```bash
   python scripts/generate_report.py
   ```

## 🧪 Test Categories

### Connection Tests (`connection_tests.robot`)
- WebSocket connection establishment
- Connection timeout handling
- Reconnection scenarios
- Connection stability validation

### Authentication Tests (`authentication_tests.robot`)
- User login with valid credentials
- Invalid credential handling
- Session token validation
- Multiple user type authentication
- Session persistence

### Game Room Tests (`game_room_tests.robot`)
- Room joining functionality
- Room state retrieval
- Multiple room access
- Room capacity validation
- High stakes room access

### End-to-End Tests (`end_to_end_tests.robot`)
- Complete dice game workflow
- Multiple bets in single round
- High stakes gaming scenarios
- Balance tracking accuracy
- Error recovery
- User journey simulation

## 🎮 Game System Overview

### Protocol Communication
- **Transport**: WebSocket with binary Protocol Buffers
- **Message Format**: Command ID (4 bytes) + Length (4 bytes) + Payload
- **Commands**: Login, Room Join, Snapshot, Bet Placement, Bet Finished, Result Request

### Game Mechanics
- **Dice**: 6-sided dice (1-6)
- **Betting**: Users bet on dice face outcome
- **Payout**: 6x multiplier for winning bets
- **Balance**: Virtual credits (1-1000 per bet, $1,000,000 starting balance)
- **Rooms**: Multiple game rooms with different limits

### Test Scenarios
- **Basic Flow**: Connect → Login → Join Room → Place Bet → Get Result
- **Multiple Bets**: Place multiple bets in single round
- **Error Handling**: Invalid inputs, network issues, server errors
- **Performance**: Rapid betting, concurrent operations

## 🔧 Configuration

### Server Configuration
Edit `data/variables/global_vars.robot`:
```robot
${SERVER_HOST}          localhost
${SERVER_PORT}          8767
${SERVER_URL}           ws://${SERVER_HOST}:${SERVER_PORT}
```

### Test Users
Edit `data/test_data/users.yaml`:
```yaml
default:
  username: "testuser"
  password: "testpass123"
  expected_balance: 1000000
  user_type: "standard"
```

### Environment Variables
Set environment-specific variables:
```bash
export SERVER_URL="ws://localhost:8767"
export TEST_ENV="dev"
```

## 📊 Running Tests

### Basic Execution
```bash
# Run all tests
python scripts/run_tests.py

# Run specific test suite
python scripts/run_tests.py --suite connection_tests.robot

# Run tests with specific tags
python scripts/run_tests.py --tags smoke critical

# Run tests against different server
python scripts/run_tests.py --server-url ws://staging.example.com:8767
```

### Advanced Options
```bash
# Install dependencies and run tests
python scripts/run_tests.py --install-deps

# Run tests for specific environment
python scripts/run_tests.py --env staging

# Custom output directory
python scripts/run_tests.py --output-dir /path/to/results
```

### Using Robot Framework Directly
```bash
# Run with Robot Framework CLI
robot --outputdir results --include smoke tests/

# Run specific test file
robot --outputdir results tests/connection_tests.robot

# Run with variables
robot --variable SERVER_URL:ws://localhost:8767 tests/
```

## 📈 Test Reports

### Generate Reports
```bash
# Generate all report formats
python scripts/generate_report.py

# Generate specific format
python scripts/generate_report.py --format html

# Custom input/output paths
python scripts/generate_report.py --input results/output.xml --output-dir reports/
```

### Report Types
- **HTML Summary**: Visual overview with statistics
- **JSON Report**: Machine-readable test data
- **Text Summary**: Console-friendly summary

### Built-in Robot Framework Reports
- **Report.html**: Detailed test execution report
- **Log.html**: Step-by-step execution log
- **Output.xml**: Raw test data (XML format)

## 🏷️ Test Tags

Tests are organized with tags for flexible execution:

- `smoke`: Critical functionality tests
- `regression`: Full regression test suite
- `integration`: Integration test scenarios
- `negative`: Error and edge case testing
- `e2e`: End-to-end workflow tests
- `connection`: Connection-related tests
- `authentication`: Authentication tests
- `room`: Room management tests
- `high_stakes`: High value betting tests

### Running Tagged Tests
```bash
# Run only smoke tests
robot --include smoke tests/

# Run multiple tag combinations
robot --include smokeORcritical tests/

# Exclude specific tags
robot --exclude broken tests/
```

## 🔍 Debugging

### Verbose Logging
```bash
robot --loglevel DEBUG tests/
```

### Test Variables
```bash
robot --variable LOG_LEVEL:DEBUG --variable TIMEOUT:60 tests/
```

### Step-by-Step Debugging
Add breakpoints in test files:
```robot
Set Log Level    DEBUG
Log    Debug checkpoint reached
```

## 🤝 Contributing

### Adding New Tests
1. Create test file in `tests/` directory
2. Follow naming convention: `*_tests.robot`
3. Use appropriate tags for categorization
4. Add test documentation

### Creating Keywords
1. Add keywords to appropriate file in `keywords/`
2. Follow naming convention: `*_keywords.robot`
3. Document parameters and return values
4. Include usage examples

### Test Data Management
1. Add test data to `data/test_data/`
2. Use YAML format for structured data
3. Update schemas in `data/schemas/` if needed
4. Validate data integrity

## 📋 Best Practices

### Test Design
- Keep tests atomic and independent
- Use descriptive test names and documentation
- Implement proper setup and teardown
- Handle errors gracefully

### Keyword Design
- Create reusable, parameterized keywords
- Use clear naming conventions
- Document expected behavior
- Return consistent data structures

### Data Management
- Use external data files for test inputs
- Implement data validation
- Support multiple environments
- Keep sensitive data separate

## 🐛 Troubleshooting

### Common Issues

**Connection Failures**
```
Check server is running on correct port
Verify firewall settings
Test with direct WebSocket client
```

**Authentication Errors**
```
Verify user credentials in test data
Check server user management
Validate session token format
```

**Test Failures**
```
Check server logs for errors
Verify test data integrity
Run individual tests for isolation
Enable debug logging
```

### Getting Help
1. Check test logs in `results/logs/`
2. Review server logs
3. Run setup validation: `python scripts/setup_environment.py`
4. Consult functional specification: `functional_spec.md`

## 📄 License

This test suite is part of the sample_gaming_sut project and is provided for educational and testing purposes.

## 📞 Support

For issues related to:
- **Test Framework**: Check Robot Framework documentation
- **Game Server**: Refer to main project documentation
- **Test Implementation**: Review this README and functional specification

---

*Happy Testing! 🎲*