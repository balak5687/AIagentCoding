import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.protocol import AgentMessage


def test_parse_simple_message():
    """Test parsing a simple agent message"""
    markdown = """---
agent: designer
status: complete
confidence: 85
---

# Design Document

## Requirements Analysis

This is a test requirement.

## Architecture Overview

Simple architecture for testing.
"""

    msg = AgentMessage(markdown)

    assert msg.metadata["agent"] == "designer"
    assert msg.metadata["status"] == "complete"
    assert msg.metadata["confidence"] == 85

    assert "Requirements Analysis" in msg.sections
    assert "Architecture Overview" in msg.sections
    assert "test requirement" in msg.sections["Requirements Analysis"]

    print("✓ test_parse_simple_message passed")


def test_extract_code_changes():
    """Test extracting SEARCH/REPLACE blocks"""
    markdown = """---
agent: coder
status: complete
---

# Implementation Report

## Changes

### File: test.py

<<<<<<< SEARCH
def old_function():
    pass
=======
def new_function():
    print("updated")
>>>>>>> REPLACE

### File: another.py

<<<<<<< SEARCH
x = 1
=======
x = 2
>>>>>>> REPLACE
"""

    msg = AgentMessage(markdown)
    changes = msg.extract_code_changes()

    assert len(changes) == 2
    assert "old_function" in changes[0]["search"]
    assert "new_function" in changes[0]["replace"]
    assert "x = 1" in changes[1]["search"]
    assert "x = 2" in changes[1]["replace"]

    print("✓ test_extract_code_changes passed")


if __name__ == "__main__":
    test_parse_simple_message()
    test_extract_code_changes()
    print("\nAll tests passed!")
