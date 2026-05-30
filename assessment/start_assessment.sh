#!/bin/bash
# Launch GarageHQ technology assessment with live persona debate in tmux

SESSION="garagehq-assessment"
DIR="$(cd "$(dirname "$0")" && pwd)"

# Kill existing session
tmux kill-session -t "$SESSION" 2>/dev/null

# Reset conversation file
cat > "$DIR/conversation.md" << 'CONV'
# GarageHQ Technology Assessment — Flutter vs Alternatives

**Question**: Is Flutter Web the right technology choice for a garage management SaaS aimed at independent garages and SME workshops?

**Context**: GarageHQ is a full-stack garage management platform (job tracking, invoicing, inventory, supplier management, customer portal). Currently built with Python/Flask backend + Flutter/Dart frontend. Targeting independent garages and multi-branch workshops.

---

## MARKET RESEARCH
*[Pending — Market Research Agent]*

---

## ROUND 1 — Opening Positions

### Product Manager
*[Pending]*

### Technical Architect
*[Pending]*

### Customer (Garage Owner)
*[Pending]*

---

## ROUND 2 — Responses & Challenges

### Product Manager responds
*[Pending]*

### Technical Architect responds
*[Pending]*

### Customer responds
*[Pending]*

---

## DEVIL'S ADVOCATE — Final Challenge
*[Pending — Opus]*

---

## SYNTHESIS & VERDICT
*[Pending]*
CONV

# Create tmux session
tmux new-session -d -s "$SESSION" -n "assessment" -x 260 -y 60

# Pane 0: Market Research (runs first, feeds all personas)
tmux send-keys -t "$SESSION:0.0" \
  "cd $DIR && echo '🔍 MARKET RESEARCH AGENT' && python3 run_market_research.py" Enter

# Pane 1: PM Agent
tmux split-window -h -t "$SESSION:0"
tmux send-keys -t "$SESSION:0.1" \
  "cd $DIR && echo '👔 PRODUCT MANAGER' && sleep 5 && python3 run_persona.py pm" Enter

# Pane 2: Architect Agent
tmux split-window -v -t "$SESSION:0.0"
tmux send-keys -t "$SESSION:0.2" \
  "cd $DIR && echo '🏗️  TECHNICAL ARCHITECT' && sleep 5 && python3 run_persona.py architect" Enter

# Pane 3: Customer Agent
tmux split-window -v -t "$SESSION:0.1"
tmux send-keys -t "$SESSION:0.3" \
  "cd $DIR && echo '🔧 CUSTOMER (Garage Owner)' && sleep 5 && python3 run_persona.py customer" Enter

# Pane 4: Devil's Advocate (Opus — waits for all round 1s)
tmux select-layout -t "$SESSION:0" tiled
tmux split-window -h -t "$SESSION:0.2"
tmux send-keys -t "$SESSION:0.4" \
  "cd $DIR && echo '😈 DEVIL\\'S ADVOCATE (Opus)' && sleep 10 && python3 run_persona.py devils_advocate" Enter

tmux select-layout -t "$SESSION:0" tiled

echo ""
echo "✓ Assessment started in tmux session: $SESSION"
echo ""
echo "  Attach to watch live: tmux attach -t $SESSION"
echo ""
echo "  Pane 0: Market Research  (Sonnet — web research)"
echo "  Pane 1: Product Manager  (Sonnet — business view)"
echo "  Pane 2: Architect        (Sonnet — technical view)"
echo "  Pane 3: Customer         (Sonnet — garage owner view)"
echo "  Pane 4: Devil's Advocate (Opus   — challenges all)"
echo ""
echo "  Output: $DIR/conversation.md"
echo ""
echo "  Watch output build: watch -n 5 'wc -l $DIR/conversation.md'"
