import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GitHubScannerOutput(_message.Message):
    __slots__ = ("agent", "status", "confidence", "issue", "markdown_body")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    ISSUE_FIELD_NUMBER: _ClassVar[int]
    MARKDOWN_BODY_FIELD_NUMBER: _ClassVar[int]
    agent: str
    status: _common_pb2.Status
    confidence: int
    issue: IssueData
    markdown_body: str
    def __init__(self, agent: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, str]] = ..., confidence: _Optional[int] = ..., issue: _Optional[_Union[IssueData, _Mapping]] = ..., markdown_body: _Optional[str] = ...) -> None: ...

class IssueData(_message.Message):
    __slots__ = ("number", "title", "body", "url", "labels", "issue_type", "components", "requirements")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    ISSUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    number: int
    title: str
    body: str
    url: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    issue_type: str
    components: _containers.RepeatedCompositeFieldContainer[IssueComponent]
    requirements: Requirements
    def __init__(self, number: _Optional[int] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., url: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ..., issue_type: _Optional[str] = ..., components: _Optional[_Iterable[_Union[IssueComponent, _Mapping]]] = ..., requirements: _Optional[_Union[Requirements, _Mapping]] = ...) -> None: ...

class IssueComponent(_message.Message):
    __slots__ = ("name", "description", "sub_components", "backend_required", "frontend_required", "database_required")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SUB_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    BACKEND_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    FRONTEND_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    DATABASE_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    sub_components: _containers.RepeatedScalarFieldContainer[str]
    backend_required: bool
    frontend_required: bool
    database_required: bool
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., sub_components: _Optional[_Iterable[str]] = ..., backend_required: bool = ..., frontend_required: bool = ..., database_required: bool = ...) -> None: ...

class Requirements(_message.Message):
    __slots__ = ("functional", "non_functional", "acceptance_criteria", "user_stories", "data_sources")
    FUNCTIONAL_FIELD_NUMBER: _ClassVar[int]
    NON_FUNCTIONAL_FIELD_NUMBER: _ClassVar[int]
    ACCEPTANCE_CRITERIA_FIELD_NUMBER: _ClassVar[int]
    USER_STORIES_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCES_FIELD_NUMBER: _ClassVar[int]
    functional: _containers.RepeatedScalarFieldContainer[str]
    non_functional: _containers.RepeatedScalarFieldContainer[str]
    acceptance_criteria: _containers.RepeatedScalarFieldContainer[str]
    user_stories: _containers.RepeatedScalarFieldContainer[str]
    data_sources: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, functional: _Optional[_Iterable[str]] = ..., non_functional: _Optional[_Iterable[str]] = ..., acceptance_criteria: _Optional[_Iterable[str]] = ..., user_stories: _Optional[_Iterable[str]] = ..., data_sources: _Optional[_Iterable[str]] = ...) -> None: ...
