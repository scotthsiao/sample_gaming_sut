*** Settings ***
Documentation    Utility and helper keywords
Library          ../libraries/GameClientLibrary.py
# Library          ../libraries/TestDataLibrary.py  # Replaced with native Robot Framework resources
Library          Collections
Library          String
Library          DateTime

*** Keywords ***
Wait For Specific Message Type
    [Documentation]    Wait for a specific message type from server
    [Arguments]    ${message_type}    ${timeout}=10
    ${response}=    Wait For Server Response    ${timeout}    ${message_type}
    Should Be Equal    ${response}[type]    ${message_type}
    Log    Received expected message type: ${message_type}
    RETURN    ${response}

Validate Response Schema
    [Documentation]    Validate response against JSON schema
    [Arguments]    ${response}    ${schema_file}
    ${validation_result}=    Validate JSON Response    ${response}    ${schema_file}
    Should Be True    ${validation_result}    Response validation failed
    Log    Response schema validation passed

Validate Required Fields
    [Documentation]    Check that response contains required fields
    [Arguments]    ${response}    @{required_fields}
    ${field_list}=    Create List    @{required_fields}
    ${validation_result}=    Validate JSON Response    ${response}    required_fields=${field_list}
    Should Be True    ${validation_result}    Required fields validation failed
    Log    Required fields validation passed

Generate Test Report Data
    [Documentation]    Generate data for test reporting
    ${timestamp}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    ${test_data}=    Create Dictionary
    ...    timestamp=${timestamp}
    ...    test_suite=${SUITE_NAME}
    ...    test_case=${TEST_NAME}
    Log    Test report data generated
    RETURN    ${test_data}

Setup Utility Test Environment
    [Documentation]    Setup test environment with simplified configuration (utility version)
    [Arguments]    ${env_name}=dev
    # Use simplified configuration - just set the server URL directly
    Set Test Variable    ${SERVER_URL}    ws://localhost:8767
    Set Test Variable    ${TIMEOUT}    60
    Log    Utility test environment setup complete for: ${env_name}

Cleanup Utility Test Resources
    [Documentation]    Clean up test resources (utility version)
    Run Keyword And Ignore Error    Close Server Connection
    # No cached data to clear in simplified version
    Log    Utility test resources cleaned up

Verify Test Data Integrity
    [Documentation]    Verify all test data files are valid
    ${integrity_check}=    Validate Test Data Integrity
    Should Be True    ${integrity_check}    Test data integrity check failed
    Log    Test data integrity verified

Validate Test Data Integrity
    [Documentation]    Simple validation - just check if data exists
    
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

Create Test User
    [Documentation]    Create a test user for the current test - simplified version
    [Arguments]    ${username}=${EMPTY}    ${password}=${EMPTY}
    # Use default user credentials if none provided
    ${actual_username}=    Set Variable If    '${username}' == '${EMPTY}'    testuser1    ${username}
    ${actual_password}=    Set Variable If    '${password}' == '${EMPTY}'    password123    ${password}
    ${mock_user}=    Create Dictionary    username=${actual_username}    password=${actual_password}
    Set Test Variable    ${TEST_USER}    ${mock_user}
    Log    Test user created: ${mock_user}[username]
    RETURN    ${mock_user}

Log Test Step
    [Documentation]    Log a test step with timestamp
    [Arguments]    ${step_description}
    ${timestamp}=    Get Current Date    result_format=%H:%M:%S
    Log    [${timestamp}] ${step_description}

Wait With Timeout
    [Documentation]    Generic wait with timeout and custom message
    [Arguments]    ${condition_keyword}    ${timeout}=30    ${error_message}=Timeout waiting for condition
    Wait Until Keyword Succeeds    ${timeout}    1s    ${condition_keyword}
    Log    Condition met within timeout: ${timeout}s

Retry Operation
    [Documentation]    Retry an operation with specified attempts
    [Arguments]    ${operation_keyword}    ${max_attempts}=3    @{args}
    FOR    ${attempt}    IN RANGE    1    ${max_attempts + 1}
        ${status}    ${result}=    Run Keyword And Ignore Error    ${operation_keyword}    @{args}
        Return From Keyword If    '${status}' == 'PASS'    ${result}
        Log    Attempt ${attempt} failed, retrying...
        Sleep    1s
    END
    Fail    Operation failed after ${max_attempts} attempts

# Test Data Management Keywords - consolidated from test_data_keywords.robot
Get User Credentials
    [Documentation]    Get user credentials by type
    [Arguments]    ${user_type}=default
    
    IF    '${user_type}' == 'default'
        Log    Retrieved credentials for user type: ${user_type}
        RETURN    &{DEFAULT_USER}
    ELSE IF    '${user_type}' == 'high_roller'
        Log    Retrieved credentials for user type: ${user_type}
        RETURN    &{HIGH_ROLLER_USER}
    ELSE IF    '${user_type}' == 'basic_user'
        Log    Retrieved credentials for user type: ${user_type}
        RETURN    &{BASIC_USER_DATA}
    ELSE
        Fail    User type '${user_type}' not found
    END

Get Room Data
    [Documentation]    Get room configuration by type
    [Arguments]    ${room_type}=room_1
    
    IF    '${room_type}' == 'room_1'
        Log    Retrieved room data for type: ${room_type}
        RETURN    &{ROOM_1_DATA}
    ELSE IF    '${room_type}' == 'room_2'
        Log    Retrieved room data for type: ${room_type}
        RETURN    &{ROOM_2_DATA}
    ELSE IF    '${room_type}' == 'room_3'
        Log    Retrieved room data for type: ${room_type}
        RETURN    &{ROOM_3_DATA}
    ELSE
        Fail    Room type '${room_type}' not found
    END

Generate Random Username
    [Documentation]    Generate a random username
    [Arguments]    ${prefix}=testuser
    
    ${random_suffix}=    Evaluate    ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))    modules=random,string
    ${username}=    Set Variable    ${prefix}_${random_suffix}
    Log    Generated random username: ${username}
    RETURN    ${username}

# Connection Keywords - consolidated from connection_keywords.robot
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