*** Variables ***
# Global variables for dice gambling game test suite - consolidated from multiple files

# Server Configuration - Single server URL for all tests
${SERVER_URL}           ws://localhost:8767

# Test Configuration
${TIMEOUT}              30
${SHORT_TIMEOUT}        5
${LONG_TIMEOUT}         60
${CONNECTION_TIMEOUT}   10

# Game Configuration
${DEFAULT_ROOM_ID}      1
${MAX_BET_AMOUNT}       1000
${MIN_BET_AMOUNT}       1
${DEFAULT_BET_AMOUNT}   10
${DEFAULT_DICE_FACE}    3

# Test User Defaults
${TEST_USERNAME}        testuser
${TEST_PASSWORD}        testpass123
${DEFAULT_BALANCE}      1000000

# Retry Configuration
${MAX_RETRIES}          3
${RETRY_DELAY}          2s

# Dice Game Specific
@{DICE_FACES}           1    2    3    4    5    6
${WINNING_MULTIPLIER}   6
${JACKPOT_CONTRIBUTION}    0.01

# User Credentials - consolidated from test_users.robot
${DEFAULT_USERNAME}             testuser1
${DEFAULT_PASSWORD}             password123
${DEFAULT_EXPECTED_BALANCE}     ${1000000}
${DEFAULT_USER_TYPE}            standard

${HIGH_ROLLER_USERNAME}         alice
${HIGH_ROLLER_PASSWORD}         alicepass
${HIGH_ROLLER_EXPECTED_BALANCE}    ${1000000}
${HIGH_ROLLER_USER_TYPE}        premium

${BASIC_USER_USERNAME}          bob
${BASIC_USER_PASSWORD}          bobpass
${BASIC_USER_EXPECTED_BALANCE}    ${1000000}
${BASIC_USER_USER_TYPE}         basic

# User data dictionaries
&{DEFAULT_USER}         username=${DEFAULT_USERNAME}    password=${DEFAULT_PASSWORD}    expected_balance=${DEFAULT_EXPECTED_BALANCE}    user_type=${DEFAULT_USER_TYPE}
&{HIGH_ROLLER_USER}     username=${HIGH_ROLLER_USERNAME}    password=${HIGH_ROLLER_PASSWORD}    expected_balance=${HIGH_ROLLER_EXPECTED_BALANCE}    user_type=${HIGH_ROLLER_USER_TYPE}
&{BASIC_USER_DATA}      username=${BASIC_USER_USERNAME}    password=${BASIC_USER_PASSWORD}    expected_balance=${BASIC_USER_EXPECTED_BALANCE}    user_type=${BASIC_USER_USER_TYPE}

# Room Configurations - consolidated from test_rooms.robot
${ROOM_1_ID}            1
${ROOM_1_NAME}          Main Room
${ROOM_1_MAX_CAPACITY}  50
${ROOM_1_MIN_BET}       1
${ROOM_1_MAX_BET}       1000

${ROOM_2_ID}            2
${ROOM_2_NAME}          High Stakes Room
${ROOM_2_MAX_CAPACITY}  20
${ROOM_2_MIN_BET}       100
${ROOM_2_MAX_BET}       10000

${ROOM_3_ID}            3
${ROOM_3_NAME}          Beginner Room
${ROOM_3_MAX_CAPACITY}  100
${ROOM_3_MIN_BET}       1
${ROOM_3_MAX_BET}       50

# Room data dictionaries
&{ROOM_1_DATA}  room_id=${ROOM_1_ID}    name=${ROOM_1_NAME}    max_capacity=${ROOM_1_MAX_CAPACITY}    min_bet=${ROOM_1_MIN_BET}    max_bet=${ROOM_1_MAX_BET}
&{ROOM_2_DATA}  room_id=${ROOM_2_ID}    name=${ROOM_2_NAME}    max_capacity=${ROOM_2_MAX_CAPACITY}    min_bet=${ROOM_2_MIN_BET}    max_bet=${ROOM_2_MAX_BET}
&{ROOM_3_DATA}  room_id=${ROOM_3_ID}    name=${ROOM_3_NAME}    max_capacity=${ROOM_3_MAX_CAPACITY}    min_bet=${ROOM_3_MIN_BET}    max_bet=${ROOM_3_MAX_BET}