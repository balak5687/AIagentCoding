#!/bin/bash
# V2 Agent daemons — backend + React only (no Flutter)
SESSION="sdlc-agents"
DIR="$(cd "$(dirname "$0")" && pwd)"
DEBUG="${1:-}"

tmux kill-session -t "$SESSION" 2>/dev/null

tmux new-session -d -s "$SESSION" -n "agents" -x 240 -y 60

# Pane 0: backend_coder
tmux send-keys -t "$SESSION:0.0" "cd $DIR && python3 run_daemon.py backend_coder $DEBUG 2>&1 | tee logs/issue4/backend_coder.log" Enter

# Pane 1: react_coder
tmux split-window -h -t "$SESSION:0"
tmux send-keys -t "$SESSION:0.1" "cd $DIR && python3 run_daemon.py react_coder $DEBUG 2>&1 | tee logs/issue4/react_coder.log" Enter

# Pane 2: compile
tmux split-window -v -t "$SESSION:0.0"
tmux send-keys -t "$SESSION:0.2" "cd $DIR && python3 run_daemon.py compile $DEBUG 2>&1 | tee logs/issue4/compile.log" Enter

# Pane 3: architect
tmux split-window -v -t "$SESSION:0.1"
tmux send-keys -t "$SESSION:0.3" "cd $DIR && python3 run_daemon.py architect $DEBUG 2>&1 | tee logs/issue4/architect.log" Enter

# Pane 4: reviewer
tmux split-window -h -t "$SESSION:0.2"
tmux send-keys -t "$SESSION:0.4" "cd $DIR && python3 run_daemon.py reviewer $DEBUG 2>&1 | tee logs/issue4/reviewer.log" Enter

tmux select-layout -t "$SESSION:0" tiled

echo "✓ V2 daemons started: backend_coder | react_coder | compile | architect | reviewer"
echo "  Logs: /home/ubuntu/bala/AIagentCoding/logs/issue4/"
echo "  Attach: tmux attach -t $SESSION"
