#!/bin/bash
# Full Issue #4 pipeline: Architect → Planner → Agent Run
# Runs in background, survives SSH disconnect
# Monitor: tail -f /home/ubuntu/bala/AIagentCoding/logs/issue4/pipeline.log

set -e
LOG="/home/ubuntu/bala/AIagentCoding/logs/issue4/pipeline.log"
PROGRESS="/home/ubuntu/bala/AIagentCoding/logs/issue4/progress.json"

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"; }

log "=== ISSUE #4 PIPELINE START ==="
log "Branch: backend=testing/sdlc-issue-4 react=testing/sdlc-issue-4"

# Step 1: Start agent daemons
log "Step 1: Starting agent daemons..."
cd /home/ubuntu/bala/AIagentCoding
bash start_agents.sh --debug
sleep 5
log "Daemons started. Logs in logs/issue4/"

# Step 2: Run architect feasibility + planner
log "Step 2: Running Architect + Planner (pipeline)..."
python3 run_pipeline.py \
  --issue 4 \
  --designer-output designer_output_issue4.md \
  2>&1 | tee -a "$LOG"

PLANNER_EXIT=${PIPESTATUS[0]}
if [ $PLANNER_EXIT -ne 0 ]; then
  log "ERROR: Pipeline failed at architect/planner stage (exit $PLANNER_EXIT)"
  echo '{"status":"failed","stage":"planner"}' > "$PROGRESS"
  exit 1
fi

log "Step 3: Running issue tasks through agent system..."
echo '{"status":"running","stage":"coding","started":"'"$(date -Iseconds)"'"}' > "$PROGRESS"

python3 run_issue.py --issue 4 \
  2>&1 | tee -a "$LOG"

RUN_EXIT=${PIPESTATUS[0]}

if [ $RUN_EXIT -eq 0 ]; then
  log "=== ISSUE #4 COMPLETE ==="
  echo '{"status":"complete","stage":"done","finished":"'"$(date -Iseconds)"'"}' > "$PROGRESS"
else
  log "=== ISSUE #4 FAILED (exit $RUN_EXIT) ==="
  echo '{"status":"failed","stage":"coding","finished":"'"$(date -Iseconds)"'"}' > "$PROGRESS"
fi
