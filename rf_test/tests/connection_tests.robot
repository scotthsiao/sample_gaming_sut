*** Settings ***
Documentation    WebSocket connection test cases for dice gambling game
Test Setup       Setup Test Environment
Test Teardown    Cleanup Test Resources
Resource         ../resources/common.robot

*** Test Cases ***
Test WebSocket Connection Success
    [Documentation]    Verify successful WebSocket connection to dice game server
    [Tags]    smoke    connection
    Establish Server Connection
    Verify Connection Status
    Log    WebSocket connection to dice game server established successfully

Test Connection With Invalid URL
    [Documentation]    Test connection failure with invalid server URL
    [Tags]    negative    connection
    ${invalid_url}=    Set Variable    ws://invalid.server:9999
    Run Keyword And Expect Error    *Connection failed to server*
    ...    Connect To Game Server    ${invalid_url}    timeout=5
    Log    Connection correctly failed for invalid URL

Test Connection Timeout
    [Documentation]    Test connection timeout handling
    [Tags]    negative    connection
    ${timeout_url}=    Set Variable    ws://192.168.1.254:8765
    Run Keyword And Expect Error    *Connection failed to server*
    ...    Connect To Game Server    ${timeout_url}    timeout=3
    Log    Connection timeout handled correctly

Test Connection Stability
    [Documentation]    Test connection stability over time
    [Tags]    stability    connection
    Establish Server Connection
    Test Connection Stability    check_count=5
    Log    Connection stability verified

Test Reconnection After Disconnect
    [Documentation]    Test reconnection capability after disconnect
    [Tags]    reconnection    connection
    Establish Server Connection
    Close Server Connection
    Sleep    2s
    Establish Server Connection
    Verify Connection Status
    Log    Reconnection after disconnect successful

Test Multiple Connection Attempts
    [Documentation]    Test connection retry mechanism
    [Tags]    retry    connection
    Connect To Game Server With Retry    ${SERVER_URL}    max_retries=2
    Verify Connection Status
    Log    Connection retry mechanism working

Test Connection During Server Unavailable
    [Documentation]    Test behavior when server is unavailable
    [Tags]    negative    connection
    ${unavailable_url}=    Set Variable    ws://localhost:9999
    Run Keyword And Expect Error    *Connection failed to server*
    ...    Connect To Game Server With Retry    ${unavailable_url}    max_retries=2
    Log    Connection correctly failed when server unavailable