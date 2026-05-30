#!/bin/bash
# Start all agent daemons as background processes with restart on failure
# Survives SSH disconnect when run inside tmux
# Usage: bash start_daemons.sh

LOGDIR="/home/ubuntu/bala/AIagentCoding/logs/issue4"
mkdir -p "$LOGDIR"

start_daemon() {
    local name=$1
    echo "[$(date '+%H:%M:%S')] Starting $name..."
    while true; do
        python3 run_daemon.py "$name" --debug >> "$LOGDIR/${name}.log" 2>&1
        echo "[$(date '+%H:%M:%S')] $name exited, restarting in 3s..."
        sleep 3
    done &
    echo "[$(date '+%H:%M:%S')] $name supervisor PID: $!"
}

# Kill any existing daemon processes
pkill -f "run_daemon.py" 2>/dev/null
sleep 2

echo "Starting all agent daemons..."
start_daemon backend_coder
start_daemon react_coder
start_daemon compile
start_daemon architect
start_daemon reviewer

sleep 5

echo ""
echo "All daemons running:"
ps aux | grep "run_daemon.py" | grep -v grep | awk '{print "  " $12, $13, "PID:"$2}'
echo ""
echo "Logs: $LOGDIR/"
echo "Monitor: tail -f $LOGDIR/reviewer.log"
