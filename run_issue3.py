#!/usr/bin/env python3
"""
Execute all remaining tasks from planner_output_issue3.md via daemon bus.
Respects dependency graph — parallel groups run concurrently.
Already-completed tasks (task_1, task_2) are skipped.
"""
import sys
import asyncio
import re
import time
from pathlib import Path
from typing import Dict, List
import networkx as nx

from src.bus import FileMessageBus
from src.workflows.conversation import ConversationLoop
from src.brain import client as brain_client

# Tasks already completed on testing/sdlc-issue-3
COMPLETED = {"task_1", "task_2"}

POLL_INTERVAL = 3
TASK_TIMEOUT  = 900  # 15 min per task max


def parse_tasks(plan_path: str) -> List[Dict]:
    text = Path(plan_path).read_text()

    # Find Task Breakdown section
    match = re.search(r'## Task Breakdown\n(.*?)(?=\n## Execution Strategy|\Z)', text, re.DOTALL)
    if not match:
        raise ValueError("No 'Task Breakdown' section found in plan")

    breakdown = match.group(1)
    tasks = []

    for block in re.split(r'\n### Task \d+:', breakdown):
        if not block.strip():
            continue

        task = {}

        name_match = re.match(r'\s*(.+?)\n', block)
        if name_match:
            task["name"] = name_match.group(1).strip()

        for field, key in [
            (r'\*\*ID\*\*:\s*(.+)',          "id"),
            (r'\*\*Description\*\*:\s*(.+)', "description"),
            (r'\*\*Files\*\*:\s*(.+)',        "files"),
            (r'\*\*Approach\*\*:\s*(.+)',     "approach"),
        ]:
            m = re.search(field, block)
            if m:
                val = m.group(1).strip()
                # Strip backtick wrapping from file paths
                if key == "files":
                    val = val.strip("`").replace("`, `", ", ")
                task[key] = val

        dep_match = re.search(r'\*\*Dependencies\*\*:\s*\[(.*?)\]', block)
        if dep_match:
            raw = dep_match.group(1).strip()
            task["dependencies"] = [d.strip() for d in raw.split(",") if d.strip()] if raw else []
        else:
            task["dependencies"] = []

        if "id" in task:
            tasks.append(task)

    return tasks


def build_groups(tasks: List[Dict]) -> List[List[Dict]]:
    G = nx.DiGraph()
    task_map = {t["id"]: t for t in tasks}

    for t in tasks:
        G.add_node(t["id"])
        for dep in t.get("dependencies", []):
            if dep in task_map:
                G.add_edge(dep, t["id"])

    groups = []
    for generation in nx.topological_generations(G):
        group = [task_map[tid] for tid in generation if tid in task_map]
        if group:
            groups.append(group)
    return groups


async def run_task(bus: FileMessageBus, task: Dict) -> Dict:
    """Drop task onto bus, poll for this specific task's result in reviewer outbox."""
    task_id = task["id"]
    bus.send("coder", task_id, {"task": task, "iteration": 1}, from_agent="orchestrator")

    start = time.time()
    while time.time() - start < TASK_TIMEOUT:
        await asyncio.sleep(POLL_INTERVAL)
        result = bus.wait_for_task("reviewer", task_id)
        if result:
            return result["result"] if "result" in result else result

    return {"status": "timeout", "task_id": task_id}


async def main():
    print("=" * 80)
    print("ISSUE #3 — FULL EXECUTION")
    print("=" * 80)

    if not brain_client.is_running():
        print("❌ Brain Server not running")
        return 1

    s = brain_client.status()
    print(f"✓ Brain — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")

    # Check daemons
    import subprocess
    r = subprocess.run(["tmux", "has-session", "-t", "sdlc-agents"], capture_output=True)
    if r.returncode != 0:
        print("❌ Agent daemons not running. Run: bash start_agents.sh --debug")
        return 1
    print("✓ Agent daemons running (sdlc-agents)")
    print()

    # Parse tasks
    tasks = parse_tasks("planner_output_issue3.md")
    print(f"Parsed {len(tasks)} tasks from planner output")

    # Skip completed
    remaining = [t for t in tasks if t["id"] not in COMPLETED]
    print(f"Skipping completed: {sorted(COMPLETED)}")
    print(f"Remaining: {[t['id'] for t in remaining]}")
    print()

    # Build dependency groups (only from remaining)
    # Need full task list for graph but only execute remaining
    groups = build_groups(tasks)
    bus = FileMessageBus()

    total_approved = 0
    total_failed = 0

    for i, group in enumerate(groups):
        # Filter to only remaining tasks in this group
        exec_group = [t for t in group if t["id"] not in COMPLETED]
        if not exec_group:
            skipped = [t["id"] for t in group]
            print(f"Group {i+1}: {skipped} — all already done, skipping")
            continue

        print(f"{'='*60}")
        print(f"Group {i+1}: executing {[t['id'] for t in exec_group]} in parallel")
        print(f"{'='*60}")

        # Drop all tasks in group simultaneously, wait for all
        results = await asyncio.gather(*[run_task(bus, t) for t in exec_group])

        for task, result in zip(exec_group, results):
            status = result.get("status", "unknown")
            applied = result.get("diffs_applied", 0)
            failed_diffs = result.get("diffs_failed", 0)
            print(f"  {task['id']:10} → {status:20} (diffs: {applied} applied, {failed_diffs} failed)")
            if status == "approved":
                total_approved += 1
                COMPLETED.add(task["id"])
            else:
                total_failed += 1

        print()

    print("=" * 80)
    print(f"COMPLETE — {total_approved} approved, {total_failed} failed")
    print("=" * 80)
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
