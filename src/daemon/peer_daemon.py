"""
Peer Daemon — pre: reads coder stuck message
              post: sends guidance back to coder/inbox
              watchdog: if coder inbox has old task, proactively offer help
"""
import time
from .base import AgentDaemon
from ..bus import FileMessageBus
from ..core.agent_runner import AgentRunner

WATCHDOG_THRESHOLD = 120  # seconds before peer proactively checks on coder


def make_peer_daemon(bus: FileMessageBus, runner: AgentRunner, debug: bool = False) -> AgentDaemon:
    daemon = AgentDaemon("peer", bus, runner, debug=debug)

    # Track coder inbox task arrival times for watchdog
    _coder_task_times: dict = {}

    # PRE-HOOK: log what coder was stuck on
    def log_stuck(context: dict) -> dict:
        task = context.get("task", {})
        if debug:
            print(f"  [peer pre-hook] helping with task: {task.get('id')} — {task.get('name', '')[:60]}")
        return context

    # POST-HOOK: send guidance back to coder
    def send_guidance(output, msg, bus: FileMessageBus):
        task_id = msg["task_id"]
        original_task = msg["payload"].get("task", {})
        iteration = msg["payload"].get("iteration", 1)

        print(f"  [peer post-hook] task {task_id} → coder/inbox (guidance ready)")
        bus.send("coder", task_id, {
            "task": original_task,
            "peer_guidance": output.raw,
            "iteration": iteration + 1,
        }, from_agent="peer")

    # WATCHDOG: called on idle — checks if coder has stale tasks
    def watchdog():
        coder_msgs = bus.peek("coder")
        now = time.time()
        for msg in coder_msgs:
            task_id = msg["task_id"]
            age = now - msg["timestamp"]
            if age > WATCHDOG_THRESHOLD:
                task = msg["payload"].get("task", {})
                print(f"  [peer watchdog] task {task_id} has been in coder inbox for {int(age)}s — proactively queuing help")
                # Don't pull from coder inbox (coder will still process it)
                # Just log for now; full proactive intervention requires coder coordination
                # TODO: in daemon v2, signal coder to pause and accept peer help

    daemon.add_pre_hook(log_stuck)
    daemon.add_post_hook(send_guidance)
    daemon._on_idle = watchdog
    return daemon
