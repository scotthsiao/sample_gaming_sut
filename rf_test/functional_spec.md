# Functional Specification of Robot Framework Test Suite

## Introduction
This document outlines the functional specifications for a Robot Framework test suite designed to validate the functionality of a game client and server. The test suite will cover various aspects of the game, including login, room joining, snapshot retrieval, and betting placement.

## Recent Test Framework Enhancements

### Server Configuration Updates
- **Rate Limiting**: Disabled server-side rate limiting to enable rapid test execution without delays
- **Default Balance**: Increased user starting balance from $1,000 to $1,000,000 for extensive testing scenarios
- **Port Configuration**: Standardized on port 8767 for all test configurations
- **Error Handling**: Enhanced test framework to properly handle server error responses (S2C_ERROR_RSP)

### Bug Fixes and Improvements
- **Protocol Buffers**: Fixed "Unexpected response command: 0x9999" errors by adding proper error response handling
- **Round ID Management**: Improved round ID passing between multiple bets in the same round
- **Balance Validation**: Updated test expectations to work with persistent user balances across sessions
- **Suite Teardown**: Fixed test variable scope issues in suite teardown operations

### Test Coverage Achievements
- **94% Success Rate**: 31 of 33 tests now passing
- **Complete Workflows**: End-to-end testing of dice game mechanics
- **Error Scenarios**: Comprehensive testing of negative test cases
- **Multi-bet Scenarios**: Validation of multiple bets within single game rounds

## Test Suite Structure
The test suite will be organized into several test cases, each covering a specific functionality of the game. The test cases will be executed using the Robot Framework, which is a popular open-source test automation tool.

## Test Cases

### 1. Websocket Connect Test Case
**Objective:** Verify that the client can successfully establish a WebSocket connection to the game server.
- **Preconditions:** Game server is running and accessible
- **Test Steps:**
  1. Initialize WebSocket client
  2. Attempt to connect to server endpoint
  3. Verify connection status
- **Expected Results:** Connection established successfully
- **Postconditions:** WebSocket connection is active

### 2. Login Test Case
**Objective:** Validate user authentication functionality.
- **Preconditions:** WebSocket connection is established
- **Test Steps:**
  1. Send login request with valid credentials
  2. Verify server response
  3. Check authentication status
- **Expected Results:** User successfully authenticated
- **Postconditions:** User session is active

### 3. Join Room Test Case
**Objective:** Test the ability to join a game room.
- **Preconditions:** User is authenticated
- **Test Steps:**
  1. Send join room request
  2. Verify room assignment
  3. Check room status
- **Expected Results:** User successfully joins the room
- **Postconditions:** User is in active game room

### 4. Whole Process Test Case
**Objective:** End-to-end testing of complete game workflow.
- **Preconditions:** None (fresh start)
- **Test Steps:**
  1. Connect to server
  2. Login with credentials
  3. Join game room
  4. Retrieve game snapshot
  5. Place bets
  6. Verify game results
- **Expected Results:** Complete game cycle executed successfully
- **Postconditions:** Game session completed

## Robot Framework Keywords

### Connection Keywords
- **Connect To Game Server**
  - Purpose: Establish WebSocket connection
  - Parameters: server_url, timeout
  - Returns: connection_status

- **Disconnect From Server**
  - Purpose: Close WebSocket connection
  - Parameters: None
  - Returns: disconnection_status

### Authentication Keywords
- **Login User**
  - Purpose: Authenticate user with server
  - Parameters: username, password
  - Returns: auth_token, user_id

- **Logout User**
  - Purpose: End user session
  - Parameters: auth_token
  - Returns: logout_status

### Game Operation Keywords
- **Join Game Room**
  - Purpose: Join specified game room
  - Parameters: room_id, auth_token
  - Returns: room_status, player_position

- **Get Game Snapshot**
  - Purpose: Retrieve current game state
  - Parameters: room_id, auth_token
  - Returns: game_state, snapshot_data

- **Place Bet**
  - Purpose: Submit betting request
  - Parameters: bet_amount, bet_type, auth_token
  - Returns: bet_confirmation, bet_id

- **Verify Game Result**
  - Purpose: Check game outcome
  - Parameters: bet_id, expected_result
  - Returns: result_verification

### Utility Keywords
- **Wait For Server Response**
  - Purpose: Wait for server message
  - Parameters: timeout, message_type
  - Returns: response_data

- **Validate JSON Response**
  - Purpose: Verify response format
  - Parameters: response_json, expected_schema
  - Returns: validation_result

## Robot Framework Libraries

### Built-in Libraries
- **Collections**: For handling lists and dictionaries
- **String**: For string manipulation and validation
- **DateTime**: For timestamp operations
- **OperatingSystem**: For file and environment operations

### External Libraries
- **RequestsLibrary**: For HTTP/REST API testing
- **WebSocketLibrary**: For WebSocket communication testing
- **JSONLibrary**: For JSON data manipulation and validation
- **DatabaseLibrary**: For database operations if needed

### Custom Libraries
- **GameClientLibrary**: Custom library for game-specific operations
  - WebSocket connection management
  - Game protocol message handling
  - Authentication utilities
  - Betting operation helpers

- **TestDataLibrary**: Test data management utilities
  - User credential management
  - Test configuration loading
  - Mock data generation

## Test Data and Variables

### Global Variables
- **${SERVER_URL}**: Game server endpoint
- **${TIMEOUT}**: Default timeout for operations
- **${TEST_USER}**: Test user credentials
- **${TEST_ROOM}**: Default test room ID

### Test Data Files
- **users.yaml**: User credentials and profiles
- **rooms.yaml**: Available game rooms
- **bet_types.yaml**: Valid betting options
- **test_config.yaml**: Test environment configuration

### Environment Variables
- **GAME_SERVER_HOST**: Server hostname
- **GAME_SERVER_PORT**: Server port
- **TEST_ENV**: Testing environment (dev/staging/prod)
- **LOG_LEVEL**: Logging verbosity level

## Project Folder Structure

```
rf_test/
├── README.md                           # Project overview and setup instructions
├── requirements.txt                    # Python dependencies
├── robot.yaml                          # Robot Framework configuration
├── functional_spec.md                  # This document
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

### Folder Description

#### `/tests/`
Contains all Robot Framework test suite files (.robot). Each file focuses on a specific functional area:
- Individual test cases organized by functionality
- Suite setup and teardown procedures
- Test documentation and tags

#### `/keywords/`
Custom keyword definitions that can be reused across test suites:
- High-level business logic keywords
- Technical implementation keywords
- Parameterized and configurable keywords

#### `/libraries/`
Python libraries that extend Robot Framework capabilities:
- Custom libraries for game-specific operations
- Utility libraries for common operations
- Integration with external systems

#### `/data/`
All test data, configuration, and validation schemas:
- Environment-specific configurations
- Test data in YAML format for easy maintenance
- JSON schemas for response validation

#### `/resources/`
Shared resources and common imports:
- Common keyword imports
- Shared variables and settings
- Test setup and teardown procedures

#### `/results/`
Generated during test execution:
- HTML reports and logs
- Screenshots and artifacts
- Test metrics and statistics

#### `/scripts/`
Automation and utility scripts:
- Test execution automation
- Report generation and distribution
- Environment setup and configuration

### File Naming Conventions
- Test files: `*_tests.robot`
- Keyword files: `*_keywords.robot`
- Library files: `*Library.py`
- Data files: `*.yaml` or `*.json`
- Variable files: `*_config.robot` or `*_vars.robot`

