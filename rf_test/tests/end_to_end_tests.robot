*** Settings ***
Documentation    End-to-end test cases for complete dice gambling game workflows
Test Setup       Setup Test Environment
Test Teardown    Cleanup Test Resources
Resource         ../common_keywords.robot

*** Test Cases ***
Test Complete Dice Game Workflow
    [Documentation]    Test complete dice game workflow from connection to result
    [Tags]    smoke    e2e    workflow
    
    # Step 1: Connect to dice game server
    Log    Starting complete dice game workflow
    Establish Server Connection
    
    # Step 2: Login user
    ${auth_result}=    Perform User Authentication    default
    
    # Step 3: Join game room
    ${room_result}=    Join Default Game Room
    
    # Step 4: Get game snapshot
    ${snapshot}=    Retrieve Game State
    ${initial_balance}=    Set Variable    ${snapshot}[user_balance]
    
    # Step 5: Perform full game round
    ${game_result}=    Perform Full Game Round    dice_face=3    amount=10
    
    # Step 8: Verify game logic
    Should Be True    1 <= ${game_result}[dice_result] <= 6
    ${won}=    Evaluate    3 == ${game_result}[dice_result]
    ${expected_winnings}=    Set Variable If    ${won}    60    0
    Should Be Equal As Numbers    ${game_result}[total_winnings]    ${expected_winnings}
    
    Log    Complete dice game workflow successful

Test Multiple Bets Single Round
    [Documentation]    Test placing multiple bets in a single dice game round
    [Tags]    e2e    multiple_bets
    
    # Setup
    Establish Server Connection
    Perform User Authentication    high_roller
    Join Default Game Room
    ${initial_snapshot}=    Retrieve Game State
    ${initial_balance}=    Set Variable    ${initial_snapshot}[user_balance]
    
    # Place multiple bets in same round
    ${bet1}=    Place Valid Dice Bet    1    100
    ${round_id}=    Set Variable    ${bet1}[round_id]
    ${bet2}=    Place Valid Dice Bet    3    200    ${round_id}
    ${bet3}=    Place Valid Dice Bet    6    150    ${round_id}
    
    # Finish betting and get result
    ${finish_result}=    Finish Current Betting Round    ${round_id}
    ${game_result}=    Get Dice Game Result    ${round_id}
    
    # Verify results
    Should Be True    1 <= ${game_result}[dice_result] <= 6
    ${expected_balance}=    Evaluate    ${initial_balance} - 450 + ${game_result}[total_winnings]
    Should Be Equal As Numbers    ${game_result}[new_balance]    ${expected_balance}
    
    Log    Multiple bets single round completed

Test High Stakes Dice Game
    [Documentation]    Test high stakes dice betting scenario
    [Tags]    e2e    high_stakes
    
    # Setup with high roller user
    Establish Server Connection
    Perform User Authentication    high_roller
    ${room_result}=    Join Specific Game Room    2
    
    # Place high stakes bet
    ${bet_result}=    Place Valid Dice Bet    4    1000
    Should Be Equal    ${bet_result}[status]    success
    Should Be Equal As Numbers    ${bet_result}[amount]    1000
    
    # Complete the round
    ${finish_result}=    Finish Current Betting Round
    ${game_result}=    Get Dice Game Result
    
    # Verify high stakes payout
    ${won}=    Evaluate    4 == ${game_result}[dice_result]
    ${expected_winnings}=    Set Variable If    ${won}    6000    0
    Should Be Equal As Numbers    ${game_result}[total_winnings]    ${expected_winnings}
    
    Log    High stakes dice game completed

Test Rapid Betting Rounds
    [Documentation]    Test rapid consecutive betting rounds
    [Tags]    e2e    rapid_betting
    
    # Setup
    Establish Server Connection
    Perform User Authentication    default
    Join Default Game Room
    
    # Perform multiple rapid rounds
    FOR    ${round}    IN RANGE    3
        ${dice_face}=    Evaluate    random.randint(1, 6)    random
        ${amount}=    Set Variable    10
        ${bet_result}=    Place Valid Dice Bet    ${dice_face}    ${amount}
        ${finish_result}=    Finish Current Betting Round
        ${game_result}=    Get Dice Game Result
        Should Be True    1 <= ${game_result}[dice_result] <= 6
        Sleep    0.5s
    END
    
    Log    Rapid betting rounds completed

Test Balance Tracking Accuracy
    [Documentation]    Test accurate balance tracking throughout game
    [Tags]    e2e    balance_tracking
    
    # Setup and get initial balance
    Establish Server Connection
    ${auth_result}=    Perform User Authentication    default
    Join Default Game Room
    ${initial_snapshot}=    Retrieve Game State
    ${starting_balance}=    Set Variable    ${initial_snapshot}[user_balance]
    
    # Track balance through multiple operations
    ${bet_amount}=    Set Variable    50
    ${bet_result}=    Place Valid Dice Bet    2    ${bet_amount}
    ${balance_after_bet}=    Get User Balance
    ${expected_after_bet}=    Evaluate    ${starting_balance} - ${bet_amount}
    Should Be Equal As Numbers    ${balance_after_bet}    ${expected_after_bet}
    
    # Complete round and verify final balance
    ${finish_result}=    Finish Current Betting Round
    ${game_result}=    Get Dice Game Result
    ${final_balance}=    Set Variable    ${game_result}[new_balance]
    ${expected_final}=    Evaluate    ${starting_balance} - ${bet_amount} + ${game_result}[total_winnings]
    Should Be Equal As Numbers    ${final_balance}    ${expected_final}
    
    Log    Balance tracking accuracy verified

Test Error Recovery During Game
    [Documentation]    Test error recovery and game continuation
    [Tags]    e2e    error_recovery
    
    # Setup
    Establish Server Connection
    Perform User Authentication    default
    Join Default Game Room
    
    # Intentionally cause an error and recover
    ${status}    ${result}=    Run Keyword And Ignore Error
    ...    Place Valid Dice Bet    7    10  # Invalid dice face
    
    # Verify we can still perform valid operations
    ${bet_result}=    Place Valid Dice Bet    3    10
    Should Be Equal    ${bet_result}[status]    success
    
    ${finish_result}=    Finish Current Betting Round
    ${game_result}=    Get Dice Game Result
    Should Be True    1 <= ${game_result}[dice_result] <= 6
    
    Log    Error recovery during game successful

Test Complete User Journey
    [Documentation]    Test realistic complete user journey
    [Tags]    e2e    user_journey
    
    # User connects and explores
    Establish Server Connection
    ${auth_result}=    Perform User Authentication    default
    
    # User checks different rooms
    ${room1}=    Join Specific Game Room    1
    ${snapshot1}=    Retrieve Game State
    
    ${room2}=    Join Specific Game Room    3  # Beginner room
    ${snapshot2}=    Retrieve Game State
    
    # Back to main room for gaming
    ${room3}=    Join Specific Game Room    1
    
    # User places several bets with different strategies
    ${conservative_bet}=    Place Valid Dice Bet    1    5
    ${finish1}=    Finish Current Betting Round
    ${result1}=    Get Dice Game Result
    
    ${aggressive_bet}=    Place Valid Dice Bet    6    25
    ${finish2}=    Finish Current Betting Round
    ${result2}=    Get Dice Game Result
    
    ${balanced_bet}=    Place Valid Dice Bet    3    15
    ${finish3}=    Finish Current Betting Round
    ${result3}=    Get Dice Game Result
    
    # Verify all results are valid
    Should Be True    1 <= ${result1}[dice_result] <= 6
    Should Be True    1 <= ${result2}[dice_result] <= 6
    Should Be True    1 <= ${result3}[dice_result] <= 6
    
    Log    Complete user journey successful

Test Session Persistence
    [Documentation]    Test session persistence across multiple game rounds
    [Tags]    e2e    session_persistence
    
    # Establish session
    Establish Server Connection
    ${auth_result}=    Perform User Authentication    default
    Join Default Game Room
    ${initial_token}=    Get Session Token
    
    # Perform multiple game rounds to test session persistence
    FOR    ${i}    IN RANGE    3
        ${snapshot}=    Retrieve Game State
        Should Contain    ${snapshot}    user_balance
        ${bet_result}=    Place Valid Dice Bet    ${i + 1}    10
        ${finish_result}=    Finish Current Betting Round
        ${game_result}=    Get Dice Game Result
        
        # Verify session token hasn't changed
        ${current_token}=    Get Session Token
        Should Be Equal    ${current_token}    ${initial_token}
        Sleep    1s
    END
    
    Log    Session persistence verified across multiple rounds