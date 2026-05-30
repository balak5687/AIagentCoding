#!/usr/bin/env python3
"""
Test Coder Agent — task_1: Add Pydantic models for Dashboard extensions
"""
import sys
from pathlib import Path
from src.core.agent_runner import AgentRunner
from src.brain import client as brain_client

TARGET_FILE = "/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/dashboard.py"

def main():
    print("=" * 80)
    print("TESTING CODER AGENT — task_1: Backend Dashboard Models")
    print("=" * 80)
    print()

    if not brain_client.is_running():
        print("❌ Brain Server not running. Start it first.")
        return 1

    s = brain_client.status()
    print(f"✓ Brain Server running — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")

    existing_code = Path(TARGET_FILE).read_text()
    print(f"✓ Existing dashboard.py loaded ({len(existing_code)} chars)")
    print()

    runner = AgentRunner(
        mode="claude-code",
        config={"debug": True, "timeout_seconds": 600}
    )

    task = {
        "id": "task_1",
        "name": "Backend — Dashboard Alert Models & Supply Issue Models",
        "description": (
            "Add new Pydantic models to app/models/dashboard.py: "
            "DashboardAlert, JobSnapshot, SupplyIssue, SearchResult, NotificationItem. "
            "Follow the exact existing pattern: BaseModel, Field() with descriptions, "
            "Optional types, and inner Config class with from_attributes=True. "
            "Do NOT modify or remove any existing models in the file."
        ),
        "files": TARGET_FILE,
        "dependencies": [],
        "approach": "cognitive",
        "existing_code": existing_code,
        "model_specs": {
            "DashboardAlert": {
                "fields": ["id:str", "type:str", "message:str", "severity:str (critical|warning)",
                           "related_entity_id:Optional[str]", "timestamp:str"]
            },
            "JobSnapshot": {
                "fields": ["job_id:str", "vehicle:str", "issue_type:str", "status:str",
                           "technician:Optional[str]", "service_status:str",
                           "delivery_status:str", "delay_reason:Optional[str]",
                           "days_elapsed:int"]
            },
            "SupplyIssue": {
                "fields": ["po_id:str", "supplier:str", "status:str",
                           "affected_jobs:int", "expected_delivery_date:Optional[str]"]
            },
            "SearchResult": {
                "fields": ["entity_type:str (job|customer|vehicle)", "entity_id:str",
                           "title:str", "subtitle:Optional[str]", "url:Optional[str]"]
            },
            "NotificationItem": {
                "fields": ["id:str", "message:str", "type:str",
                           "read:bool", "timestamp:str", "related_entity_id:Optional[str]"]
            }
        },
        "constraints": [
            "Follow existing pattern in the file exactly",
            "Use from pydantic import BaseModel, Field",
            "All Optional fields default to None",
            "Include class Config with from_attributes = True on each model",
            "Do NOT modify existing models",
            "Output SEARCH/REPLACE blocks only — no prose explanations in the Changes section"
        ]
    }

    print("=" * 80)
    print("RUNNING CODER AGENT (sonnet, 1M context)...")
    print("=" * 80)
    print()

    try:
        result = runner.run("coder", task, max_retries=2)

        print()
        print("=" * 80)
        print("CODER OUTPUT")
        print("=" * 80)
        print()
        print("METADATA:")
        for k, v in result.metadata.items():
            print(f"  {k}: {v}")
        print()
        print("CONTENT:")
        print(result.content)

        output_file = Path("coder_output_task1.md")
        with open(output_file, "w") as f:
            f.write("# Coder Output — task_1\n\n## Metadata\n\n")
            for k, v in result.metadata.items():
                f.write(f"- **{k}**: {v}\n")
            f.write("\n## Implementation\n\n")
            f.write(result.content)

        print()
        print(f"✅ OUTPUT SAVED TO: {output_file}")
        print("=" * 80)
        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
