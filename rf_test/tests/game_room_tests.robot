*** Settings ***
Documentation    Dice game room functionality test cases
Test Setup       Setup Game Room Test
Test Teardown    Cleanup Test Resources
Resource         ../resources/common.robot

*** Test Cases ***
Test Join Default Room
    [Documentation]    Test joining the default dice game room
    [Tags]    smoke    room
    ${room_result}=    Join Default Game Room
    Should Be Equal    ${room_result}[status]    success
    Should Be Equal As Numbers    ${room_result}[room_id]    1
    Log    Default dice game room joined successfully

Test Join Specific Room
    [Documentation]    Test joining a specific room by ID
    [Tags]    room    specific
    ${room_result}=    Join Specific Game Room    2
    Should Be Equal    ${room_result}[status]    success
    Should Be Equal As Numbers    ${room_result}[room_id]    2
    Log    Specific dice game room joined successfully

Test Join Nonexistent Room
    [Documentation]    Test joining a room that doesn't exist
    [Tags]    negative    room
    Run Keyword And Expect Error    *Failed to join room*
    ...    Join Game Room    999
    Log    Nonexistent room join correctly failed

Test Room State Retrieval
    [Documentation]    Test retrieving room state information
    [Tags]    room    state
    Join Default Game Room
    ${snapshot}=    Retrieve Game State
    Should Contain    ${snapshot}    user_balance
    Should Contain    ${snapshot}    current_room
    Should Contain    ${snapshot}    jackpot_pool
    Should Be True    ${snapshot}[current_room] == 1
    Log    Room state information retrieved successfully

Test Multiple Room Access
    [Documentation]    Test accessing multiple rooms in sequence
    [Tags]    room    multiple
    # Join first room
    ${room1}=    Join Specific Game Room    1
    ${snapshot1}=    Retrieve Game State
    Should Be Equal As Numbers    ${snapshot1}[current_room]    1
    
    # Join second room (should leave first)
    ${room2}=    Join Specific Game Room    2
    ${snapshot2}=    Retrieve Game State
    Should Be Equal As Numbers    ${snapshot2}[current_room]    2
    Log    Multiple room access handled correctly

Test Room Capacity Information
    [Documentation]    Test room capacity and player count information
    [Tags]    room    capacity
    ${room_result}=    Join Default Game Room
    Should Contain    ${room_result}    player_count
    Should Be True    ${room_result}[player_count] >= 1
    Log    Room capacity information verified

Test Join Room Without Authentication
    [Documentation]    Test joining room without being logged in
    [Tags]    negative    room    auth
    # Disconnect and reconnect without login
    Close Server Connection
    Establish Server Connection
    
    Run Keyword And Expect Error    *User must be logged in*
    ...    Join Game Room    1
    Log    Unauthenticated room join correctly blocked

Test High Stakes Room Access
    [Documentation]    Test access to high stakes rooms
    [Tags]    room    high_stakes
    # Login with high roller user for better access
    Close Server Connection
    Establish Server Connection
    Login With Valid Credentials    high_roller
    
    ${room_result}=    Join Specific Game Room    2
    Should Be Equal    ${room_result}[status]    success
    Log    High stakes room access verified

Test Room Jackpot Pool Information
    [Documentation]    Test that room jackpot pool information is provided
    [Tags]    room    jackpot
    ${room_result}=    Join Default Game Room
    Should Contain    ${room_result}    jackpot_pool
    Should Be True    ${room_result}[jackpot_pool] >= 0
    
    ${snapshot}=    Retrieve Game State
    Should Be True    ${snapshot}[jackpot_pool] >= 0
    Log    Room jackpot pool information verified

Test Room State Consistency
    [Documentation]    Test that room state remains consistent
    [Tags]    room    consistency
    Join Default Game Room
    ${snapshot1}=    Retrieve Game State
    Sleep    1s
    ${snapshot2}=    Retrieve Game State
    
    # Room should remain the same
    Should Be Equal As Numbers    ${snapshot1}[current_room]    ${snapshot2}[current_room]
    Log    Room state consistency verified

*** Keywords ***
Setup Game Room Test
    [Documentation]    Setup for game room tests
    Setup Test Environment
    Establish Server Connection
    Login With Valid Credentials    default