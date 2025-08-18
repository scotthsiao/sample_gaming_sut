*** Settings ***
Documentation    Common resource file with shared imports and keywords for dice gambling game tests

# Variable imports
Resource         ../data/variables/global_vars.robot

# Library imports
Library          Collections
Library          String
Library          DateTime
Library          OperatingSystem
Library          ../libraries/GameClientLibrary.py
Library          ../libraries/TestDataLibrary.py

# Keyword resource imports
Resource         ../keywords/connection_keywords.robot
Resource         ../keywords/auth_keywords.robot
Resource         ../keywords/game_keywords.robot
Resource         ../keywords/utility_keywords.robot
Resource         test_setup.robot

*** Variables ***
# Test execution variables
${TEST_START_TIME}    ${EMPTY}
${TEST_ENV}           dev

*** Keywords ***
Initialize Test Suite
    [Documentation]    Initialize test suite with common setup
    ${start_time}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    Set Suite Variable    ${TEST_START_TIME}    ${start_time}
    Log    Dice gambling game test suite initialized at: ${start_time}
    
    # Verify test data integrity
    Verify Test Data Integrity
    
    # Set environment-specific variables
    Set Environment Variables

Set Environment Variables
    [Documentation]    Set variables based on test environment
    ${env}=    Get Variable Value    ${TEST_ENV}    dev
    
    Run Keyword If    '${env}' == 'dev'
    ...    Set Suite Variable    ${SERVER_URL}    ws://localhost:8767
    ...    ELSE IF    '${env}' == 'staging'
    ...    Set Suite Variable    ${SERVER_URL}    wss://staging.gameserver.com:8767
    ...    ELSE IF    '${env}' == 'prod'
    ...    Set Suite Variable    ${SERVER_URL}    wss://prod.gameserver.com:8767
    
    Log    Environment set to: ${env}
    Log    Server URL: ${SERVER_URL}

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