#!/usr/bin/env python3
"""
Run the Issue #6 pipeline and stream each agent's output
to its dedicated tmux pane in real time.

Pane layout (session: issue6-pipeline):
  Pane 0.0 (left)        = Designer
  Pane 0.1 (top right)   = Architect
  Pane 0.2 (bottom right) = Planner
"""
import subprocess, sys, os, threading

SESSION = "issue6-pipeline"
PANES = {
    "designer":  f"{SESSION}:0.0",
    "architect": f"{SESSION}:0.1",
    "planner":   f"{SESSION}:0.2",
}
LOGS = {k: f"/tmp/issue6_{k}.log" for k in PANES}

def pane_print(pane_key, msg):
    """Write a line to the pane's log (which pane is tail -f ing)."""
    with open(LOGS[pane_key], "a") as f:
        f.write(msg + "\n")

def header(pane_key, title):
    pane_print(pane_key, "")
    pane_print(pane_key, "═" * 60)
    pane_print(pane_key, f"  {title}")
    pane_print(pane_key, "═" * 60)

# Clear logs and start tail in each pane
for k, log in LOGS.items():
    open(log, "w").close()
    subprocess.run(["tmux", "send-keys", "-t", PANES[k], f"tail -f {log}", "Enter"])

import time; time.sleep(1)

pane_print("designer",  "Issue #6 — Service Master Module")
pane_print("architect", "Issue #6 — Service Master Module")
pane_print("planner",   "Issue #6 — Service Master Module")

# Detect which phase we're in based on pipeline stdout markers
current_pane = "designer"
phase_map = {
    "DESIGNER":   "designer",
    "ARCHITECT":  "architect",
    "PLANNER":    "planner",
}

header("designer", "DESIGNER — Claude Opus")
header("architect", "ARCHITECT — Claude Opus (Feasibility Review)")
header("planner", "PLANNER — Claude Opus")

pane_print("designer",  "Waiting for Designer to start...")
pane_print("architect", "Waiting for Architect review...")
pane_print("planner",   "Waiting for Planner...")

# Run the pipeline, route output lines to correct pane
env = os.environ.copy()
proc = subprocess.Popen(
    [sys.executable, "run_pipeline.py", "--issue", "6"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    env=env,
    cwd="/home/ubuntu/bala/AIagentCoding"
)

for line in proc.stdout:
    line = line.rstrip()
    # Detect phase switches
    for marker, pane_key in phase_map.items():
        if marker in line.upper():
            current_pane = pane_key
            break
    pane_print(current_pane, line)
    # Mirror important lines to all panes
    if any(x in line for x in ["✅", "❌", "BLOCKED", "APPROVED", "Pipeline complete"]):
        for k in PANES:
            if k != current_pane:
                pane_print(k, f"  [{current_pane.upper()}] {line}")

proc.wait()
status = "✅ Pipeline complete" if proc.returncode == 0 else "❌ Pipeline failed"
for k in PANES:
    pane_print(k, "")
    pane_print(k, status)
    pane_print(k, "See: designer_output_issue6.md  |  planner_output_issue6.md")
