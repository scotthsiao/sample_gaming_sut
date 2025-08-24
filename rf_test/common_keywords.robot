*** Settings ***
Documentation    Common resource file with shared imports and keywords for dice gambling game tests

# Variable imports
Resource         global_vars.robot

# Library imports
Library          Collections
Library          String
Library          DateTime
Library          OperatingSystem
Library          libraries/GameClientLibrary.py

# Keyword resource imports
Resource         keywords.robot

*** Variables ***
# Test execution variables
${TEST_START_TIME}    ${EMPTY}

*** Keywords ***
Initialize Test Suite
    [Documentation]    Initialize test suite with common setup
    ${start_time}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    Set Suite Variable    ${TEST_START_TIME}    ${start_time}
    Log    Dice gambling game test suite initialized at: ${start_time}
    
    # Verify test data integrity
    Validate Test Data Integrity
    
    # Log configuration
    Log Configuration

Log Configuration
    [Documentation]    Log current test configuration
    Log    Server URL: ${SERVER_URL}
    Log    Connection timeout: ${CONNECTION_TIMEOUT}s
    Log    Default balance: ${DEFAULT_BALANCE}

Common Test Setup
    [Documentation]    Common setup for individual dice game tests
    Log    Starting dice gambling game test: ${TEST_NAME}
    
    # Verify test prerequisites
    Should Not Be Empty    ${SERVER_URL}    Server URL not configured
    
    # Clear any previous test state
    Clear Test Variables

Common Test Teardown
    [Documentation]    Common teardown for individual dice game tests
    Log    Completing dice gambling game test: ${TEST_NAME}
    
    # Clean up connections and sessions
    Run Keyword And Ignore Error    Close Server Connection
    
    # Log test completion
    ${end_time}=    Get Current Date    result_format=%H:%M:%S
    Log    Test completed at: ${end_time}

# Test Setup and Teardown Keywords - consolidated from test_setup.robot
Setup Test Environment
    [Documentation]    Setup test environment for dice game test execution
    [Arguments]    ${env_name}=dev
    
    Log    Setting up dice game test environment: ${env_name}
    
    # Use configuration from global_vars.robot (which imports from generated_config.robot)
    # SERVER_URL and TIMEOUT are already defined in global scope from generated_config.robot
    Set Test Variable    ${TIMEOUT}       60  # Override timeout for specific tests if needed
    
    # Initialize test tracking (now using native Robot Framework keyword)
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
    
    # Clear test variables (no cached data to clear in simplified library)
    Clear Test Variables
    
    Log    Dice game test resources cleanup complete

Suite Teardown
    [Documentation]    Clean up suite-level resources without test variables
    
    Log    Cleaning up dice game test suite resources
    
    # Close server connection if active
    ${status}    ${result}=    Run Keyword And Ignore Error    Close Server Connection
    Run Keyword If    '${status}' == 'PASS'    Log    Connection closed during suite cleanup
    
    # Note: No cached data to clear in simplified library
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