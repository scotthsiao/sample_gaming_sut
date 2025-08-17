*** Variables ***
# Development environment configuration

# Server Configuration
${SERVER_HOST}          localhost
${SERVER_PORT}          8080
${SERVER_URL}           ws://${SERVER_HOST}:${SERVER_PORT}/ws

# Environment Settings
${ENV_NAME}             dev
${DEBUG_MODE}           True
${LOG_LEVEL}            DEBUG

# Database Configuration (if needed)
${DB_HOST}              localhost
${DB_PORT}              5432
${DB_NAME}              game_test_db

# Test Configuration
${TIMEOUT}              30
${CONNECTION_TIMEOUT}   10
${RESPONSE_TIMEOUT}     5