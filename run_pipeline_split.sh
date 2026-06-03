#!/bin/bash
# ============================================================
# Issue #6 SDLC Pipeline — split output across 3 tmux panes
# Pane 0 = Designer | Pane 1 = Architect | Pane 2 = Planner
# ============================================================
SESSION="issue6-pipeline"
PANE_DESIGNER="$SESSION:0.0"
PANE_ARCHITECT="$SESSION:0.1"
PANE_PLANNER="$SESSION:0.2"

LOG_DESIGNER="/tmp/issue6_designer.log"
LOG_ARCHITECT="/tmp/issue6_architect.log"
LOG_PLANNER="/tmp/issue6_planner.log"

# Clear logs
> $LOG_DESIGNER; > $LOG_ARCHITECT; > $LOG_PLANNER

# Tail each log into its pane
tmux send-keys -t "$PANE_DESIGNER"  "tail -f $LOG_DESIGNER" Enter
tmux send-keys -t "$PANE_ARCHITECT" "tail -f $LOG_ARCHITECT" Enter
tmux send-keys -t "$PANE_PLANNER"   "tail -f $LOG_PLANNER" Enter

echo "Panes streaming logs. Starting pipeline..."
echo ""

cd /home/ubuntu/bala/AIagentCoding

# ── Load spec + images ──────────────────────────────────────
SPEC=".project-brain/sources/functionality-brain/specs/issue-6/requirements.md"
IMG_DIR=".project-brain/sources/functionality-brain/specs/issue-6"

echo "[$(date +%H:%M:%S)] SDLC Pipeline — Issue #6: Service Master Module" | tee -a $LOG_DESIGNER $LOG_ARCHITECT $LOG_PLANNER
echo "[$(date +%H:%M:%S)] Spec: $SPEC" | tee -a $LOG_DESIGNER

# ── PHASE 1: DESIGNER ──────────────────────────────────────
echo "" >> $LOG_DESIGNER
echo "════════════════════════════════════════" >> $LOG_DESIGNER
echo "  DESIGNER (Claude Opus) — Design Cycle 1" >> $LOG_DESIGNER
echo "════════════════════════════════════════" >> $LOG_DESIGNER

python3 run_pipeline.py --issue 6 >> $LOG_DESIGNER 2>&1
STATUS=$?

if [ $STATUS -eq 0 ]; then
  echo "" | tee -a $LOG_ARCHITECT $LOG_PLANNER
  echo "[$(date +%H:%M:%S)] ✅ Pipeline completed successfully" | tee -a $LOG_DESIGNER $LOG_ARCHITECT $LOG_PLANNER
  echo "[$(date +%H:%M:%S)] Designer output: designer_output_issue6.md" >> $LOG_DESIGNER
  echo "[$(date +%H:%M:%S)] Architect output: see designer log" >> $LOG_ARCHITECT
  echo "[$(date +%H:%M:%S)] Planner output: planner_output_issue6.md" >> $LOG_PLANNER
else
  echo "[$(date +%H:%M:%S)] ❌ Pipeline failed — check logs" | tee -a $LOG_DESIGNER $LOG_ARCHITECT $LOG_PLANNER
fi
