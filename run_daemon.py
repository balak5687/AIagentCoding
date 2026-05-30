#!/usr/bin/env python3
"""
Launch a single agent daemon. Called by start_agents.sh, one per tmux pane.

Usage:
    python3 run_daemon.py coder           # legacy single coder
    python3 run_daemon.py backend_coder
    python3 run_daemon.py frontend_coder
    python3 run_daemon.py architect
    python3 run_daemon.py compile         # no LLM — deterministic
    python3 run_daemon.py reviewer
    python3 run_daemon.py peer            # legacy
    [--debug]
"""
import sys
from src.bus import FileMessageBus
from src.core.agent_runner import AgentRunner
from src.daemon import (
    make_coder_daemon,
    make_backend_coder_daemon,
    make_frontend_coder_daemon,
    make_peer_daemon,
    make_reviewer_daemon,
    make_architect_daemon,
    CompileAgent,
)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_daemon.py <agent_name> [--debug]")
        sys.exit(1)

    agent_name = sys.argv[1]
    debug = "--debug" in sys.argv

    bus = FileMessageBus()

    # Compile agent needs no AgentRunner — purely deterministic
    if agent_name == "compile":
        agent = CompileAgent(bus, debug=debug)
        agent.run()
        sys.exit(0)

    runner = AgentRunner(mode="claude-code", config={"debug": debug, "timeout_seconds": 600})

    def _make_named_daemon(name, bus, runner, debug):
        """Create a coder daemon with a specific agent_name (for react_coder etc.)."""
        from src.daemon.coder_daemon import _make_daemon
        return _make_daemon(name, bus, runner, debug)

    makers = {
        "coder":          lambda: make_coder_daemon(bus, runner, debug),
        "backend_coder":  lambda: make_backend_coder_daemon(bus, runner, debug),
        "frontend_coder": lambda: make_frontend_coder_daemon(bus, runner, debug),
        "react_coder":    lambda: _make_named_daemon("react_coder", bus, runner, debug),
        "peer":           lambda: make_peer_daemon(bus, runner, debug),
        "reviewer":       lambda: make_reviewer_daemon(bus, runner, debug),
        "architect":      lambda: make_architect_daemon(bus, runner, debug),
    }

    if agent_name not in makers:
        print(f"Unknown agent: {agent_name}. Available: {', '.join(makers)}")
        sys.exit(1)

    daemon = makers[agent_name]()
    daemon.run()
