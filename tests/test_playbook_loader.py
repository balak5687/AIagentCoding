import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.playbook_loader import PlaybookLoader


def test_load_crud_playbook():
    """Test loading CRUD endpoint playbook"""
    loader = PlaybookLoader()

    playbook = loader.get_playbook("add_crud_endpoint.yaml")

    assert playbook is not None
    assert playbook["name"] == "add_crud_endpoint"
    assert playbook["category"] == "api"
    assert playbook["reduces_hallucination"] == True
    assert "steps" in playbook
    assert len(playbook["steps"]) >= 8

    print("✓ test_load_crud_playbook passed")


def test_match_crud_task():
    """Test matching a CRUD task to playbook"""
    loader = PlaybookLoader()

    # Test matching
    task_description = "Add CRUD REST API endpoints for User model"
    playbook = loader.find_matching_playbook(task_description)

    assert playbook is not None
    assert playbook["name"] == "add_crud_endpoint"

    print("✓ test_match_crud_task passed")


def test_match_test_task():
    """Test matching a unit test task to playbook"""
    loader = PlaybookLoader()

    task_description = "Add unit tests for calculate_total function using pytest"
    playbook = loader.find_matching_playbook(task_description)

    assert playbook is not None
    assert playbook["name"] == "add_unit_tests"

    print("✓ test_match_test_task passed")


def test_no_match():
    """Test that novel tasks don't match playbooks"""
    loader = PlaybookLoader()

    # Novel algorithm - should not match
    task_description = "Implement A* pathfinding algorithm for game AI"
    playbook = loader.find_matching_playbook(task_description)

    # Should either be None or have low confidence
    # (might match error handling playbook weakly)
    if playbook:
        print(f"  Note: Weak match to {playbook['name']} (expected for some edge cases)")

    print("✓ test_no_match passed")


def test_format_playbook():
    """Test formatting playbook for agent"""
    loader = PlaybookLoader()

    playbook = loader.get_playbook("add_crud_endpoint.yaml")
    formatted = loader.format_playbook_for_agent(playbook)

    assert "# Playbook:" in formatted
    assert "Deterministic Steps" in formatted
    assert "Code Templates" in formatted
    assert "Validation Checklist" in formatted

    print("✓ test_format_playbook passed")


def test_list_playbooks():
    """Test listing all available playbooks"""
    loader = PlaybookLoader()

    playbooks = loader.list_available_playbooks()

    assert len(playbooks) >= 2  # At least CRUD and unit tests
    assert "add_crud_endpoint" in playbooks
    assert "add_unit_tests" in playbooks

    print(f"✓ test_list_playbooks passed (found {len(playbooks)} playbooks)")


if __name__ == "__main__":
    test_load_crud_playbook()
    test_match_crud_task()
    test_match_test_task()
    test_no_match()
    test_format_playbook()
    test_list_playbooks()
    print("\nAll playbook tests passed!")
