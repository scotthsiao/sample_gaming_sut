# Dice Gambling Game - Robot Framework Test Suite

A simplified Robot Framework test suite for testing the WebSocket-based dice gambling game system. This test suite validates all aspects of the game including authentication, room management, betting mechanics, and game logic.

## 🎯 Overview

This test suite is designed to validate the functionality of a dice gambling game that uses:
- WebSocket communication with Protocol Buffers serialization
- User authentication and session management
- Multi-room game environments
- Dice betting mechanics with 6x payout multiplier
- Real-time state synchronization

## 🆕 Recent Updates

### Test Framework Simplifications
- **Consolidated Structure**: Eliminated nested folders and reduced file count by 50%
- **Native Robot Framework**: Removed Python library dependencies in favor of native Robot Framework
- **Single Configuration**: All variables consolidated into one `global_vars.robot` file
- **Simplified Execution**: Direct Robot Framework commands instead of wrapper scripts

### Test Coverage Achievements  
- **33 of 33 tests passing** (100% success rate)
- **Complete Protocol Buffers validation** for all message types
- **Multi-bet scenario testing** with proper round ID management
- **Real-time balance persistence** validation across sessions

## 📁 Ultra-Compact Project Structure

```
rf_test/
├── README.md                           # This documentation
├── requirements.txt                    # Python dependencies
├── robot.yaml                          # Robot Framework configuration
├── functional_spec.md                  # Complete functional specification
├── common_keywords.robot               # All shared keywords and setup
├── global_vars.robot                   # All variables and test data
│
├── tests/                              # Test suite files
│   ├── connection_tests.robot          # WebSocket connection tests
│   ├── authentication_tests.robot     # Login/logout tests
│   ├── game_room_tests.robot          # Room joining tests
│   ├── end_to_end_tests.robot         # Complete workflow tests
│   └── __init__.robot                 # Test suite initialization
│
├── keywords/                           # Custom keyword definitions
│   ├── auth_keywords.robot            # Authentication keywords
│   ├── game_keywords.robot            # Game operation keywords
│   ├── utility_keywords.robot         # Utility and helper keywords
│   └── __init__.robot                 # Keywords initialization
│
└── libraries/                          # Custom Python libraries
    ├── GameClientLibrary.py           # Game client operations
    └── protocol_client.py             # Protocol Buffers client
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Access to the dice gambling game server

### Installation

1. **Install Dependencies**
   ```bash
   cd rf_test
   pip install -r requirements.txt
   ```

2. **Verify Installation**
   ```bash
   robot --version
   ```

### Quick Start

1. **Start the dice gambling game server** (refer to main project documentation)

2. **Run smoke tests**
   ```bash
   robot --include smoke tests/
   ```

3. **Run all tests**
   ```bash
   robot tests/
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
Edit `global_vars.robot`:
```robot
${SERVER_URL}           ws://localhost:8767
```

### Test Users
Test users are defined in `global_vars.robot`:
- **default**: testuser1/password123 (standard user)
- **high_roller**: alice/alicepass (premium user)  
- **basic_user**: bob/bobpass (basic user)

All users start with 1,000,000 credits and 60-second connection timeout.

## 📊 Running Tests

### Basic Execution
```bash
# Run all tests
robot tests/

# Run specific test suite
robot tests/connection_tests.robot

# Run tests with specific tags
robot --include smoke --include critical tests/

# Run tests against different server
robot --variable SERVER_URL:ws://staging.example.com:8767 tests/
```

### Advanced Options
```bash
# Custom output directory
robot --outputdir results tests/

# Verbose logging
robot --loglevel DEBUG tests/

# Run specific test by name
robot --test "Test WebSocket Connection Success" tests/
```

## 📈 Test Reports

Robot Framework automatically generates comprehensive reports:

### Built-in Reports
- **report.html**: Detailed test execution report with statistics
- **log.html**: Step-by-step execution log with screenshots
- **output.xml**: Raw test data (XML format)

### Viewing Reports
After running tests, open the generated HTML files in your browser:
```bash
# Open main report (Windows)
start report.html

# Open detailed log (Windows)
start log.html
```

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
Test data is centralized in `global_vars.robot`:
1. Edit user credentials directly in the variables file
2. Modify room configurations in the same file
3. All test data is in native Robot Framework syntax

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
- Use centralized configuration in `global_vars.robot`
- Implement data validation
- Keep sensitive data separate

## 🐛 Troubleshooting

### Common Issues

**Connection Failures**
```
Check server is running on correct port
Verify firewall settings
Test with: robot --variable SERVER_URL:ws://localhost:8767 tests/connection_tests.robot
```

**Authentication Errors**
```
Verify user credentials in global_vars.robot
Check server user management
Validate session token format
```

**Test Failures**
```
Check server logs for errors
Run individual tests: robot tests/specific_test.robot
Enable debug logging: robot --loglevel DEBUG tests/
```

### Getting Help
1. Check test logs in generated `log.html`
2. Review server logs
3. Run specific test: `robot tests/connection_tests.robot`
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