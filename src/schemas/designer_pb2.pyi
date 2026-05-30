import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DesignerOutput(_message.Message):
    __slots__ = ("agent", "status", "confidence", "design", "markdown_body")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    DESIGN_FIELD_NUMBER: _ClassVar[int]
    MARKDOWN_BODY_FIELD_NUMBER: _ClassVar[int]
    agent: str
    status: _common_pb2.Status
    confidence: int
    design: Design
    markdown_body: str
    def __init__(self, agent: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, str]] = ..., confidence: _Optional[int] = ..., design: _Optional[_Union[Design, _Mapping]] = ..., markdown_body: _Optional[str] = ...) -> None: ...

class Design(_message.Message):
    __slots__ = ("title", "summary", "architecture", "components", "approach", "risks", "technical_debt", "estimates")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    APPROACH_FIELD_NUMBER: _ClassVar[int]
    RISKS_FIELD_NUMBER: _ClassVar[int]
    TECHNICAL_DEBT_FIELD_NUMBER: _ClassVar[int]
    ESTIMATES_FIELD_NUMBER: _ClassVar[int]
    title: str
    summary: str
    architecture: ArchitectureDesign
    components: _containers.RepeatedCompositeFieldContainer[_common_pb2.Component]
    approach: ImplementationApproach
    risks: _containers.RepeatedCompositeFieldContainer[_common_pb2.Risk]
    technical_debt: _containers.RepeatedCompositeFieldContainer[_common_pb2.TechnicalDebt]
    estimates: Estimates
    def __init__(self, title: _Optional[str] = ..., summary: _Optional[str] = ..., architecture: _Optional[_Union[ArchitectureDesign, _Mapping]] = ..., components: _Optional[_Iterable[_Union[_common_pb2.Component, _Mapping]]] = ..., approach: _Optional[_Union[ImplementationApproach, _Mapping]] = ..., risks: _Optional[_Iterable[_Union[_common_pb2.Risk, _Mapping]]] = ..., technical_debt: _Optional[_Iterable[_Union[_common_pb2.TechnicalDebt, _Mapping]]] = ..., estimates: _Optional[_Union[Estimates, _Mapping]] = ...) -> None: ...

class ArchitectureDesign(_message.Message):
    __slots__ = ("pattern", "layers", "data_flow", "integrations")
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    DATA_FLOW_FIELD_NUMBER: _ClassVar[int]
    INTEGRATIONS_FIELD_NUMBER: _ClassVar[int]
    pattern: str
    layers: _containers.RepeatedScalarFieldContainer[str]
    data_flow: str
    integrations: _containers.RepeatedCompositeFieldContainer[Integration]
    def __init__(self, pattern: _Optional[str] = ..., layers: _Optional[_Iterable[str]] = ..., data_flow: _Optional[str] = ..., integrations: _Optional[_Iterable[_Union[Integration, _Mapping]]] = ...) -> None: ...

class Integration(_message.Message):
    __slots__ = ("name", "description", "components_involved")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_INVOLVED_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    components_involved: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., components_involved: _Optional[_Iterable[str]] = ...) -> None: ...

class ImplementationApproach(_message.Message):
    __slots__ = ("strategy", "phases", "prerequisites", "success_criteria")
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    PHASES_FIELD_NUMBER: _ClassVar[int]
    PREREQUISITES_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_CRITERIA_FIELD_NUMBER: _ClassVar[int]
    strategy: str
    phases: _containers.RepeatedCompositeFieldContainer[Phase]
    prerequisites: _containers.RepeatedScalarFieldContainer[str]
    success_criteria: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, strategy: _Optional[str] = ..., phases: _Optional[_Iterable[_Union[Phase, _Mapping]]] = ..., prerequisites: _Optional[_Iterable[str]] = ..., success_criteria: _Optional[_Iterable[str]] = ...) -> None: ...

class Phase(_message.Message):
    __slots__ = ("order", "name", "description", "deliverables")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DELIVERABLES_FIELD_NUMBER: _ClassVar[int]
    order: int
    name: str
    description: str
    deliverables: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, order: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., deliverables: _Optional[_Iterable[str]] = ...) -> None: ...

class Estimates(_message.Message):
    __slots__ = ("complexity_score", "files_to_create", "files_to_modify", "estimated_loc", "time_estimate")
    COMPLEXITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    FILES_TO_CREATE_FIELD_NUMBER: _ClassVar[int]
    FILES_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_LOC_FIELD_NUMBER: _ClassVar[int]
    TIME_ESTIMATE_FIELD_NUMBER: _ClassVar[int]
    complexity_score: int
    files_to_create: int
    files_to_modify: int
    estimated_loc: int
    time_estimate: str
    def __init__(self, complexity_score: _Optional[int] = ..., files_to_create: _Optional[int] = ..., files_to_modify: _Optional[int] = ..., estimated_loc: _Optional[int] = ..., time_estimate: _Optional[str] = ...) -> None: ...
