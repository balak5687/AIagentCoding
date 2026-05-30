#!/usr/bin/env python3
"""
Test Reviewer Agent — review coder output for task_1
"""
import sys
from pathlib import Path
from src.core.agent_runner import AgentRunner
from src.brain import client as brain_client

TARGET_FILE = "/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/dashboard.py"

def main():
    print("=" * 80)
    print("TESTING REVIEWER AGENT — task_1: Backend Dashboard Models")
    print("=" * 80)
    print()

    if not brain_client.is_running():
        print("❌ Brain Server not running.")
        return 1

    s = brain_client.status()
    print(f"✓ Brain Server running — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")

    coder_output = Path("coder_output_task1.md").read_text()
    current_file = Path(TARGET_FILE).read_text()
    print(f"✓ Coder output loaded ({len(coder_output)} chars)")
    print()

    runner = AgentRunner(
        mode="claude-code",
        config={"debug": True, "timeout_seconds": 300}
    )

    context = {
        "task": {
            "id": "task_1",
            "name": "Backend — Dashboard Alert Models & Supply Issue Models",
            "description": "Add DashboardAlert, JobSnapshot, SupplyIssue, SearchResult, NotificationItem Pydantic models to dashboard.py",
            "files": TARGET_FILE,
        },
        "code_changes": coder_output,
        "current_file_state": current_file,
        "review_criteria": [
            "All 5 models present: DashboardAlert, JobSnapshot, SupplyIssue, SearchResult, NotificationItem",
            "Each model follows existing pattern: BaseModel, Field() with descriptions, Config class",
            "Optional fields use Optional[str] with default=None",
            "No existing models modified or removed",
            "No security issues (no eval, no dynamic execution, no secrets)",
            "Type hints are correct and consistent",
            "Field descriptions are meaningful",
        ]
    }

    print("=" * 80)
    print("RUNNING REVIEWER AGENT (sonnet, 1M context)...")
    print("=" * 80)
    print()

    try:
        result = runner.run("reviewer", context, max_retries=2)

        print()
        print("=" * 80)
        print("REVIEWER OUTPUT")
        print("=" * 80)
        print()
        print("METADATA:")
        for k, v in result.metadata.items():
            print(f"  {k}: {v}")
        print()
        print("CONTENT:")
        print(result.content)

        output_file = Path("reviewer_output_task1.md")
        with open(output_file, "w") as f:
            f.write("# Reviewer Output — task_1\n\n## Metadata\n\n")
            for k, v in result.metadata.items():
                f.write(f"- **{k}**: {v}\n")
            f.write("\n## Review\n\n")
            f.write(result.content)

        decision = result.metadata.get("status", "unknown")
        print()
        print(f"{'✅' if decision == 'approved' else '⚠️' if decision == 'needs_minor_fixes' else '❌'} DECISION: {decision.upper()}")
        print(f"OUTPUT SAVED TO: {output_file}")
        print("=" * 80)
        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
