"""
Architect Daemon — two modes:
  feasibility: pre-planning review of design (→ planner or blocked)
  guidance:    mid-task help when coder stuck (→ coder/inbox with guidance)
"""
from .base import AgentDaemon
from ..bus import FileMessageBus
from ..core.agent_runner import AgentRunner


def make_architect_daemon(bus: FileMessageBus, runner: AgentRunner, debug: bool = False) -> AgentDaemon:
    daemon = AgentDaemon("architect", bus, runner, debug=debug)

    def route(output, msg, bus: FileMessageBus):
        task_id = msg["task_id"]
        mode = msg["payload"].get("mode", "guidance")
        status = output.metadata.get("status", "")

        if mode == "feasibility":
            if status == "blocked":
                print(f"  [architect post-hook] task {task_id} BLOCKED by architect")
                bus.ack("architect", task_id, {
                    "status": "blocked",
                    "task_id": task_id,
                    "architect_review": output.raw,
                })
            else:
                print(f"  [architect post-hook] feasibility APPROVED → planner can proceed")
                bus.ack("architect", task_id, {
                    "status": "approved",
                    "task_id": task_id,
                    "architect_review": output.raw,
                })

        elif mode == "guidance":
            task = msg["payload"].get("task", {})
            iteration = msg["payload"].get("iteration", 1)
            # Detect coder type from task
            import re
            raw = task.get("files", "")
            m = re.search(r'`(/[^`]+)`', raw)
            target = m.group(1) if m else raw
            if "/GreasyNutsReact/" in target or target.endswith(('.ts', '.tsx', '.js', '.jsx')):
                coder = "react_coder"
            elif ".dart" in target or "/flutter_prototype/" in target:
                coder = "frontend_coder"
            else:
                coder = "backend_coder"

            print(f"  [architect post-hook] task {task_id} guidance ready → {coder}/inbox")
            bus.send(coder, task_id, {
                "task": task,
                "architect_guidance": output.raw,
                "iteration": iteration + 1,
            }, from_agent="architect")

    daemon.add_post_hook(route)
    return daemon
