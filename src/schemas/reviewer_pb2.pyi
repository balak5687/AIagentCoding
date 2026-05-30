import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReviewDecision(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DECISION_UNSPECIFIED: _ClassVar[ReviewDecision]
    APPROVED: _ClassVar[ReviewDecision]
    NEEDS_MINOR_FIXES: _ClassVar[ReviewDecision]
    REJECTED: _ClassVar[ReviewDecision]

class IssueCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CATEGORY_UNSPECIFIED: _ClassVar[IssueCategory]
    SECURITY: _ClassVar[IssueCategory]
    PERFORMANCE: _ClassVar[IssueCategory]
    CORRECTNESS: _ClassVar[IssueCategory]
    STYLE: _ClassVar[IssueCategory]
    MAINTAINABILITY: _ClassVar[IssueCategory]
    TESTING: _ClassVar[IssueCategory]
    DOCUMENTATION: _ClassVar[IssueCategory]
DECISION_UNSPECIFIED: ReviewDecision
APPROVED: ReviewDecision
NEEDS_MINOR_FIXES: ReviewDecision
REJECTED: ReviewDecision
CATEGORY_UNSPECIFIED: IssueCategory
SECURITY: IssueCategory
PERFORMANCE: IssueCategory
CORRECTNESS: IssueCategory
STYLE: IssueCategory
MAINTAINABILITY: IssueCategory
TESTING: IssueCategory
DOCUMENTATION: IssueCategory

class ReviewerOutput(_message.Message):
    __slots__ = ("agent", "status", "confidence", "review", "markdown_body")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    REVIEW_FIELD_NUMBER: _ClassVar[int]
    MARKDOWN_BODY_FIELD_NUMBER: _ClassVar[int]
    agent: str
    status: _common_pb2.Status
    confidence: int
    review: Review
    markdown_body: str
    def __init__(self, agent: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, str]] = ..., confidence: _Optional[int] = ..., review: _Optional[_Union[Review, _Mapping]] = ..., markdown_body: _Optional[str] = ...) -> None: ...

class Review(_message.Message):
    __slots__ = ("task_id", "decision", "issues", "strengths", "suggestions", "quality")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    ISSUES_FIELD_NUMBER: _ClassVar[int]
    STRENGTHS_FIELD_NUMBER: _ClassVar[int]
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    decision: ReviewDecision
    issues: _containers.RepeatedCompositeFieldContainer[ReviewIssue]
    strengths: _containers.RepeatedScalarFieldContainer[str]
    suggestions: _containers.RepeatedScalarFieldContainer[str]
    quality: QualityAssessment
    def __init__(self, task_id: _Optional[str] = ..., decision: _Optional[_Union[ReviewDecision, str]] = ..., issues: _Optional[_Iterable[_Union[ReviewIssue, _Mapping]]] = ..., strengths: _Optional[_Iterable[str]] = ..., suggestions: _Optional[_Iterable[str]] = ..., quality: _Optional[_Union[QualityAssessment, _Mapping]] = ...) -> None: ...

class ReviewIssue(_message.Message):
    __slots__ = ("id", "category", "severity", "description", "file_path", "line_number", "suggestion", "blocking")
    ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    SUGGESTION_FIELD_NUMBER: _ClassVar[int]
    BLOCKING_FIELD_NUMBER: _ClassVar[int]
    id: str
    category: IssueCategory
    severity: _common_pb2.Severity
    description: str
    file_path: str
    line_number: int
    suggestion: str
    blocking: bool
    def __init__(self, id: _Optional[str] = ..., category: _Optional[_Union[IssueCategory, str]] = ..., severity: _Optional[_Union[_common_pb2.Severity, str]] = ..., description: _Optional[str] = ..., file_path: _Optional[str] = ..., line_number: _Optional[int] = ..., suggestion: _Optional[str] = ..., blocking: bool = ...) -> None: ...

class QualityAssessment(_message.Message):
    __slots__ = ("code_quality_score", "security_score", "maintainability_score", "test_coverage_estimate", "follows_patterns", "overall_comment")
    CODE_QUALITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    SECURITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    MAINTAINABILITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    TEST_COVERAGE_ESTIMATE_FIELD_NUMBER: _ClassVar[int]
    FOLLOWS_PATTERNS_FIELD_NUMBER: _ClassVar[int]
    OVERALL_COMMENT_FIELD_NUMBER: _ClassVar[int]
    code_quality_score: int
    security_score: int
    maintainability_score: int
    test_coverage_estimate: int
    follows_patterns: bool
    overall_comment: str
    def __init__(self, code_quality_score: _Optional[int] = ..., security_score: _Optional[int] = ..., maintainability_score: _Optional[int] = ..., test_coverage_estimate: _Optional[int] = ..., follows_patterns: bool = ..., overall_comment: _Optional[str] = ...) -> None: ...
