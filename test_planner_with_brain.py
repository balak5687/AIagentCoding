#!/usr/bin/env python3
"""
Test Planner Agent with Designer output + Project Brain
"""
import sys
from pathlib import Path
from src.core.agent_runner import AgentRunner
from src.brain import client as brain_client

def main():
    print("=" * 80)
    print("TESTING PLANNER AGENT WITH PROJECT BRAIN")
    print("=" * 80)
    print()

    # Check brain server
    if brain_client.is_running():
        s = brain_client.status()
        print(f"✓ Brain Server running — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")
    else:
        print("❌ Brain Server not running. Start it first:")
        print("   python start_brain_server.py --daemon")
        return 1

    # Load designer output
    designer_output = Path("designer_output_issue3.md").read_text()
    print(f"✓ Designer output loaded ({len(designer_output)} chars)")
    print()

    # Create AgentRunner — planner auto-selects opus (1M context)
    runner = AgentRunner(
        mode="claude-code",
        config={
            "debug": True,
            "timeout_seconds": 600
        }
    )

    # Context for Planner
    context = {
        "design": designer_output,
        "project": "GreasyNuts",
        "issue_number": 3,
        "branch": "testing/sdlc-issue-3",
        "backend_path": "/home/ubuntu/greasynuts/dev/backend/GreasyNuts",
        "frontend_path": "/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype",
        "constraints": [
            "Do not modify main, dev, or prod branches",
            "Only work in testing/sdlc-issue-3 branch",
            "Follow existing Flask patterns in backend",
            "Follow existing StatefulWidget + service patterns in Flutter",
            "Backend uses DynamoDB — no SQL"
        ]
    }

    print("=" * 80)
    print("RUNNING PLANNER AGENT (opus, 1M context)...")
    print("=" * 80)
    print()

    try:
        result = runner.run("planner", context, max_retries=2)

        print()
        print("=" * 80)
        print("PLANNER OUTPUT")
        print("=" * 80)
        print()
        print("METADATA:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")
        print()
        print("CONTENT:")
        print(result.content)

        # Save output
        output_file = Path("planner_output_issue3.md")
        with open(output_file, 'w') as f:
            f.write("# Planner Output - Issue #3\n\n")
            f.write("## Metadata\n\n")
            for key, value in result.metadata.items():
                f.write(f"- **{key}**: {value}\n")
            f.write("\n## Execution Plan\n\n")
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
