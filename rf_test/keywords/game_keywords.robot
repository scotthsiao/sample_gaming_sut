*** Settings ***
Documentation    Dice gambling game operation keywords
Library          ../libraries/GameClientLibrary.py
# Library          ../libraries/TestDataLibrary.py  # Replaced with native Robot Framework resources
Library          Collections

*** Keywords ***
Join Default Game Room
    [Documentation]    Join the default dice game room
    ${room_data}=    Get Room Data    room_1
    ${result}=    Join Game Room    ${room_data}[room_id]
    Should Be Equal    ${result}[status]    success
    Should Be Equal As Numbers    ${result}[room_id]    ${room_data}[room_id]
    Log    Successfully joined room: ${result}[room_id]
    Set Test Variable    ${CURRENT_ROOM}    ${result}[room_id]
    Set Test Variable    ${ROOM_RESULT}    ${result}
    RETURN    ${result}

Join Specific Game Room
    [Documentation]    Join a specific dice game room by ID
    [Arguments]    ${room_id}
    ${result}=    Join Game Room    ${room_id}
    Should Be Equal    ${result}[status]    success
    Should Be Equal As Numbers    ${result}[room_id]    ${room_id}
    Log    Successfully joined room: ${room_id}
    Set Test Variable    ${CURRENT_ROOM}    ${room_id}
    Set Test Variable    ${ROOM_RESULT}    ${result}
    RETURN    ${result}

Retrieve Game State
    [Documentation]    Get current dice game snapshot
    ${snapshot}=    Get Game Snapshot
    Should Not Be Empty    ${snapshot}
    Should Contain    ${snapshot}    user_balance
    Should Contain    ${snapshot}    current_room
    Log    Game snapshot retrieved successfully
    Set Test Variable    ${GAME_SNAPSHOT}    ${snapshot}
    [Return]    ${snapshot}

Place Valid Dice Bet
    [Documentation]    Place a valid bet on dice outcome
    [Arguments]    ${dice_face}=3    ${amount}=10    ${round_id}=${EMPTY}
    ${round_id_arg}=    Set Variable If    '${round_id}' == '${EMPTY}'    ${None}    ${round_id}
    ${result}=    Place Bet    ${dice_face}    ${amount}    ${round_id_arg}
    Should Be Equal    ${result}[status]    success
    Should Not Be Empty    ${result}[bet_id]
    Should Be Equal As Numbers    ${result}[dice_face]    ${dice_face}
    Should Be Equal As Numbers    ${result}[amount]    ${amount}
    Log    Dice bet placed successfully: ${result}[bet_id]
    Set Test Variable    ${CURRENT_BET_ID}    ${result}[bet_id]
    Set Test Variable    ${CURRENT_ROUND_ID}    ${result}[round_id]
    Set Test Variable    ${BET_RESULT}    ${result}
    RETURN    ${result}

Place Random Dice Bet
    [Documentation]    Place a bet with random dice face and amount
    ${dice_face}=    Evaluate    random.randint(1, 6)    random
    ${amount}=    Evaluate    random.randint(1, 100)    random
    ${result}=    Place Valid Dice Bet    ${dice_face}    ${amount}
    Log    Random dice bet placed: face ${dice_face} for ${amount}
    RETURN    ${result}

Finish Current Betting Round
    [Documentation]    Signal that betting is finished for current round
    [Arguments]    ${round_id}=${EMPTY}
    ${round_id_arg}=    Set Variable If    '${round_id}' == '${EMPTY}'    ${None}    ${round_id}
    ${result}=    Finish Betting    ${round_id_arg}
    Should Be Equal    ${result}[status]    success
    Log    Betting finished for round: ${result}[round_id]
    RETURN    ${result}

Get Dice Game Result
    [Documentation]    Get the dice game result for current round
    [Arguments]    ${round_id}=${EMPTY}
    ${round_id_arg}=    Set Variable If    '${round_id}' == '${EMPTY}'    ${None}    ${round_id}
    ${result}=    Get Game Result    ${round_id_arg}
    Should Be True    1 <= ${result}[dice_result] <= 6    Invalid dice result
    Should Be True    ${result}[total_winnings] >= 0    Invalid winnings amount
    Should Be True    ${result}[new_balance] >= 0    Invalid new balance
    Log    Dice game result: ${result}[dice_result], winnings: ${result}[total_winnings]
    Set Test Variable    ${GAME_RESULT}    ${result}
    RETURN    ${result}

Complete Dice Game Round
    [Documentation]    Complete a full dice game round from bet to result
    [Arguments]    ${dice_face}=3    ${amount}=10
    ${bet_result}=    Place Valid Dice Bet    ${dice_face}    ${amount}
    ${finish_result}=    Finish Current Betting Round    ${bet_result}[round_id]
    ${game_result}=    Get Dice Game Result    ${bet_result}[round_id]
    
    # Verify game logic
    ${won}=    Evaluate    ${dice_face} == ${game_result}[dice_result]
    ${expected_winnings}=    Set Variable If    ${won}    ${amount * 6}    0
    Should Be Equal As Numbers    ${game_result}[total_winnings]    ${expected_winnings}
    
    Log    Dice game round completed - Result: ${game_result}[dice_result], Won: ${won}
    [Return]    ${game_result}

Place Multiple Dice Bets
    [Documentation]    Place multiple bets in the same round
    [Arguments]    ${bet_count}=3    ${round_id}=${EMPTY}
    ${bet_results}=    Create List
    ${current_round_id}=    Set Variable    ${round_id}
    
    FOR    ${i}    IN RANGE    ${bet_count}
        ${dice_face}=    Evaluate    random.randint(1, 6)    random
        ${amount}=    Evaluate    random.randint(1, 50)    random
        ${bet_result}=    Place Valid Dice Bet    ${dice_face}    ${amount}    ${current_round_id}
        ${current_round_id}=    Set Variable    ${bet_result}[round_id]
        Append To List    ${bet_results}    ${bet_result}
        Sleep    0.5s
    END
    
    Log    Placed ${bet_count} dice bets successfully
    RETURN    ${bet_results}

Verify Dice Game Balance
    [Documentation]    Verify user balance after game operations
    [Arguments]    ${expected_balance}
    ${current_balance}=    Get User Balance
    Should Be Equal As Numbers    ${current_balance}    ${expected_balance}
    Log    Balance verified: ${current_balance}

Perform Full Game Round
    [Documentation]    Perform a full game round including placing a bet, finishing the round and getting the result.
    [Arguments]    ${dice_face}    ${bet_amount}
    ${bet_result}=    Place Valid Dice Bet    ${dice_face}    ${bet_amount}
    Finish Current Betting Round    ${bet_result}[round_id]
    ${game_result}=    Get Dice Game Result    ${bet_result}[round_id]
    [Return]    ${game_result}