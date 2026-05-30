"""
Schema Validator - Validates agent outputs against Protobuf schemas

Agents output YAML + Markdown, we validate against Protobuf definitions.
"""

import yaml
from typing import Dict, Any, Tuple, Optional
from google.protobuf import json_format
from google.protobuf.message import Message

# Import generated protobuf schemas
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas import (
    github_scanner_pb2,
    context_agent_pb2,
    designer_pb2,
    planner_pb2,
    coder_pb2,
    reviewer_pb2,
    common_pb2
)


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class SchemaValidator:
    """Validates agent outputs against Protobuf schemas"""

    # Map agent names to their protobuf message classes
    SCHEMA_MAP = {
        "github_scanner": github_scanner_pb2.GitHubScannerOutput,
        "context_agent": context_agent_pb2.ContextAgentOutput,
        "designer": designer_pb2.DesignerOutput,
        "planner": planner_pb2.PlannerOutput,
        "coder": coder_pb2.CoderOutput,
        "reviewer": reviewer_pb2.ReviewerOutput,
    }

    @classmethod
    def validate(
        cls,
        agent_name: str,
        yaml_data: Dict[str, Any],
        markdown_body: str,
        strict: bool = True
    ) -> Tuple[bool, Optional[Message], Optional[str]]:
        """
        Validate agent output against its schema.

        Args:
            agent_name: Name of the agent (e.g., "designer")
            yaml_data: Parsed YAML frontmatter
            markdown_body: Markdown content
            strict: If True, fail on any validation error

        Returns:
            (is_valid, protobuf_message, error_message)
        """
        # Get schema class
        schema_class = cls.SCHEMA_MAP.get(agent_name)
        if not schema_class:
            error = f"Unknown agent: {agent_name}"
            if strict:
                raise ValidationError(error)
            return (False, None, error)

        try:
            # Create protobuf message instance
            message = schema_class()

            # Add markdown_body to yaml_data for validation
            yaml_data_with_body = yaml_data.copy()
            yaml_data_with_body["markdown_body"] = markdown_body

            # Convert YAML dict to protobuf message
            json_format.ParseDict(yaml_data_with_body, message, ignore_unknown_fields=not strict)

            # Additional validation
            validation_errors = cls._validate_business_rules(agent_name, message)
            if validation_errors:
                error_msg = "; ".join(validation_errors)
                if strict:
                    raise ValidationError(error_msg)
                return (False, message, error_msg)

            return (True, message, None)

        except json_format.ParseError as e:
            error = f"Schema validation failed: {str(e)}"
            if strict:
                raise ValidationError(error)
            return (False, None, error)

        except Exception as e:
            error = f"Unexpected validation error: {str(e)}"
            if strict:
                raise ValidationError(error)
            return (False, None, error)

    @classmethod
    def _validate_business_rules(cls, agent_name: str, message: Message) -> list[str]:
        """
        Validate business rules beyond schema structure.

        Args:
            agent_name: Name of the agent
            message: Protobuf message to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Common validation: confidence score
        if hasattr(message, "confidence"):
            if message.confidence < 0 or message.confidence > 100:
                errors.append(f"Confidence must be 0-100, got {message.confidence}")

        # Agent-specific validation
        if agent_name == "designer":
            if message.status == common_pb2.COMPLETE:
                if not message.design.components:
                    errors.append("Designer marked complete but has no components")
                if message.confidence < 60:
                    errors.append(f"Designer confidence too low for COMPLETE status: {message.confidence}")

        elif agent_name == "planner":
            if message.status == common_pb2.COMPLETE:
                if not message.plan.tasks:
                    errors.append("Planner marked complete but has no tasks")
                # Check for circular dependencies
                errors.extend(cls._check_circular_dependencies(message.plan))

        elif agent_name == "coder":
            if message.status == common_pb2.COMPLETE:
                impl = message.implementation
                if not impl.changes and not impl.new_files:
                    errors.append("Coder marked complete but has no changes or new files")

        elif agent_name == "reviewer":
            if message.status == common_pb2.APPROVED:
                # If approved, blocking issues should be resolved
                for issue in message.review.issues:
                    if issue.blocking and issue.severity in [common_pb2.HIGH, common_pb2.CRITICAL]:
                        errors.append(f"Cannot approve with blocking {issue.severity} issue: {issue.id}")

        return errors

    @classmethod
    def _check_circular_dependencies(cls, plan) -> list[str]:
        """Check for circular dependencies in task graph"""
        errors = []

        # Build adjacency list
        graph = {}
        for task in plan.tasks:
            graph[task.id] = task.depends_on

        # DFS to detect cycles
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id, visited, set()):
                    errors.append(f"Circular dependency detected involving task {task_id}")
                    break

        return errors


def validate_agent_output(
    agent_name: str,
    raw_output: str,
    strict: bool = True
) -> Tuple[bool, Optional[Message], Dict[str, Any], str]:
    """
    Convenience function to parse and validate agent output.

    Args:
        agent_name: Name of the agent
        raw_output: Raw markdown + YAML output from agent
        strict: If True, raise ValidationError on failure

    Returns:
        (is_valid, protobuf_message, yaml_data, markdown_body)
    """
    from .protocol import AgentMessage

    # Parse with existing protocol parser
    try:
        parsed = AgentMessage(raw_output)
        yaml_data = parsed.metadata
        markdown_body = parsed.raw
    except Exception as e:
        if strict:
            raise ValidationError(f"Failed to parse agent output: {e}")
        return (False, None, {}, "")

    # Validate against schema
    is_valid, proto_msg, error = SchemaValidator.validate(
        agent_name,
        yaml_data,
        markdown_body,
        strict=strict
    )

    return (is_valid, proto_msg, yaml_data, markdown_body)
