#!/usr/bin/env python3
"""
Smoke test: Wire 'View All' in AlertsPanel to open full alerts view in DashboardRev2.

Two files to change:
1. dashboard_rev2_screen.dart — pass onViewAll callback + add 'alerts' module case
2. No change needed to alerts_panel.dart (onViewAll already exists)

This tests the full V2 pipeline: frontend_coder → compile → reviewer
"""
import sys
import asyncio
from pathlib import Path
from src.bus import FileMessageBus
from src.workflows.conversation import ConversationLoop
from src.brain import client as brain_client

DASHBOARD_FILE = "/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/screens/dashboard/dashboard_rev2_screen.dart"

TASK = {
    "id": "smoke_alerts_view_all",
    "name": "Wire View All alerts to full alerts screen",
    "description": (
        "In dashboard_rev2_screen.dart, make two changes: "
        "1) Pass onViewAll callback to AlertsPanel that calls setModule('alerts'). "
        "2) Add a new module case in _buildContent: when _activeModule == 'alerts', "
        "show a full-screen list of all alerts from _overview?.alerts with severity "
        "color coding (red=critical, yellow=warning) and a Back button that calls setModule(null). "
        "The alerts list should show: severity dot, type, message, timestamp. "
        "Keep existing dashboard layout unchanged when _activeModule is null."
    ),
    "files": DASHBOARD_FILE,
    "dependencies": [],
    "approach": "cognitive",
    "constraints": [
        "Only modify dashboard_rev2_screen.dart",
        "Do not change alerts_panel.dart",
        "AlertsPanel already has onViewAll: VoidCallback? parameter",
        "Use existing DashboardAlert model fields: type, message, severity, timestamp",
        "Severity 'critical' = red dot, 'warning' = orange/yellow dot",
        "Back button should call setModule(null) to return to dashboard home",
    ]
}


async def main():
    print("=" * 70)
    print("SMOKE TEST — View All Alerts (V2 frontend_coder → compile → reviewer)")
    print("=" * 70)

    if not brain_client.is_running():
        print("❌ Brain not running")
        return 1

    s = brain_client.status()
    print(f"✓ Brain — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")
    print(f"✓ Target: {DASHBOARD_FILE.split('lib/')[-1]}")
    print()

    # Verify branch
    import subprocess
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd="/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd",
        capture_output=True, text=True
    ).stdout.strip()
    print(f"✓ Branch: {branch}")
    if branch not in ("testing/sdlc-issue-3",):
        print("⚠️  Warning: not on testing/sdlc-issue-3")
    print()

    bus = FileMessageBus()
    loop = ConversationLoop(bus=bus)

    print("Dropping task → frontend_coder/inbox")
    print("Watch: tmux attach -t sdlc-agents")
    print()

    try:
        result = await loop.execute_task(TASK, max_iterations=3)
        print()
        print("=" * 70)
        print(f"RESULT: {result['status'].upper()}")
        print(f"Diffs applied: {result.get('diffs_applied', 0)}")
        print(f"Diffs failed:  {result.get('diffs_failed', 0)}")
        print("=" * 70)

        if result['status'] == 'approved' and result.get('diffs_applied', 0) > 0:
            print("\n✅ Code applied — rebuilding Flutter...")
            import os
            os.system(
                "cd /home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype && "
                "/home/ubuntu/flutter/bin/flutter build web --release 2>&1 | tail -3 && "
                "cp -r build/web/. /home/ubuntu/greasynuts/feature/feature-flutter-frontend/"
                "GreasyNutsFrontEnd/flutter_prototype/build/web/ && echo '✓ Deployed to 8090'"
            )
        return 0 if result['status'] == 'approved' else 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback; traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
