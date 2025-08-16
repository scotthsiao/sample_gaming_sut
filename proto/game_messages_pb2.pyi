from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GameRoundStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NO_ACTIVE_ROUND: _ClassVar[GameRoundStatus]
    BETTING_PHASE: _ClassVar[GameRoundStatus]
    WAITING_RESULTS: _ClassVar[GameRoundStatus]
NO_ACTIVE_ROUND: GameRoundStatus
BETTING_PHASE: GameRoundStatus
WAITING_RESULTS: GameRoundStatus

class LoginRequest(_message.Message):
    __slots__ = ("username", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ("success", "message", "session_token", "user_id", "balance")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    session_token: str
    user_id: int
    balance: int
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ..., session_token: _Optional[str] = ..., user_id: _Optional[int] = ..., balance: _Optional[int] = ...) -> None: ...

class RoomJoinRequest(_message.Message):
    __slots__ = ("room_id",)
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    room_id: int
    def __init__(self, room_id: _Optional[int] = ...) -> None: ...

class RoomJoinResponse(_message.Message):
    __slots__ = ("success", "message", "room_id", "player_count", "jackpot_pool")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_COUNT_FIELD_NUMBER: _ClassVar[int]
    JACKPOT_POOL_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    room_id: int
    player_count: int
    jackpot_pool: int
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ..., room_id: _Optional[int] = ..., player_count: _Optional[int] = ..., jackpot_pool: _Optional[int] = ...) -> None: ...

class SnapshotRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SnapshotResponse(_message.Message):
    __slots__ = ("user_balance", "active_bets", "current_room", "jackpot_pool", "round_status")
    USER_BALANCE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_BETS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ROOM_FIELD_NUMBER: _ClassVar[int]
    JACKPOT_POOL_FIELD_NUMBER: _ClassVar[int]
    ROUND_STATUS_FIELD_NUMBER: _ClassVar[int]
    user_balance: int
    active_bets: _containers.RepeatedCompositeFieldContainer[Bet]
    current_room: int
    jackpot_pool: int
    round_status: GameRoundStatus
    def __init__(self, user_balance: _Optional[int] = ..., active_bets: _Optional[_Iterable[_Union[Bet, _Mapping]]] = ..., current_room: _Optional[int] = ..., jackpot_pool: _Optional[int] = ..., round_status: _Optional[_Union[GameRoundStatus, str]] = ...) -> None: ...

class Bet(_message.Message):
    __slots__ = ("dice_face", "amount", "bet_id", "round_id")
    DICE_FACE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BET_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_ID_FIELD_NUMBER: _ClassVar[int]
    dice_face: int
    amount: int
    bet_id: str
    round_id: str
    def __init__(self, dice_face: _Optional[int] = ..., amount: _Optional[int] = ..., bet_id: _Optional[str] = ..., round_id: _Optional[str] = ...) -> None: ...

class BetPlacementRequest(_message.Message):
    __slots__ = ("dice_face", "amount", "round_id")
    DICE_FACE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_ID_FIELD_NUMBER: _ClassVar[int]
    dice_face: int
    amount: int
    round_id: str
    def __init__(self, dice_face: _Optional[int] = ..., amount: _Optional[int] = ..., round_id: _Optional[str] = ...) -> None: ...

class BetPlacementResponse(_message.Message):
    __slots__ = ("success", "message", "bet_id", "remaining_balance", "round_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    BET_ID_FIELD_NUMBER: _ClassVar[int]
    REMAINING_BALANCE_FIELD_NUMBER: _ClassVar[int]
    ROUND_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    bet_id: str
    remaining_balance: int
    round_id: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ..., bet_id: _Optional[str] = ..., remaining_balance: _Optional[int] = ..., round_id: _Optional[str] = ...) -> None: ...

class BetFinishedRequest(_message.Message):
    __slots__ = ("round_id",)
    ROUND_ID_FIELD_NUMBER: _ClassVar[int]
    round_id: str
    def __init__(self, round_id: _Optional[str] = ...) -> None: ...

class BetFinishedResponse(_message.Message):
    __slots__ = ("success", "message", "round_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ROUND_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    round_id: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ..., round_id: _Optional[str] = ...) -> None: ...

class ReckonResultRequest(_message.Message):
    __slots__ = ("round_id",)
    ROUND_ID_FIELD_NUMBER: _ClassVar[int]
    round_id: str
    def __init__(self, round_id: _Optional[str] = ...) -> None: ...

class ReckonResultResponse(_message.Message):
    __slots__ = ("dice_result", "bet_results", "total_winnings", "new_balance", "updated_jackpot_pool", "round_id")
    DICE_RESULT_FIELD_NUMBER: _ClassVar[int]
    BET_RESULTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_WINNINGS_FIELD_NUMBER: _ClassVar[int]
    NEW_BALANCE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_JACKPOT_POOL_FIELD_NUMBER: _ClassVar[int]
    ROUND_ID_FIELD_NUMBER: _ClassVar[int]
    dice_result: int
    bet_results: _containers.RepeatedCompositeFieldContainer[BetResult]
    total_winnings: int
    new_balance: int
    updated_jackpot_pool: int
    round_id: str
    def __init__(self, dice_result: _Optional[int] = ..., bet_results: _Optional[_Iterable[_Union[BetResult, _Mapping]]] = ..., total_winnings: _Optional[int] = ..., new_balance: _Optional[int] = ..., updated_jackpot_pool: _Optional[int] = ..., round_id: _Optional[str] = ...) -> None: ...

class BetResult(_message.Message):
    __slots__ = ("bet_id", "dice_face", "bet_amount", "won", "payout", "round_id")
    BET_ID_FIELD_NUMBER: _ClassVar[int]
    DICE_FACE_FIELD_NUMBER: _ClassVar[int]
    BET_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    WON_FIELD_NUMBER: _ClassVar[int]
    PAYOUT_FIELD_NUMBER: _ClassVar[int]
    ROUND_ID_FIELD_NUMBER: _ClassVar[int]
    bet_id: str
    dice_face: int
    bet_amount: int
    won: bool
    payout: int
    round_id: str
    def __init__(self, bet_id: _Optional[str] = ..., dice_face: _Optional[int] = ..., bet_amount: _Optional[int] = ..., won: _Optional[bool] = ..., payout: _Optional[int] = ..., round_id: _Optional[str] = ...) -> None: ...

class ErrorResponse(_message.Message):
    __slots__ = ("error_code", "error_message", "details")
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    error_code: int
    error_message: str
    details: str
    def __init__(self, error_code: _Optional[int] = ..., error_message: _Optional[str] = ..., details: _Optional[str] = ...) -> None: ...
