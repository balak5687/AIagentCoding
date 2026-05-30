#!/usr/bin/env python3
"""
End-to-end test: task_2 (Alerts Engine in DashboardService)
Daemons run in tmux (start_agents.sh). Brain already running.
This script drops the task on the bus and waits for completion.
"""
import sys
import asyncio
import subprocess
import time
from pathlib import Path
from src.bus import FileMessageBus
from src.workflows.conversation import ConversationLoop
from src.brain import client as brain_client

TARGET_FILE = "/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py"

TASK = {
    "id": "task_2",
    "name": "Backend — Alerts Engine in DashboardService",
    "description": (
        "Add alert generation logic to DashboardService. "
        "Implement private methods: _get_blocked_jobs(), _get_supplier_delays(), "
        "_get_low_stock_alerts(), _get_unpaid_invoices(), _get_delayed_jobs(). "
        "Add public get_alerts() that aggregates all, sorts by severity (critical first), "
        "returns top 10 as List[DashboardAlert]. "
        "Import DashboardAlert from app.models.dashboard."
    ),
    "files": TARGET_FILE,
    "dependencies": ["task_1"],
    "approach": "cognitive",
    "constraints": [
        "Follow existing DashboardService method patterns",
        "Use existing repository instances already in the service",
        "DashboardAlert is already defined in app.models.dashboard",
        "severity values: 'critical' or 'warning'",
        "Do NOT modify existing methods",
    ]
}


def ensure_daemons_running() -> bool:
    """Check tmux session exists with agent daemons."""
    result = subprocess.run(["tmux", "has-session", "-t", "sdlc-agents"], capture_output=True)
    if result.returncode != 0:
        print("❌ Agent daemons not running. Start them first:")
        print("   bash start_agents.sh --debug")
        return False
    print("✓ Agent daemon session running (sdlc-agents)")
    return True


async def main():
    print("=" * 80)
    print("END-TO-END TEST — task_2: Alerts Engine")
    print("=" * 80)
    print()

    # Brain check
    if not brain_client.is_running():
        print("❌ Brain Server not running.")
        return 1
    s = brain_client.status()
    print(f"✓ Brain Server — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")

    # Daemon check
    if not ensure_daemons_running():
        return 1

    # Check target file exists
    if not Path(TARGET_FILE).exists():
        print(f"❌ Target file not found: {TARGET_FILE}")
        return 1
    print(f"✓ Target file: {TARGET_FILE}")
    print()

    bus = FileMessageBus()
    loop = ConversationLoop(bus=bus)

    print(f"Dropping task_2 onto coder/inbox...")
    print(f"Watch progress: tmux attach -t sdlc-agents")
    print()

    try:
        result = await loop.execute_task(TASK, max_iterations=5)

        print()
        print("=" * 80)
        print("RESULT")
        print("=" * 80)
        print(f"  Status:        {result['status']}")
        print(f"  Diffs applied: {result.get('diffs_applied', 0)}")
        print(f"  Diffs failed:  {result.get('diffs_failed', 0)}")
        print("=" * 80)
        return 0 if result["status"] == "approved" else 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
