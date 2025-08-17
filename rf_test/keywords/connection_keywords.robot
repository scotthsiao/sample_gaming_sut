*** Settings ***
Documentation    Connection-related keywords for dice gambling game WebSocket communication
Library          ../libraries/GameClientLibrary.py
Library          Collections

*** Keywords ***
Connect To Game Server With Retry
    [Documentation]    Connect to dice game server with retry mechanism
    [Arguments]    ${server_url}    ${max_retries}=3    ${timeout}=10
    FOR    ${retry}    IN RANGE    ${max_retries}
        ${status}=    Connect To Game Server    ${server_url}    ${timeout}
        Return From Keyword If    ${status}    ${status}
        Log    Connection attempt ${retry + 1} failed, retrying...
        Sleep    2s
    END
    Fail    Failed to connect after ${max_retries} attempts

Establish Server Connection
    [Documentation]    High-level keyword to establish server connection
    [Arguments]    ${server_url}=${SERVER_URL}
    ${connection_status}=    Connect To Game Server With Retry    ${server_url}
    Should Be True    ${connection_status}    Connection to server failed
    Log    Successfully connected to dice game server: ${server_url}
    RETURN    ${connection_status}

Verify Connection Status
    [Documentation]    Verify that WebSocket connection is active
    ${status}=    Get Connection Status
    Should Be True    ${status}    WebSocket connection is not active
    Log    WebSocket connection to dice game server is active

Close Server Connection
    [Documentation]    Cleanly close server connection
    ${status}=    Disconnect From Server
    Should Be True    ${status}    Failed to disconnect from server
    Log    Successfully disconnected from dice game server

Test Connection Stability
    [Documentation]    Test connection stability by checking status multiple times
    [Arguments]    ${check_count}=3
    FOR    ${i}    IN RANGE    ${check_count}
        Verify Connection Status
        Sleep    1s
    END
    Log    Connection stability test passed with ${check_count} checks