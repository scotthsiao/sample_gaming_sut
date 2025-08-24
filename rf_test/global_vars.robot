*** Settings ***
# Import generated configuration (single source of truth)
Resource    generated_config.robot

*** Variables ***
# Global variables - ultra-minimal set for dice gambling game

# Note: SERVER_URL, TIMEOUT, CONNECTION_TIMEOUT are now imported from generated_config.robot
# To change these values, edit config.yaml and run: python config_loader.py --export-robot

# Test Environment
${DEFAULT_BALANCE}      1000000
${TEST_ENV}             dev

# User Credentials
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

# Room Configurations (Server creates 10 rooms, all with capacity 50)
${ROOM_1_ID}            1
${ROOM_1_NAME}          Room 1
${ROOM_1_MAX_CAPACITY}  50
${ROOM_1_MIN_BET}       1
${ROOM_1_MAX_BET}       1000

${ROOM_2_ID}            2
${ROOM_2_NAME}          Room 2
${ROOM_2_MAX_CAPACITY}  50
${ROOM_2_MIN_BET}       1
${ROOM_2_MAX_BET}       1000

${ROOM_3_ID}            3
${ROOM_3_NAME}          Room 3
${ROOM_3_MAX_CAPACITY}  50
${ROOM_3_MIN_BET}       1
${ROOM_3_MAX_BET}       1000

${ROOM_4_ID}            4
${ROOM_4_NAME}          Room 4
${ROOM_4_MAX_CAPACITY}  50
${ROOM_4_MIN_BET}       1
${ROOM_4_MAX_BET}       1000

${ROOM_5_ID}            5
${ROOM_5_NAME}          Room 5
${ROOM_5_MAX_CAPACITY}  50
${ROOM_5_MIN_BET}       1
${ROOM_5_MAX_BET}       1000

${ROOM_6_ID}            6
${ROOM_6_NAME}          Room 6
${ROOM_6_MAX_CAPACITY}  50
${ROOM_6_MIN_BET}       1
${ROOM_6_MAX_BET}       1000

${ROOM_7_ID}            7
${ROOM_7_NAME}          Room 7
${ROOM_7_MAX_CAPACITY}  50
${ROOM_7_MIN_BET}       1
${ROOM_7_MAX_BET}       1000

${ROOM_8_ID}            8
${ROOM_8_NAME}          Room 8
${ROOM_8_MAX_CAPACITY}  50
${ROOM_8_MIN_BET}       1
${ROOM_8_MAX_BET}       1000

${ROOM_9_ID}            9
${ROOM_9_NAME}          Room 9
${ROOM_9_MAX_CAPACITY}  50
${ROOM_9_MIN_BET}       1
${ROOM_9_MAX_BET}       1000

${ROOM_10_ID}            10
${ROOM_10_NAME}          Room 10
${ROOM_10_MAX_CAPACITY}  50
${ROOM_10_MIN_BET}       1
${ROOM_10_MAX_BET}       1000

# Room data dictionaries
&{ROOM_1_DATA}   room_id=${ROOM_1_ID}    name=${ROOM_1_NAME}    max_capacity=${ROOM_1_MAX_CAPACITY}    min_bet=${ROOM_1_MIN_BET}    max_bet=${ROOM_1_MAX_BET}
&{ROOM_2_DATA}   room_id=${ROOM_2_ID}    name=${ROOM_2_NAME}    max_capacity=${ROOM_2_MAX_CAPACITY}    min_bet=${ROOM_2_MIN_BET}    max_bet=${ROOM_2_MAX_BET}
&{ROOM_3_DATA}   room_id=${ROOM_3_ID}    name=${ROOM_3_NAME}    max_capacity=${ROOM_3_MAX_CAPACITY}    min_bet=${ROOM_3_MIN_BET}    max_bet=${ROOM_3_MAX_BET}
&{ROOM_4_DATA}   room_id=${ROOM_4_ID}    name=${ROOM_4_NAME}    max_capacity=${ROOM_4_MAX_CAPACITY}    min_bet=${ROOM_4_MIN_BET}    max_bet=${ROOM_4_MAX_BET}
&{ROOM_5_DATA}   room_id=${ROOM_5_ID}    name=${ROOM_5_NAME}    max_capacity=${ROOM_5_MAX_CAPACITY}    min_bet=${ROOM_5_MIN_BET}    max_bet=${ROOM_5_MAX_BET}
&{ROOM_6_DATA}   room_id=${ROOM_6_ID}    name=${ROOM_6_NAME}    max_capacity=${ROOM_6_MAX_CAPACITY}    min_bet=${ROOM_6_MIN_BET}    max_bet=${ROOM_6_MAX_BET}
&{ROOM_7_DATA}   room_id=${ROOM_7_ID}    name=${ROOM_7_NAME}    max_capacity=${ROOM_7_MAX_CAPACITY}    min_bet=${ROOM_7_MIN_BET}    max_bet=${ROOM_7_MAX_BET}
&{ROOM_8_DATA}   room_id=${ROOM_8_ID}    name=${ROOM_8_NAME}    max_capacity=${ROOM_8_MAX_CAPACITY}    min_bet=${ROOM_8_MIN_BET}    max_bet=${ROOM_8_MAX_BET}
&{ROOM_9_DATA}   room_id=${ROOM_9_ID}    name=${ROOM_9_NAME}    max_capacity=${ROOM_9_MAX_CAPACITY}    min_bet=${ROOM_9_MIN_BET}    max_bet=${ROOM_9_MAX_BET}
&{ROOM_10_DATA}  room_id=${ROOM_10_ID}   name=${ROOM_10_NAME}   max_capacity=${ROOM_10_MAX_CAPACITY}   min_bet=${ROOM_10_MIN_BET}   max_bet=${ROOM_10_MAX_BET}