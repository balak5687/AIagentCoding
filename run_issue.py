#!/usr/bin/env python3
"""
Generic issue runner — reads planner_output_issueN.md and executes all tasks.
Usage: python3 run_issue.py --issue 4
"""
import sys
import asyncio
import argparse
import re
import time
import json
from pathlib import Path
from typing import Dict, List
import networkx as nx

from src.bus import FileMessageBus
from src.workflows.conversation import ConversationLoop

def _route_task(task):
    raw = task.get('files', '')
    m = re.search(r'`(/[^`]+)`', raw)
    target = m.group(1) if m else raw
    if '/GreasyNutsReact/' in target or target.endswith(('.ts','.tsx','.js','.jsx')):
        return 'react_coder'
    return 'backend_coder'
from src.brain import client as brain_client

POLL_INTERVAL = 3
TASK_TIMEOUT  = 1800  # 30 min


def parse_tasks(plan_path: str) -> List[Dict]:
    text = Path(plan_path).read_text()
    match = re.search(r'## Task Breakdown\n(.*?)(?=\n## Execution Strategy|\Z)', text, re.DOTALL)
    if not match:
        raise ValueError(f"No 'Task Breakdown' section found in {plan_path}")

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
                if key == "files":
                    val = val.strip("`").replace("`, `", ", ").strip("`")
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


async def run_task(bus: FileMessageBus, task: Dict, issue_num: int) -> Dict:
    task_id = task["id"]
    coder_inbox = _route_task(task)
    bus.send(coder_inbox, task_id, {"task": task, "iteration": 1}, from_agent="orchestrator")

    start = time.time()
    while time.time() - start < TASK_TIMEOUT:
        await asyncio.sleep(POLL_INTERVAL)
        result = bus.wait_for_task("reviewer", task_id)
        if result:
            r = result.get("result", result)
            return r
    return {"status": "timeout", "task_id": task_id}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--skip", nargs="*", default=[], help="Task IDs to skip")
    args = parser.parse_args()

    issue_num = args.issue
    plan_file = f"planner_output_issue{issue_num}.md"
    progress_file = Path(f"logs/issue{issue_num}/progress.json")
    progress_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"{'='*70}")
    print(f"ISSUE #{issue_num} — FULL EXECUTION")
    print(f"{'='*70}")

    if not brain_client.is_running():
        print("❌ Brain not running")
        return 1

    s = brain_client.status()
    print(f"✓ Brain — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")

    import subprocess
    r = subprocess.run(["tmux", "has-session", "-t", "sdlc-agents"], capture_output=True)
    if r.returncode != 0:
        print("❌ Agent daemons not running. Run: bash start_agents.sh --debug")
        return 1
    print("✓ Agent daemons running")
    print()

    tasks = parse_tasks(plan_file)
    print(f"Parsed {len(tasks)} tasks")

    completed = set(args.skip)
    if completed:
        print(f"Skipping: {sorted(completed)}")

    groups = build_groups(tasks)
    bus = FileMessageBus()

    total_approved = 0
    total_failed = 0

    for i, group in enumerate(groups):
        exec_group = [t for t in group if t["id"] not in completed]
        if not exec_group:
            print(f"Group {i+1}: {[t['id'] for t in group]} — all done, skipping")
            continue

        print(f"\n{'='*50}")
        print(f"Group {i+1}: {[t['id'] for t in exec_group]}")
        print(f"{'='*50}")

        results = await asyncio.gather(*[run_task(bus, t, issue_num) for t in exec_group])

        timed_out = []
        for task, result in zip(exec_group, results):
            status = result.get("status", "unknown")
            applied = result.get("diffs_applied", 0)
            sym = "✅" if status == "approved" else "⏱" if status == "timeout" else "❌"
            print(f"  {sym} {task['id']:12} → {status:20} (diffs: {applied})")

            if status == "approved":
                total_approved += 1
                completed.add(task["id"])
            elif status == "timeout":
                # Auto-retry timed-out tasks once
                timed_out.append(task)
            else:
                total_failed += 1

        # Retry timed-out tasks individually with longer patience
        if timed_out:
            print(f"\n  ⏱ Retrying {len(timed_out)} timed-out tasks...")
            for task in timed_out:
                print(f"    Retrying {task['id']}...")
                result = await run_task(bus, task, issue_num)
                status = result.get("status", "unknown")
                applied = result.get("diffs_applied", 0)
                sym = "✅" if status == "approved" else "❌"
                print(f"    {sym} {task['id']} → {status} (diffs: {applied})")
                if status == "approved":
                    total_approved += 1
                    completed.add(task["id"])
                else:
                    total_failed += 1

        # Update progress file
        progress_file.write_text(json.dumps({
            "issue": issue_num,
            "completed": list(completed),
            "approved": total_approved,
            "failed": total_failed,
            "current_group": i + 1,
            "total_groups": len(groups),
        }, indent=2))

    print(f"\n{'='*70}")
    print(f"COMPLETE — {total_approved} approved, {total_failed} failed")
    print(f"{'='*70}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
