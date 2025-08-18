*** Settings ***
Documentation    Test setup and teardown procedures for dice gambling game tests

*** Keywords ***
Setup Test Environment
    [Documentation]    Setup test environment for dice game test execution
    [Arguments]    ${env_name}=dev
    
    Log    Setting up dice game test environment: ${env_name}
    
    # Load environment configuration
    ${config}=    Get Environment Config    ${env_name}
    Set Test Variable    ${TEST_CONFIG}    ${config}
    
    # Set server URL based on environment
    ${server_url}=    Set Variable If
    ...    '${env_name}' == 'dev'        ws://${config}[server_host]:${config}[server_port]
    ...    '${env_name}' == 'staging'    wss://${config}[server_host]:${config}[server_port]
    ...    '${env_name}' == 'prod'       wss://${config}[server_host]:${config}[server_port]
    ...    ws://localhost:8767
    
    Set Test Variable    ${SERVER_URL}    ${server_url}
    Set Test Variable    ${TIMEOUT}       ${config}[timeout]
    
    # Initialize test tracking
    ${test_id}=    Generate Random Username    test
    Set Test Variable    ${TEST_ID}    ${test_id}
    
    Log    Dice game test environment setup complete
    Log    Server URL: ${SERVER_URL}
    Log    Timeout: ${TIMEOUT}
    Log    Test ID: ${TEST_ID}

Cleanup Test Resources
    [Documentation]    Clean up all dice game test resources
    
    Log    Cleaning up dice game test resources
    
    # Clean up active rounds first (multiple attempts)
    FOR    ${i}    IN RANGE    3
        ${status}    ${result}=    Run Keyword And Ignore Error    Cleanup Active Round
        Run Keyword If    '${status}' == 'PASS'    Log    Active round cleanup attempt ${i+1} successful
        Exit For Loop If    '${status}' == 'PASS'
    END
    
    # Reset client state
    ${status}    ${result}=    Run Keyword And Ignore Error    Reset Client State
    Run Keyword If    '${status}' == 'PASS'    Log    Client state reset
    
    # Close server connection if active
    ${status}    ${result}=    Run Keyword And Ignore Error    Close Server Connection
    Run Keyword If    '${status}' == 'PASS'    Log    Connection closed during cleanup
    
    # Clear cached data
    Clear Cached Data
    
    # Clear test variables
    Clear Test Variables
    
    Log    Dice game test resources cleanup complete

Suite Teardown
    [Documentation]    Clean up suite-level resources without test variables
    
    Log    Cleaning up dice game test suite resources
    
    # Close server connection if active
    ${status}    ${result}=    Run Keyword And Ignore Error    Close Server Connection
    Run Keyword If    '${status}' == 'PASS'    Log    Connection closed during suite cleanup
    
    # Clear cached data
    Clear Cached Data
    
    # Note: Cannot clear test variables during suite teardown
    Log    Dice game test suite cleanup complete

Setup Dice Game Test Environment
    [Documentation]    Setup environment specifically for dice game tests
    [Arguments]    ${user_type}=default    ${env_name}=dev
    
    Setup Test Environment    ${env_name}
    Establish Server Connection
    Perform User Authentication    ${user_type}
    
    Log    Dice game test environment ready

Setup Performance Test Environment
    [Documentation]    Setup environment for dice game performance tests
    [Arguments]    ${env_name}=dev
    
    Setup Test Environment    ${env_name}
    
    # Set performance-specific timeouts
    Set Test Variable    ${PERF_TIMEOUT}        60
    Set Test Variable    ${RESPONSE_TIMEOUT}    5
    Set Test Variable    ${CONNECTION_TIMEOUT}  10
    
    Log    Dice game performance test environment ready

Validate Test Prerequisites
    [Documentation]    Validate that test prerequisites are met
    
    # Check server URL is configured
    Should Not Be Empty    ${SERVER_URL}    Server URL not configured
    
    # Check timeout is set
    Should Not Be Empty    ${TIMEOUT}    Timeout not configured
    
    # Validate test data integrity
    ${integrity}=    Validate Test Data Integrity
    Should Be True    ${integrity}    Test data integrity check failed
    
    Log    Dice game test prerequisites validated

Clear Test Variables
    [Documentation]    Clear test-specific variables
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${SESSION_TOKEN}      ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${USER_ID}           ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${USER_BALANCE}      0
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${CURRENT_ROOM}      ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${CURRENT_BET_ID}    ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${CURRENT_ROUND_ID}  ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${GAME_SNAPSHOT}     ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${GAME_RESULT}       ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${AUTH_RESULT}       ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${ROOM_RESULT}       ${EMPTY}
    ${status}    ${result}=    Run Keyword And Ignore Error    Set Test Variable    ${BET_RESULT}        ${EMPTY}

Log Test Environment Info
    [Documentation]    Log current dice game test environment information
    
    Log    ===== Dice Game Test Environment =====
    Log    Server URL: ${SERVER_URL}
    Log    Environment: ${TEST_ENV}
    Log    Timeout: ${TIMEOUT}
    Log    Test ID: ${TEST_ID}
    Log    Suite: ${SUITE_NAME}
    Log    Test: ${TEST_NAME}
    Log    ====================================