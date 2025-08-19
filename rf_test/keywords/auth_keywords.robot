*** Settings ***
Documentation    Authentication keywords for dice gambling game
Library          ../libraries/GameClientLibrary.py
# Library          ../libraries/TestDataLibrary.py  # Replaced with native Robot Framework resources
Library          Collections

*** Keywords ***
Login With Valid Credentials
    [Documentation]    Login with valid user credentials
    [Arguments]    ${user_type}=default
    ${credentials}=    Get User Credentials    ${user_type}
    ${result}=    Login User    ${credentials}[username]    ${credentials}[password]
    Should Be Equal    ${result}[status]    success
    Should Not Be Empty    ${result}[session_token]
    Should Be True    ${result}[user_id] > 0
    Should Be True    ${result}[balance] >= 0
    Log    Successfully logged in user: ${credentials}[username]
    Set Test Variable    ${AUTH_RESULT}    ${result}
    RETURN    ${result}

Login With Invalid Credentials
    [Documentation]    Attempt login with invalid credentials (should fail)
    [Arguments]    ${username}=invalid_user    ${password}=invalid_pass
    Run Keyword And Expect Error    *Login failed*    Login User    ${username}    ${password}
    Log    Login correctly failed for invalid credentials

Perform User Authentication
    [Documentation]    High-level authentication keyword
    [Arguments]    ${user_type}=default
    ${auth_result}=    Login With Valid Credentials    ${user_type}
    Set Test Variable    ${SESSION_TOKEN}    ${auth_result}[session_token]
    Set Test Variable    ${USER_ID}    ${auth_result}[user_id]
    Set Test Variable    ${USER_BALANCE}    ${auth_result}[balance]
    RETURN    ${auth_result}

Verify Authentication State
    [Documentation]    Verify user is properly authenticated
    ${session_token}=    Get Session Token
    ${user_balance}=    Get User Balance
    Should Not Be Empty    ${session_token}    User is not authenticated
    Should Be True    ${user_balance} >= 0    Invalid user balance
    Log    Authentication state verified - Balance: ${user_balance}

Test Login Flow
    [Documentation]    Complete login flow test
    [Arguments]    ${user_type}=default
    ${auth_result}=    Perform User Authentication    ${user_type}
    Verify Authentication State
    RETURN    ${auth_result}