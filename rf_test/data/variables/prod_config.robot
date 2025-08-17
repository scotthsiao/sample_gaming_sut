*** Variables ***
# Production environment configuration

# Server Configuration
${SERVER_HOST}          prod.gameserver.com
${SERVER_PORT}          443
${SERVER_URL}           wss://${SERVER_HOST}:${SERVER_PORT}/ws

# Environment Settings
${ENV_NAME}             prod
${DEBUG_MODE}           False
${LOG_LEVEL}            WARN

# Database Configuration (if needed)
${DB_HOST}              prod-db.gameserver.com
${DB_PORT}              5432
${DB_NAME}              game_prod_db

# Test Configuration
${TIMEOUT}              60
${CONNECTION_TIMEOUT}   20
${RESPONSE_TIMEOUT}     15