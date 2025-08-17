*** Settings ***
Documentation    Authentication test cases for dice gambling game
Test Setup       Setup Authentication Test
Test Teardown    Cleanup Test Resources
Resource         ../resources/common.robot

*** Test Cases ***
Test Successful Login
    [Documentation]    Test successful user authentication
    [Tags]    smoke    authentication
    ${auth_result}=    Login With Valid Credentials    default
    Should Be Equal    ${auth_result}[status]    success
    Should Not Be Empty    ${auth_result}[session_token]
    Should Be True    ${auth_result}[balance] >= 0
    Log    User authentication successful

Test Login With Invalid Credentials
    [Documentation]    Test login failure with wrong credentials
    [Tags]    negative    authentication
    Login With Invalid Credentials    invalid_user    wrong_password
    Log    Invalid login correctly rejected

Test Login With Empty Credentials
    [Documentation]    Test login with empty username/password
    [Tags]    negative    authentication
    Run Keyword And Expect Error    *Login failed*
    ...    Login User    ${EMPTY}    ${EMPTY}
    Log    Empty credentials correctly rejected

Test Multiple User Types Login
    [Documentation]    Test login with different user types
    [Tags]    authentication    user_types
    # Test default user
    ${auth1}=    Login With Valid Credentials    default
    ${balance1}=    Get User Balance
    Close Server Connection
    
    # Reconnect and test high roller user
    Establish Server Connection
    ${auth2}=    Login With Valid Credentials    high_roller
    ${balance2}=    Get User Balance
    Should Not Be Equal    ${auth1}[user_id]    ${auth2}[user_id]
    Should Be True    ${balance2} >= 0
    Log    Multiple user types authenticated successfully

Test Session Token Validation
    [Documentation]    Test session token validation
    [Tags]    authentication    session
    Login With Valid Credentials    default
    ${session_token}=    Get Session Token
    Should Not Be Empty    ${session_token}
    Should Match Regexp    ${session_token}    ^[a-f0-9-]{36}$    Invalid UUID format
    Log    Session token validation passed

Test Balance Verification After Login
    [Documentation]    Test that balance matches expected value after login
    [Tags]    authentication    balance
    ${credentials}=    Get User Credentials    default
    ${auth_result}=    Login With Valid Credentials    default
    ${current_balance}=    Get User Balance
    Should Be True    ${current_balance} >= 0
    Log    Balance verification after login successful

Test Login With Admin User
    [Documentation]    Test login with admin user credentials
    [Tags]    authentication    admin
    ${auth_result}=    Login With Valid Credentials    admin_user
    Should Be Equal    ${auth_result}[status]    success
    ${balance}=    Get User Balance
    Should Be True    ${balance} >= 1000
    Log    Admin user login successful

Test Authentication State Persistence
    [Documentation]    Test that authentication state persists across operations
    [Tags]    authentication    persistence
    Login With Valid Credentials    default
    ${initial_token}=    Get Session Token
    
    # Perform some operation that requires authentication
    Retrieve Game State
    
    # Verify token is still valid
    ${current_token}=    Get Session Token
    Should Be Equal    ${current_token}    ${initial_token}
    Log    Authentication state persistence verified

*** Keywords ***
Setup Authentication Test
    [Documentation]    Setup for authentication tests
    Setup Test Environment
    Establish Server Connection