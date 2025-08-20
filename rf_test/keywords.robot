*** Settings ***
Documentation    All keywords for dice gambling game - consolidated and minimal
Library          libraries/GameClientLibrary.py
Library          Collections
Library          String
Library          DateTime

*** Keywords ***
# Authentication Keywords
Login With Valid Credentials
    [Documentation]    Login with valid user credentials
    [Arguments]    ${user_type}=default
    ${credentials}=    Get User Credentials    ${user_type}
    ${login_result}=    Login User    ${credentials}[username]    ${credentials}[password]
    Should Be Equal    ${login_result}[status]    success    Login failed
    Set Test Variable    ${SESSION_TOKEN}    ${login_result}[session_token]
    Set Test Variable    ${USER_ID}    ${login_result}[user_id]
    Set Test Variable    ${USER_BALANCE}    ${login_result}[balance]
    Set Test Variable    ${AUTH_RESULT}    ${login_result}
    Log    Login successful for user: ${credentials}[username]
    RETURN    ${login_result}

Login With Invalid Credentials
    [Documentation]    Attempt login with invalid credentials (should fail)
    [Arguments]    ${username}=invalid_user    ${password}=invalid_pass
    # This should raise an exception since GameClientLibrary throws exceptions on login failure
    ${status}    ${error}=    Run Keyword And Ignore Error    Login User    ${username}    ${password}
    Should Be Equal    ${status}    FAIL    Login should have failed but succeeded
    Log    Login correctly failed for invalid credentials: ${username}
    RETURN    ${status}

Perform User Authentication
    [Documentation]    Perform complete user authentication
    [Arguments]    ${user_type}=default
    ${login_result}=    Login With Valid Credentials    ${user_type}
    Verify Authentication State
    Log    User authentication completed for type: ${user_type}
    RETURN    ${login_result}

Verify Authentication State
    [Documentation]    Verify that user is properly authenticated
    Should Not Be Empty    ${SESSION_TOKEN}    Session token not available
    Should Not Be Equal As Integers    ${USER_ID}    0    User ID not available
    Should Be True    ${USER_BALANCE} >= 0    Invalid user balance: ${USER_BALANCE}
    Log    Authentication state verified: User ${USER_ID}, Balance ${USER_BALANCE}

# Game Keywords
Join Default Game Room
    [Documentation]    Join the default dice game room
    ${room_data}=    Get Room Data    room_1
    ${join_result}=    Join Game Room    ${room_data}[room_id]
    Should Be Equal    ${join_result}[status]    success    Failed to join room
    Set Test Variable    ${CURRENT_ROOM}    ${room_data}[room_id]
    Set Test Variable    ${ROOM_RESULT}    ${join_result}
    Log    Successfully joined room: ${room_data}[name]
    RETURN    ${join_result}

Join Specific Game Room
    [Documentation]    Join a specific game room by type
    [Arguments]    ${room_type}=room_1
    ${room_data}=    Get Room Data    ${room_type}
    ${join_result}=    Join Game Room    ${room_data}[room_id]
    Should Be Equal    ${join_result}[status]    success    Failed to join room
    Set Test Variable    ${CURRENT_ROOM}    ${room_data}[room_id]
    Set Test Variable    ${ROOM_RESULT}    ${join_result}
    Log    Successfully joined room: ${room_data}[name] (ID: ${room_data}[room_id])
    RETURN    ${join_result}

Get Game Snapshot
    [Documentation]    Retrieve current game state
    ${snapshot}=    GameClientLibrary.Get Game Snapshot
    Should Be True    ${snapshot}[round_status] >= 0    Failed to get snapshot: ${snapshot}[round_status]
    Set Test Variable    ${GAME_SNAPSHOT}    ${snapshot}
    ${status}    ${room_var}=    Run Keyword And Ignore Error    Variable Should Exist    ${CURRENT_ROOM}
    ${room_info}=    Set Variable If    '${status}' == 'PASS'    ${CURRENT_ROOM}    ${snapshot}[current_room]
    Log    Game snapshot retrieved for room: ${room_info}
    RETURN    ${snapshot}

Retrieve Game State
    [Documentation]    Alias for Get Game Snapshot for compatibility
    ${snapshot}=    Get Game Snapshot
    RETURN    ${snapshot}

Place Valid Dice Bet
    [Documentation]    Place a valid dice bet
    [Arguments]    ${dice_face}    ${amount}    ${round_id}=${None}
    Should Be True    1 <= ${dice_face} <= 6    Invalid dice face: ${dice_face}
    Should Be True    ${amount} > 0    Invalid bet amount: ${amount}
    
    ${bet_result}=    Place Bet    ${dice_face}    ${amount}    ${round_id}
    Should Be Equal    ${bet_result}[status]    success    Bet failed
    Set Test Variable    ${CURRENT_BET_ID}    ${bet_result}[bet_id]
    Set Test Variable    ${CURRENT_ROUND_ID}    ${bet_result}[round_id]
    Set Test Variable    ${BET_RESULT}    ${bet_result}
    Log    Bet placed: ${amount} on dice face ${dice_face}
    RETURN    ${bet_result}

Finish Current Betting Round
    [Documentation]    Finish the current betting round
    [Arguments]    ${round_id}=${CURRENT_ROUND_ID}
    ${finish_result}=    Finish Betting    ${round_id}
    Should Be Equal    ${finish_result}[status]    success    Failed to finish betting
    Log    Betting round finished: ${round_id}
    RETURN    ${finish_result}

Get Dice Game Result
    [Documentation]    Get the result of dice game
    [Arguments]    ${round_id}=${CURRENT_ROUND_ID}
    ${result}=    Get Game Result    ${round_id}
    Should Contain    ${result}    dice_result    Failed to get valid result
    Set Test Variable    ${GAME_RESULT}    ${result}
    
    # Log the game outcome
    ${dice_result}=    Set Variable    ${result}[dice_result]
    ${winnings}=    Set Variable    ${result}[total_winnings]
    Log    Game result: Dice rolled ${dice_result}, Winnings: ${winnings}
    RETURN    ${result}

Complete Dice Game Round
    [Documentation]    Complete a full dice game round
    [Arguments]    ${dice_face}    ${amount}    ${room_type}=room_1
    
    # Join room and get snapshot
    Join Specific Game Room    ${room_type}
    Get Game Snapshot
    
    # Place bet and finish round
    ${bet_result}=    Place Valid Dice Bet    ${dice_face}    ${amount}
    ${finish_result}=    Finish Current Betting Round
    ${game_result}=    Get Dice Game Result
    
    Log    Complete round finished: Bet ${amount} on ${dice_face}, Result: ${game_result}[dice_result]
    RETURN    ${game_result}

Perform Full Game Round
    [Documentation]    Perform complete game workflow from connection to result
    [Arguments]    ${user_type}=default    ${dice_face}=3    ${amount}=10    ${room_type}=room_1
    
    # If not already authenticated and in room, do full setup
    ${auth_status}    ${result}=    Run Keyword And Ignore Error    Variable Should Exist    ${SESSION_TOKEN}
    IF    '${auth_status}' == 'FAIL'
        # Complete authentication and room joining
        Perform User Authentication    ${user_type}
        Join Specific Game Room    ${room_type}
    END
    
    # Execute betting round (just the betting part, assuming we're already in a room)
    Get Game Snapshot
    ${bet_result}=    Place Valid Dice Bet    ${dice_face}    ${amount}
    ${finish_result}=    Finish Current Betting Round
    ${game_result}=    Get Dice Game Result
    
    Log    Full game round completed: Bet ${amount} on ${dice_face}, Result: ${game_result}[dice_result]
    RETURN    ${game_result}

# Utility Keywords
Get User Credentials
    [Documentation]    Get user credentials by type
    [Arguments]    ${user_type}=default
    
    IF    '${user_type}' == 'default'
        RETURN    &{DEFAULT_USER}
    ELSE IF    '${user_type}' == 'high_roller'
        RETURN    &{HIGH_ROLLER_USER}
    ELSE IF    '${user_type}' == 'basic_user'
        RETURN    &{BASIC_USER_DATA}
    ELSE IF    '${user_type}' == 'admin_user'
        RETURN    &{ADMIN_USER_DATA}
    ELSE
        Fail    User type '${user_type}' not found
    END

Get Room Data
    [Documentation]    Get room configuration by type (Server has 10 rooms: 1-10)
    [Arguments]    ${room_type}=room_1
    
    IF    '${room_type}' == 'room_1' or '${room_type}' == '1'
        RETURN    &{ROOM_1_DATA}
    ELSE IF    '${room_type}' == 'room_2' or '${room_type}' == '2'
        RETURN    &{ROOM_2_DATA}
    ELSE IF    '${room_type}' == 'room_3' or '${room_type}' == '3'
        RETURN    &{ROOM_3_DATA}
    ELSE IF    '${room_type}' == 'room_4' or '${room_type}' == '4'
        RETURN    &{ROOM_4_DATA}
    ELSE IF    '${room_type}' == 'room_5' or '${room_type}' == '5'
        RETURN    &{ROOM_5_DATA}
    ELSE IF    '${room_type}' == 'room_6' or '${room_type}' == '6'
        RETURN    &{ROOM_6_DATA}
    ELSE IF    '${room_type}' == 'room_7' or '${room_type}' == '7'
        RETURN    &{ROOM_7_DATA}
    ELSE IF    '${room_type}' == 'room_8' or '${room_type}' == '8'
        RETURN    &{ROOM_8_DATA}
    ELSE IF    '${room_type}' == 'room_9' or '${room_type}' == '9'
        RETURN    &{ROOM_9_DATA}
    ELSE IF    '${room_type}' == 'room_10' or '${room_type}' == '10'
        RETURN    &{ROOM_10_DATA}
    ELSE
        Fail    Room type '${room_type}' not found (valid rooms: 1-10)
    END

Generate Random Username
    [Documentation]    Generate a random username
    [Arguments]    ${prefix}=testuser
    
    ${random_suffix}=    Evaluate    ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))    modules=random,string
    ${username}=    Set Variable    ${prefix}_${random_suffix}
    Log    Generated random username: ${username}
    RETURN    ${username}

Establish Server Connection
    [Documentation]    Connect to dice game server
    [Arguments]    ${server_url}=${SERVER_URL}    ${timeout}=${CONNECTION_TIMEOUT}
    ${status}=    Connect To Game Server    ${server_url}    ${timeout}
    Should Be True    ${status}    Connection to server failed
    Log    Successfully connected to dice game server: ${server_url}
    RETURN    ${status}

Verify Connection Status
    [Documentation]    Verify that WebSocket connection is active
    ${status}=    Get Connection Status
    Should Be True    ${status}    WebSocket connection is not active
    Log    WebSocket connection to dice game server is active

Close Server Connection
    [Documentation]    Close server connection
    ${status}=    Disconnect From Server
    Should Be True    ${status}    Failed to disconnect from server
    Log    Successfully disconnected from dice game server

Connect To Game Server With Retry
    [Documentation]    Connect to dice game server with retry mechanism
    [Arguments]    ${server_url}=${SERVER_URL}    ${max_retries}=3    ${timeout}=${CONNECTION_TIMEOUT}
    FOR    ${retry}    IN RANGE    ${max_retries}
        ${status}=    Connect To Game Server    ${server_url}    ${timeout}
        Return From Keyword If    ${status}    ${status}
        Log    Connection attempt ${retry + 1} failed, retrying...
        Sleep    2s
    END
    Fail    Failed to connect after ${max_retries} attempts

Test Connection Stability
    [Documentation]    Test connection stability by checking status multiple times
    [Arguments]    ${check_count}=3
    FOR    ${i}    IN RANGE    ${check_count}
        Verify Connection Status
        Sleep    1s
    END
    Log    Connection stability test passed with ${check_count} checks

Validate Test Data Integrity
    [Documentation]    Validate that test data exists
    
    # Check if user data is available
    Should Not Be Empty    ${DEFAULT_USERNAME}    Default user data not available
    Should Not Be Empty    ${HIGH_ROLLER_USERNAME}    High roller user data not available
    Should Not Be Empty    ${BASIC_USER_USERNAME}    Basic user data not available
    
    # Check if room data is available
    Should Not Be Empty    ${ROOM_1_ID}    Room 1 data not available
    Should Not Be Empty    ${ROOM_2_ID}    Room 2 data not available
    Should Not Be Empty    ${ROOM_3_ID}    Room 3 data not available
    
    Log    Test data integrity check passed
    RETURN    ${True}