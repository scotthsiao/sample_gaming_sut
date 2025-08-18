*** Variables ***
# Global variables for dice gambling game test suite

# Server Configuration
${SERVER_HOST}          localhost
${SERVER_PORT}          8767
${SERVER_URL}           ws://${SERVER_HOST}:${SERVER_PORT}

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
${DEFAULT_BALANCE}      1000

# Retry Configuration
${MAX_RETRIES}          3
${RETRY_DELAY}          2s

# Dice Game Specific
@{DICE_FACES}           1    2    3    4    5    6
${WINNING_MULTIPLIER}   6
${JACKPOT_CONTRIBUTION}    0.01