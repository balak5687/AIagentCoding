#!/usr/bin/env python3
"""
Test Designer Agent with Project Brain on GitHub Issue #3
Target: Dashboard Module Rev2 with target design image
"""
import sys
import subprocess
import time
from pathlib import Path
from src.core.agent_runner import AgentRunner
from src.brain import client as brain_client

def ensure_brain_server():
    """Start Brain Server as background process if not already running"""
    if brain_client.is_running():
        s = brain_client.status()
        print(f"✓ Brain Server already running — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")
        return

    print("🧠 Starting Brain Server in background...")
    subprocess.Popen(
        ["python", "start_brain_server.py", "--daemon"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait up to 30s for it to come online
    for i in range(30):
        time.sleep(1)
        if brain_client.is_running():
            s = brain_client.status()
            print(f"✓ Brain Server ready — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")
            return

    print("⚠ Brain Server did not start in time — continuing without brain context")

def main():
    print("=" * 80)
    print("TESTING DESIGNER AGENT WITH PROJECT BRAIN")
    print("=" * 80)
    print()

    target_image = Path.home() / "Dashboard image.png"
    print(f"✓ Target design: {target_image}")
    print(f"✓ Issue: GitHub #3 - Dashboard Module Rev2")
    print()

    # Ensure brain server is running (background)
    ensure_brain_server()
    print()

    # Create AgentRunner — no brain_manifest_path needed, uses HTTP client
    runner = AgentRunner(
        mode="claude-code",
        config={
            "debug": True,
            "timeout_seconds": 600
        }
    )

    print("✓ AgentRunner initialized with Project Brain")
    print()

    # Prepare context for Designer
    context = {
        "requirement": "Dashboard Module Rev2 - Real-time Operational Overview",
        "issue_number": 3,
        "issue_url": "https://github.com/aravindmk1011/GreasyNutsIssues/issues/3",
        "target_design_image": str(target_image),
        "issue_description": """
Build a comprehensive dashboard module that provides a centralized real-time
operational overview of the garage business.

Key Requirements:
1. Display key metrics: Total Jobs (12), Parts (0), Revenue (₹2,440), Expenses (₹1,120)
2. Recent activity feed showing latest updates
3. Revenue trend chart showing last 7 days performance
4. Top 5 suppliers list with contact info
5. Mobile responsive design with touch-friendly interface
6. Auto-refresh every 60 seconds

The dashboard should provide workflow visibility, financial tracking,
operational alerts, and analytics to help garage owners make informed decisions.

Technologies:
- Backend: Python FastAPI with DynamoDB
- Frontend: Flutter/Dart
- Real-time updates via WebSocket or polling
        """,
        "project_context": {
            "name": "GreasyNuts",
            "backend": "Python/FastAPI/DynamoDB",
            "frontend": "Flutter/Dart",
            "branch": "testing/sdlc-issue-3"
        }
    }

    print("=" * 80)
    print("CONTEXT FOR DESIGNER")
    print("=" * 80)
    print(f"Requirement: {context['requirement']}")
    print(f"Issue: #{context['issue_number']}")
    print(f"Target Image: {context['target_design_image']}")
    print()

    # Run Designer agent
    print("=" * 80)
    print("RUNNING DESIGNER AGENT (This may take 1-2 minutes...)")
    print("=" * 80)
    print()

    try:
        result = runner.run("designer", context, max_retries=2)

        print()
        print("=" * 80)
        print("DESIGNER OUTPUT")
        print("=" * 80)
        print()

        # Display metadata
        print("METADATA:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")

        print()
        print("CONTENT:")
        print(result.content)

        # Save output
        output_file = Path("designer_output_issue3.md")
        with open(output_file, 'w') as f:
            f.write(f"# Designer Output - Issue #3\n\n")
            f.write(f"## Metadata\n\n")
            for key, value in result.metadata.items():
                f.write(f"- **{key}**: {value}\n")
            f.write(f"\n## Design Document\n\n")
            f.write(result.content)

        print()
        print("=" * 80)
        print(f"✅ OUTPUT SAVED TO: {output_file}")
        print("=" * 80)

        return 0

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERROR: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
