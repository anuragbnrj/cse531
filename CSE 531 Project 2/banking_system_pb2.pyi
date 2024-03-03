from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Transfer_Request(_message.Message):
    __slots__ = ["id", "interface", "amount", "propagate", "customer_request_id", "logical_clock"]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PROPAGATE_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_CLOCK_FIELD_NUMBER: _ClassVar[int]
    id: int
    interface: str
    amount: int
    propagate: bool
    customer_request_id: int
    logical_clock: int
    def __init__(self, id: _Optional[int] = ..., interface: _Optional[str] = ..., amount: _Optional[int] = ..., propagate: bool = ..., customer_request_id: _Optional[int] = ..., logical_clock: _Optional[int] = ...) -> None: ...

class Transfer_Response(_message.Message):
    __slots__ = ["id", "interface", "result", "balance", "logical_clock"]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_CLOCK_FIELD_NUMBER: _ClassVar[int]
    id: int
    interface: str
    result: str
    balance: int
    logical_clock: int
    def __init__(self, id: _Optional[int] = ..., interface: _Optional[str] = ..., result: _Optional[str] = ..., balance: _Optional[int] = ..., logical_clock: _Optional[int] = ...) -> None: ...
