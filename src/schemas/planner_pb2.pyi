import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerOutput(_message.Message):
    __slots__ = ("agent", "status", "confidence", "plan", "markdown_body")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    PLAN_FIELD_NUMBER: _ClassVar[int]
    MARKDOWN_BODY_FIELD_NUMBER: _ClassVar[int]
    agent: str
    status: _common_pb2.Status
    confidence: int
    plan: Plan
    markdown_body: str
    def __init__(self, agent: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, str]] = ..., confidence: _Optional[int] = ..., plan: _Optional[_Union[Plan, _Mapping]] = ..., markdown_body: _Optional[str] = ...) -> None: ...

class Plan(_message.Message):
    __slots__ = ("title", "summary", "tasks", "strategy", "dependencies")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    title: str
    summary: str
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    strategy: ExecutionStrategy
    dependencies: DependencyGraph
    def __init__(self, title: _Optional[str] = ..., summary: _Optional[str] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ..., strategy: _Optional[_Union[ExecutionStrategy, _Mapping]] = ..., dependencies: _Optional[_Union[DependencyGraph, _Mapping]] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("id", "name", "description", "files", "depends_on", "blocks", "approach", "playbook", "agent", "complexity", "estimated_time", "test_cases")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    DEPENDS_ON_FIELD_NUMBER: _ClassVar[int]
    BLOCKS_FIELD_NUMBER: _ClassVar[int]
    APPROACH_FIELD_NUMBER: _ClassVar[int]
    PLAYBOOK_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    COMPLEXITY_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TIME_FIELD_NUMBER: _ClassVar[int]
    TEST_CASES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    files: _containers.RepeatedCompositeFieldContainer[_common_pb2.FileReference]
    depends_on: _containers.RepeatedScalarFieldContainer[str]
    blocks: _containers.RepeatedScalarFieldContainer[str]
    approach: str
    playbook: str
    agent: str
    complexity: int
    estimated_time: str
    test_cases: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., files: _Optional[_Iterable[_Union[_common_pb2.FileReference, _Mapping]]] = ..., depends_on: _Optional[_Iterable[str]] = ..., blocks: _Optional[_Iterable[str]] = ..., approach: _Optional[str] = ..., playbook: _Optional[str] = ..., agent: _Optional[str] = ..., complexity: _Optional[int] = ..., estimated_time: _Optional[str] = ..., test_cases: _Optional[_Iterable[str]] = ...) -> None: ...

class ExecutionStrategy(_message.Message):
    __slots__ = ("type", "phases", "max_parallel_tasks")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PHASES_FIELD_NUMBER: _ClassVar[int]
    MAX_PARALLEL_TASKS_FIELD_NUMBER: _ClassVar[int]
    type: str
    phases: _containers.RepeatedCompositeFieldContainer[ExecutionPhase]
    max_parallel_tasks: int
    def __init__(self, type: _Optional[str] = ..., phases: _Optional[_Iterable[_Union[ExecutionPhase, _Mapping]]] = ..., max_parallel_tasks: _Optional[int] = ...) -> None: ...

class ExecutionPhase(_message.Message):
    __slots__ = ("order", "name", "task_ids", "execution_mode")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_MODE_FIELD_NUMBER: _ClassVar[int]
    order: int
    name: str
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    execution_mode: str
    def __init__(self, order: _Optional[int] = ..., name: _Optional[str] = ..., task_ids: _Optional[_Iterable[str]] = ..., execution_mode: _Optional[str] = ...) -> None: ...

class DependencyGraph(_message.Message):
    __slots__ = ("edges", "max_depth", "critical_path")
    EDGES_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    CRITICAL_PATH_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[DependencyEdge]
    max_depth: int
    critical_path: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, edges: _Optional[_Iterable[_Union[DependencyEdge, _Mapping]]] = ..., max_depth: _Optional[int] = ..., critical_path: _Optional[_Iterable[str]] = ...) -> None: ...

class DependencyEdge(_message.Message):
    __slots__ = ("from_task", "to_task", "relationship")
    FROM_TASK_FIELD_NUMBER: _ClassVar[int]
    TO_TASK_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_FIELD_NUMBER: _ClassVar[int]
    from_task: str
    to_task: str
    relationship: str
    def __init__(self, from_task: _Optional[str] = ..., to_task: _Optional[str] = ..., relationship: _Optional[str] = ...) -> None: ...
