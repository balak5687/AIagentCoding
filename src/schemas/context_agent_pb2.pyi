import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContextAgentOutput(_message.Message):
    __slots__ = ("agent", "status", "confidence", "backend", "frontend", "markdown_body")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    BACKEND_FIELD_NUMBER: _ClassVar[int]
    FRONTEND_FIELD_NUMBER: _ClassVar[int]
    MARKDOWN_BODY_FIELD_NUMBER: _ClassVar[int]
    agent: str
    status: _common_pb2.Status
    confidence: int
    backend: ProjectContext
    frontend: ProjectContext
    markdown_body: str
    def __init__(self, agent: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, str]] = ..., confidence: _Optional[int] = ..., backend: _Optional[_Union[ProjectContext, _Mapping]] = ..., frontend: _Optional[_Union[ProjectContext, _Mapping]] = ..., markdown_body: _Optional[str] = ...) -> None: ...

class ProjectContext(_message.Message):
    __slots__ = ("name", "path", "type", "tech_stack", "architecture", "file_tree", "patterns", "api_endpoints", "imports", "stats")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TECH_STACK_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    FILE_TREE_FIELD_NUMBER: _ClassVar[int]
    PATTERNS_FIELD_NUMBER: _ClassVar[int]
    API_ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    IMPORTS_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    type: str
    tech_stack: TechStack
    architecture: Architecture
    file_tree: FileTree
    patterns: _containers.RepeatedCompositeFieldContainer[Pattern]
    api_endpoints: _containers.RepeatedCompositeFieldContainer[ApiEndpoint]
    imports: _containers.RepeatedCompositeFieldContainer[ImportRelationship]
    stats: ProjectStats
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ..., type: _Optional[str] = ..., tech_stack: _Optional[_Union[TechStack, _Mapping]] = ..., architecture: _Optional[_Union[Architecture, _Mapping]] = ..., file_tree: _Optional[_Union[FileTree, _Mapping]] = ..., patterns: _Optional[_Iterable[_Union[Pattern, _Mapping]]] = ..., api_endpoints: _Optional[_Iterable[_Union[ApiEndpoint, _Mapping]]] = ..., imports: _Optional[_Iterable[_Union[ImportRelationship, _Mapping]]] = ..., stats: _Optional[_Union[ProjectStats, _Mapping]] = ...) -> None: ...

class TechStack(_message.Message):
    __slots__ = ("language", "framework", "database", "libraries", "version")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FRAMEWORK_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    language: str
    framework: str
    database: str
    libraries: _containers.RepeatedScalarFieldContainer[str]
    version: str
    def __init__(self, language: _Optional[str] = ..., framework: _Optional[str] = ..., database: _Optional[str] = ..., libraries: _Optional[_Iterable[str]] = ..., version: _Optional[str] = ...) -> None: ...

class Architecture(_message.Message):
    __slots__ = ("pattern", "layers", "directories")
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    DIRECTORIES_FIELD_NUMBER: _ClassVar[int]
    pattern: str
    layers: _containers.RepeatedScalarFieldContainer[str]
    directories: _containers.RepeatedCompositeFieldContainer[DirectoryRole]
    def __init__(self, pattern: _Optional[str] = ..., layers: _Optional[_Iterable[str]] = ..., directories: _Optional[_Iterable[_Union[DirectoryRole, _Mapping]]] = ...) -> None: ...

class DirectoryRole(_message.Message):
    __slots__ = ("path", "role", "file_count")
    PATH_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    FILE_COUNT_FIELD_NUMBER: _ClassVar[int]
    path: str
    role: str
    file_count: int
    def __init__(self, path: _Optional[str] = ..., role: _Optional[str] = ..., file_count: _Optional[int] = ...) -> None: ...

class FileTree(_message.Message):
    __slots__ = ("directories", "total_files", "total_directories")
    DIRECTORIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FILES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DIRECTORIES_FIELD_NUMBER: _ClassVar[int]
    directories: _containers.RepeatedCompositeFieldContainer[DirectoryNode]
    total_files: int
    total_directories: int
    def __init__(self, directories: _Optional[_Iterable[_Union[DirectoryNode, _Mapping]]] = ..., total_files: _Optional[int] = ..., total_directories: _Optional[int] = ...) -> None: ...

class DirectoryNode(_message.Message):
    __slots__ = ("path", "files", "subdirectories", "purpose")
    PATH_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    SUBDIRECTORIES_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    path: str
    files: _containers.RepeatedScalarFieldContainer[str]
    subdirectories: _containers.RepeatedScalarFieldContainer[str]
    purpose: str
    def __init__(self, path: _Optional[str] = ..., files: _Optional[_Iterable[str]] = ..., subdirectories: _Optional[_Iterable[str]] = ..., purpose: _Optional[str] = ...) -> None: ...

class Pattern(_message.Message):
    __slots__ = ("name", "description", "examples", "code_snippet")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    CODE_SNIPPET_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    examples: _containers.RepeatedScalarFieldContainer[str]
    code_snippet: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., examples: _Optional[_Iterable[str]] = ..., code_snippet: _Optional[str] = ...) -> None: ...

class ApiEndpoint(_message.Message):
    __slots__ = ("method", "path", "handler_file", "handler_function", "requires_auth", "description")
    METHOD_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    HANDLER_FILE_FIELD_NUMBER: _ClassVar[int]
    HANDLER_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_AUTH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    method: str
    path: str
    handler_file: str
    handler_function: str
    requires_auth: bool
    description: str
    def __init__(self, method: _Optional[str] = ..., path: _Optional[str] = ..., handler_file: _Optional[str] = ..., handler_function: _Optional[str] = ..., requires_auth: bool = ..., description: _Optional[str] = ...) -> None: ...

class ImportRelationship(_message.Message):
    __slots__ = ("from_file", "imports", "from_module", "usage_count")
    FROM_FILE_FIELD_NUMBER: _ClassVar[int]
    IMPORTS_FIELD_NUMBER: _ClassVar[int]
    FROM_MODULE_FIELD_NUMBER: _ClassVar[int]
    USAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    from_file: str
    imports: str
    from_module: str
    usage_count: int
    def __init__(self, from_file: _Optional[str] = ..., imports: _Optional[str] = ..., from_module: _Optional[str] = ..., usage_count: _Optional[int] = ...) -> None: ...

class ProjectStats(_message.Message):
    __slots__ = ("total_files", "lines_of_code", "routes_count", "services_count", "models_count", "widgets_count", "screens_count")
    TOTAL_FILES_FIELD_NUMBER: _ClassVar[int]
    LINES_OF_CODE_FIELD_NUMBER: _ClassVar[int]
    ROUTES_COUNT_FIELD_NUMBER: _ClassVar[int]
    SERVICES_COUNT_FIELD_NUMBER: _ClassVar[int]
    MODELS_COUNT_FIELD_NUMBER: _ClassVar[int]
    WIDGETS_COUNT_FIELD_NUMBER: _ClassVar[int]
    SCREENS_COUNT_FIELD_NUMBER: _ClassVar[int]
    total_files: int
    lines_of_code: int
    routes_count: int
    services_count: int
    models_count: int
    widgets_count: int
    screens_count: int
    def __init__(self, total_files: _Optional[int] = ..., lines_of_code: _Optional[int] = ..., routes_count: _Optional[int] = ..., services_count: _Optional[int] = ..., models_count: _Optional[int] = ..., widgets_count: _Optional[int] = ..., screens_count: _Optional[int] = ...) -> None: ...
