import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChangeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHANGE_TYPE_UNSPECIFIED: _ClassVar[ChangeType]
    MODIFY: _ClassVar[ChangeType]
    DELETE: _ClassVar[ChangeType]
    RENAME: _ClassVar[ChangeType]
CHANGE_TYPE_UNSPECIFIED: ChangeType
MODIFY: ChangeType
DELETE: ChangeType
RENAME: ChangeType

class CoderOutput(_message.Message):
    __slots__ = ("agent", "status", "confidence", "implementation", "markdown_body")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_FIELD_NUMBER: _ClassVar[int]
    MARKDOWN_BODY_FIELD_NUMBER: _ClassVar[int]
    agent: str
    status: _common_pb2.Status
    confidence: int
    implementation: Implementation
    markdown_body: str
    def __init__(self, agent: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, str]] = ..., confidence: _Optional[int] = ..., implementation: _Optional[_Union[Implementation, _Mapping]] = ..., markdown_body: _Optional[str] = ...) -> None: ...

class Implementation(_message.Message):
    __slots__ = ("task_id", "summary", "changes", "new_files", "notes", "request_peer", "peer_question")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    NEW_FILES_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    REQUEST_PEER_FIELD_NUMBER: _ClassVar[int]
    PEER_QUESTION_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    summary: str
    changes: _containers.RepeatedCompositeFieldContainer[CodeChange]
    new_files: _containers.RepeatedCompositeFieldContainer[FileCreation]
    notes: _containers.RepeatedCompositeFieldContainer[ImplementationNote]
    request_peer: bool
    peer_question: str
    def __init__(self, task_id: _Optional[str] = ..., summary: _Optional[str] = ..., changes: _Optional[_Iterable[_Union[CodeChange, _Mapping]]] = ..., new_files: _Optional[_Iterable[_Union[FileCreation, _Mapping]]] = ..., notes: _Optional[_Iterable[_Union[ImplementationNote, _Mapping]]] = ..., request_peer: bool = ..., peer_question: _Optional[str] = ...) -> None: ...

class CodeChange(_message.Message):
    __slots__ = ("file_path", "type", "search_block", "replace_block", "approximate_line", "reason")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_BLOCK_FIELD_NUMBER: _ClassVar[int]
    REPLACE_BLOCK_FIELD_NUMBER: _ClassVar[int]
    APPROXIMATE_LINE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    type: ChangeType
    search_block: str
    replace_block: str
    approximate_line: int
    reason: str
    def __init__(self, file_path: _Optional[str] = ..., type: _Optional[_Union[ChangeType, str]] = ..., search_block: _Optional[str] = ..., replace_block: _Optional[str] = ..., approximate_line: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...

class FileCreation(_message.Message):
    __slots__ = ("file_path", "content", "purpose", "template_used")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_USED_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    content: str
    purpose: str
    template_used: str
    def __init__(self, file_path: _Optional[str] = ..., content: _Optional[str] = ..., purpose: _Optional[str] = ..., template_used: _Optional[str] = ...) -> None: ...

class ImplementationNote(_message.Message):
    __slots__ = ("type", "note")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    type: str
    note: str
    def __init__(self, type: _Optional[str] = ..., note: _Optional[str] = ...) -> None: ...
