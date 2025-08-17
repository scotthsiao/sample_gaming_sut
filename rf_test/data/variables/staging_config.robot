*** Variables ***
# Staging environment configuration

# Server Configuration
${SERVER_HOST}          staging.gameserver.com
${SERVER_PORT}          8080
${SERVER_URL}           wss://${SERVER_HOST}:${SERVER_PORT}/ws

# Environment Settings
${ENV_NAME}             staging
${DEBUG_MODE}           False
${LOG_LEVEL}            INFO

# Database Configuration (if needed)
${DB_HOST}              staging-db.gameserver.com
${DB_PORT}              5432
${DB_NAME}              game_staging_db

# Test Configuration
${TIMEOUT}              45
${CONNECTION_TIMEOUT}   15
${RESPONSE_TIMEOUT}     10