from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Transfer_Request(_message.Message):
    __slots__ = ("id", "operation_type", "amount", "propagate")
    ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PROPAGATE_FIELD_NUMBER: _ClassVar[int]
    id: int
    operation_type: str
    amount: int
    propagate: bool
    def __init__(self, id: _Optional[int] = ..., operation_type: _Optional[str] = ..., amount: _Optional[int] = ..., propagate: bool = ...) -> None: ...

class Transfer_Response(_message.Message):
    __slots__ = ("id", "interface", "result", "balance")
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    id: int
    interface: str
    result: str
    balance: int
    def __init__(self, id: _Optional[int] = ..., interface: _Optional[str] = ..., result: _Optional[str] = ..., balance: _Optional[int] = ...) -> None: ...
