*** Settings ***
Documentation    Utility and helper keywords
Library          ../libraries/GameClientLibrary.py
Library          ../libraries/TestDataLibrary.py
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
    [Documentation]    Setup test environment with configuration (utility version)
    [Arguments]    ${env_name}=dev
    ${config}=    Get Environment Config    ${env_name}
    Set Test Variable    ${TEST_CONFIG}    ${config}
    Set Test Variable    ${SERVER_URL}    ws://${config}[server_host]:${config}[server_port]/ws
    Set Test Variable    ${TIMEOUT}    ${config}[timeout]
    Log    Utility test environment setup complete for: ${env_name}

Cleanup Utility Test Resources
    [Documentation]    Clean up test resources (utility version)
    Run Keyword And Ignore Error    Close Server Connection
    Clear Cached Data
    Log    Utility test resources cleaned up

Verify Test Data Integrity
    [Documentation]    Verify all test data files are valid
    ${integrity_check}=    Validate Test Data Integrity
    Should Be True    ${integrity_check}    Test data integrity check failed
    Log    Test data integrity verified

Create Test User
    [Documentation]    Create a test user for the current test
    [Arguments]    ${username}=${EMPTY}    ${password}=${EMPTY}
    ${mock_user}=    Create Mock User    ${username}    ${password}
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