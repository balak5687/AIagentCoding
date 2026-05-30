#!/usr/bin/env python3
"""
Full SDLC pipeline: Designer → Architect (feasibility) → [revise loop] → Planner

If Architect blocks, Designer automatically re-runs with Architect feedback.
Max 3 design revision cycles before giving up.

Usage:
    python3 run_pipeline.py --issue 4 --designer-output designer_output_issue4.md
    python3 run_pipeline.py --issue 4  # runs designer first if no output exists
"""
import sys
import argparse
from pathlib import Path
from src.core.agent_runner import AgentRunner
from src.brain import client as brain_client

MAX_DESIGN_CYCLES = 3


def run_designer(runner, context: dict, issue_num: int, architect_feedback: str = "") -> str:
    print("=" * 80)
    print(f"DESIGNER {'(REVISION)' if architect_feedback else '(INITIAL)'}")
    print("=" * 80)

    designer_context = {**context}
    if architect_feedback:
        designer_context["architect_feedback"] = architect_feedback
        designer_context["revision_instructions"] = (
            "The Architect reviewed your previous design and found issues. "
            "Address ALL blockers listed in architect_feedback before producing the revised design. "
            "Pay special attention to: DynamoDB GSI limits, missing backward compatibility, "
            "system component assessment, and absolute file paths."
        )

    result = runner.run("designer", designer_context, max_retries=2)
    output_file = Path(f"designer_output_issue{issue_num}.md")
    with open(output_file, "w") as f:
        f.write(f"# Designer Output - Issue #{issue_num}\n\n## Metadata\n\n")
        for k, v in result.metadata.items():
            f.write(f"- **{k}**: {v}\n")
        f.write("\n## Design Document\n\n")
        f.write(result.content)

    print(f"✅ Design saved: {output_file} (confidence: {result.metadata.get('confidence')}%)")
    return result.content


def run_architect(runner, designer_output: str, context: dict) -> tuple:
    """Returns (approved: bool, review_text: str)"""
    print("=" * 80)
    print("ARCHITECT FEASIBILITY REVIEW")
    print("=" * 80)

    architect_context = {
        "mode": "feasibility",
        "design": designer_output,
        "project": context.get("project"),
        "branch": context.get("branch"),
        "backend_path": context.get("backend_path"),
        "react_path": context.get("react_path"),
        "constraints": context.get("constraints", []),
        "instructions": (
            "Review this design for feasibility before planning begins. "
            "Check: missing repos/services, wrong field names, DynamoDB GSI limits (max 5), "
            "missing backward compatibility, system component assessment (WebSocket/queue/cache/S3). "
            "Output APPROVED if safe to plan, BLOCKED if critical issues found."
        )
    }

    try:
        result = runner.run("architect", architect_context, max_retries=1)
        status = result.metadata.get("status", "approved")
        approved = status != "blocked"

        if approved:
            print(f"✅ Architect: APPROVED")
            if "warning" in result.content.lower():
                for line in result.content.split('\n'):
                    if '**Warning' in line or '⚠️' in line:
                        print(f"  ⚠️  {line.strip()}")
        else:
            print(f"❌ Architect: BLOCKED")
            print()
            # Print blockers
            in_blockers = False
            for line in result.content.split('\n'):
                if 'Blocker' in line or 'BLOCKED' in line:
                    in_blockers = True
                if in_blockers:
                    print(f"  {line}")
                if in_blockers and line.strip() == '' and 'Warning' in result.content[result.content.find(line):result.content.find(line)+200]:
                    break

        return approved, result.content

    except Exception as e:
        print(f"⚠️  Architect review failed ({e}) — proceeding")
        return True, ""


def run_planner(runner, designer_output: str, architect_review: str, context: dict, issue_num: int):
    print("=" * 80)
    print("PLANNER")
    print("=" * 80)

    planner_context = {
        "design": designer_output,
        "architect_review": architect_review,
        "project": context.get("project"),
        "issue_number": issue_num,
        "branch": context.get("branch"),
        "backend_path": context.get("backend_path"),
        "react_path": context.get("react_path"),
        "constraints": context.get("constraints", []),
        "path_format": (
            "ABSOLUTE PATHS ONLY. "
            "Backend: /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/... "
            "React: /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/..."
        )
    }

    result = runner.run("planner", planner_context, max_retries=2)

    output_file = Path(f"planner_output_issue{issue_num}.md")
    with open(output_file, "w") as f:
        f.write(f"# Planner Output - Issue #{issue_num}\n\n## Metadata\n\n")
        for k, v in result.metadata.items():
            f.write(f"- **{k}**: {v}\n")
        f.write("\n## Execution Plan\n\n")
        f.write(result.content)

    print(f"✅ Plan saved: {output_file} (confidence: {result.metadata.get('confidence')}%)")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--designer-output", type=str, default=None)
    parser.add_argument("--project", default="GreasyNuts")
    parser.add_argument("--skip-designer", action="store_true", help="Use existing designer output")
    args = parser.parse_args()

    issue_num = args.issue
    designer_file = args.designer_output or f"designer_output_issue{issue_num}.md"

    print("=" * 80)
    print(f"SDLC PIPELINE — Issue #{issue_num}")
    print("=" * 80)

    if not brain_client.is_running():
        print("❌ Brain not running. Start: python3 start_brain_server.py --daemon")
        return 1
    s = brain_client.status()
    print(f"✓ Brain — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")

    runner = AgentRunner(mode="claude-code", config={"debug": True, "timeout_seconds": 600})

    context = {
        "project": args.project,
        "issue_number": issue_num,
        "branch": f"testing/sdlc-issue-{issue_num}",
        "backend_path": "/home/ubuntu/greasynuts/dev/backend/GreasyNuts",
        "react_path": "/home/ubuntu/greasynuts/dev/GreasyNutsReact",
        "constraints": [
            f"Only work in testing/sdlc-issue-{issue_num} branch",
            "Do not modify main, dev, or prod branches",
            "Frontend is React/TypeScript — NOT Flutter",
            "Backend is Python/Flask/DynamoDB",
            "Use absolute file paths only",
            "DynamoDB max 5 GSIs per table",
            "Backend files: /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/...",
            "React files: /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/...",
        ]
    }

    # Phase 1: Designer (with revision loop)
    architect_feedback = ""
    designer_output = ""

    for cycle in range(1, MAX_DESIGN_CYCLES + 1):
        print(f"\n--- Design Cycle {cycle}/{MAX_DESIGN_CYCLES} ---")

        if cycle == 1 and args.skip_designer and Path(designer_file).exists():
            print(f"Using existing designer output: {designer_file}")
            designer_output = Path(designer_file).read_text()
            # Extract content after ## Design Document header
            if "## Design Document" in designer_output:
                designer_output = designer_output.split("## Design Document\n\n", 1)[-1]
        else:
            # Add issue context from job module documents if available
            issue_context = context.copy()
            if cycle == 1:
                # Load issue spec dynamically from brain sources
                spec_path = Path(f'.project-brain/sources/functionality-brain/specs/issue-{issue_num}/requirements.md')
                if spec_path.exists():
                    spec_content = spec_path.read_text()
                    issue_context["issue_specification"] = spec_content
                    for line in spec_content.split('\n'):
                        if line.startswith('**Title**:'):
                            issue_context["requirement"] = line.replace('**Title**:', '').strip()
                            break
                    issue_context["issue_url"] = f"https://github.com/aravindmk1011/GreasyNutsIssues/issues/{issue_num}"
                    print(f"✓ Loaded spec: {spec_path} ({len(spec_content)} chars)")
                    # Also load target design image if available
                    img_path = spec_path.parent / "target_design.png"
                    if img_path.exists():
                        issue_context["target_design_image"] = str(img_path)
                        print(f"✓ Loaded design image: {img_path}")
                else:
                    print(f"⚠️  No spec at {spec_path} — using brain context only")
                    issue_context["issue_url"] = "https://github.com/aravindmk1011/GreasyNutsIssues/issues/4"

            designer_output = run_designer(runner, issue_context, issue_num, architect_feedback)

        # Phase 2: Architect review
        approved, architect_review = run_architect(runner, designer_output, context)

        if approved:
            break

        if cycle < MAX_DESIGN_CYCLES:
            print(f"\nDesigner will revise based on Architect feedback (cycle {cycle+1})...")
            architect_feedback = architect_review
        else:
            print(f"\n❌ Design blocked after {MAX_DESIGN_CYCLES} cycles. Check architect feedback.")
            return 1

    # Phase 3: Planner
    print()
    try:
        result = run_planner(runner, designer_output, architect_review, context, issue_num)
        print(f"\n✅ Pipeline complete — run: python3 run_issue.py --issue {issue_num}")
        return 0
    except Exception as e:
        print(f"\n❌ Planner failed: {e}")
        import traceback; traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
