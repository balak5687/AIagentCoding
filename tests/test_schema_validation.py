#!/usr/bin/env python3
"""
Test Schema Validation

Verifies that Protobuf schema validation works correctly.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.schema_validator import validate_agent_output, ValidationError


def test_valid_designer_output():
    """Test valid designer output passes validation"""

    raw_output = """---
agent: designer
status: COMPLETE
confidence: 88

design:
  title: "Dashboard Module"
  summary: "Implement dashboard with 7 components"

  architecture:
    pattern: "3-layer"
    layers: ["routes", "services", "repositories"]
    data_flow: "Routes → Services → Repositories"

  components:
    - name: "Dashboard Routes"
      type: "route"
      files:
        - path: "app/routes/dashboard.py"
          description: "API endpoints"
      description: "5 REST endpoints"
      dependencies: ["dashboard_service"]

  approach:
    strategy: "incremental"
    success_criteria:
      - "All endpoints return valid data"

  risks:
    - id: "perf-001"
      description: "May be slow"
      severity: MEDIUM
      mitigation: "Add caching"

  estimates:
    complexity_score: 6
    files_to_create: 2
    files_to_modify: 1
    estimated_loc: 300
    time_estimate: "3 hours"
---

# Design Document

This is the design...
"""

    try:
        is_valid, proto_msg, yaml_data, markdown = validate_agent_output(
            "designer",
            raw_output,
            strict=True
        )

        print("✓ Valid designer output passed validation")
        print(f"  Agent: {proto_msg.agent}")
        print(f"  Status: {proto_msg.status}")
        print(f"  Confidence: {proto_msg.confidence}")
        print(f"  Components: {len(proto_msg.design.components)}")
        print(f"  Complexity: {proto_msg.design.estimates.complexity_score}/10")
        return True

    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
        return False


def test_invalid_confidence():
    """Test invalid confidence score fails validation"""

    raw_output = """---
agent: designer
status: COMPLETE
confidence: 150
---

# Design
"""

    try:
        is_valid, proto_msg, yaml_data, markdown = validate_agent_output(
            "designer",
            raw_output,
            strict=True
        )
        print("✗ Should have failed - confidence out of range")
        return False

    except ValidationError as e:
        print(f"✓ Correctly rejected invalid confidence: {e}")
        return True


def test_missing_required_field():
    """Test missing required field fails validation"""

    raw_output = """---
agent: designer
status: COMPLETE
---

# Design
"""

    try:
        is_valid, proto_msg, yaml_data, markdown = validate_agent_output(
            "designer",
            raw_output,
            strict=True
        )
        print("✗ Should have failed - missing confidence")
        return False

    except Exception as e:
        print(f"✓ Correctly rejected missing field: {type(e).__name__}")
        return True


def test_complete_without_components():
    """Test designer marked COMPLETE without components fails"""

    raw_output = """---
agent: designer
status: COMPLETE
confidence: 80

design:
  title: "Test"
  summary: "Test"
  components: []
---

# Design
"""

    try:
        is_valid, proto_msg, yaml_data, markdown = validate_agent_output(
            "designer",
            raw_output,
            strict=True
        )
        print("✗ Should have failed - COMPLETE but no components")
        return False

    except ValidationError as e:
        print(f"✓ Correctly rejected COMPLETE without components: {e}")
        return True


def main():
    """Run all tests"""
    print("="*60)
    print("Schema Validation Tests")
    print("="*60)
    print()

    tests = [
        ("Valid designer output", test_valid_designer_output),
        ("Invalid confidence score", test_invalid_confidence),
        ("Missing required field", test_missing_required_field),
        ("Complete without components", test_complete_without_components),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\nTest: {name}")
        print("-" * 60)
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
