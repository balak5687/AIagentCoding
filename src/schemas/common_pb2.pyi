from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNSPECIFIED: _ClassVar[Status]
    COMPLETE: _ClassVar[Status]
    INCOMPLETE: _ClassVar[Status]
    IN_PROGRESS: _ClassVar[Status]
    FAILED: _ClassVar[Status]
    NEEDS_REVIEW: _ClassVar[Status]
    APPROVED: _ClassVar[Status]
    REJECTED: _ClassVar[Status]

class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEVERITY_UNSPECIFIED: _ClassVar[Severity]
    LOW: _ClassVar[Severity]
    MEDIUM: _ClassVar[Severity]
    HIGH: _ClassVar[Severity]
    CRITICAL: _ClassVar[Severity]
STATUS_UNSPECIFIED: Status
COMPLETE: Status
INCOMPLETE: Status
IN_PROGRESS: Status
FAILED: Status
NEEDS_REVIEW: Status
APPROVED: Status
REJECTED: Status
SEVERITY_UNSPECIFIED: Severity
LOW: Severity
MEDIUM: Severity
HIGH: Severity
CRITICAL: Severity

class FileReference(_message.Message):
    __slots__ = ("path", "start_line", "end_line", "description")
    PATH_FIELD_NUMBER: _ClassVar[int]
    START_LINE_FIELD_NUMBER: _ClassVar[int]
    END_LINE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    path: str
    start_line: int
    end_line: int
    description: str
    def __init__(self, path: _Optional[str] = ..., start_line: _Optional[int] = ..., end_line: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class Component(_message.Message):
    __slots__ = ("name", "type", "files", "description", "dependencies")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    files: _containers.RepeatedCompositeFieldContainer[FileReference]
    description: str
    dependencies: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., files: _Optional[_Iterable[_Union[FileReference, _Mapping]]] = ..., description: _Optional[str] = ..., dependencies: _Optional[_Iterable[str]] = ...) -> None: ...

class Risk(_message.Message):
    __slots__ = ("id", "description", "severity", "mitigation")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    MITIGATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    description: str
    severity: Severity
    mitigation: str
    def __init__(self, id: _Optional[str] = ..., description: _Optional[str] = ..., severity: _Optional[_Union[Severity, str]] = ..., mitigation: _Optional[str] = ...) -> None: ...

class TechnicalDebt(_message.Message):
    __slots__ = ("description", "severity", "reason")
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    description: str
    severity: Severity
    reason: str
    def __init__(self, description: _Optional[str] = ..., severity: _Optional[_Union[Severity, str]] = ..., reason: _Optional[str] = ...) -> None: ...
