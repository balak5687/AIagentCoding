"""
ConversationLoop — routes tasks to the correct coder daemon based on file type,
waits for reviewer/outbox result.

V2 routing:
  .dart / /frontend/ → frontend_coder/inbox
  .py   / /backend/  → backend_coder/inbox
  fallback            → coder/inbox (legacy)
"""
import asyncio
import time
from typing import Dict, Any
from ..bus import FileMessageBus

POLL_INTERVAL = 3
TASK_TIMEOUT  = 1800  # 30 min — tasks can take long with multi-iteration review


class MaxIterationsExceeded(Exception):
    pass


def _route_coder(task: dict) -> str:
    """Detect coder inbox from file extension. Handles markdown paths like: - `/path/file.py`"""
    raw = task.get("files", "")
    # Extract path from backtick-quoted markdown: `...`
    import re as _re
    m = _re.search(r'`(/[^`]+)`', raw)
    target = m.group(1) if m else raw.split(",")[0].split("\n")[0].strip().strip("- ").strip("`")

    if target.endswith((".tsx", ".jsx", ".ts", ".js")) or "/GreasyNutsReact/" in target:
        return "react_coder"
    if target.endswith(".dart") or "/flutter_prototype/" in target:
        return "frontend_coder"
    if target.endswith(".py") or "/GreasyNuts/" in target:
        return "backend_coder"
    return "coder"


class ConversationLoop:

    def __init__(self, runner=None, bus: FileMessageBus = None):
        self.runner = runner
        self.bus = bus or FileMessageBus()

    async def execute_task(self, task: Dict, max_iterations: int = 5) -> Dict:
        """Route task to correct coder, wait for reviewer/outbox result."""
        task_id = task.get("id", "unknown")
        coder_inbox = _route_coder(task)

        print(f"  [orchestrator] queuing {task_id} → {coder_inbox}/inbox")
        self.bus.send(coder_inbox, task_id, {"task": task, "iteration": 1}, from_agent="orchestrator")

        start = time.time()
        while time.time() - start < TASK_TIMEOUT:
            await asyncio.sleep(POLL_INTERVAL)
            result = self.bus.wait_for_task("reviewer", task_id)
            if result:
                r = result.get("result", result)
                status = r.get("status", "unknown")
                elapsed = int(time.time() - start)
                print(f"  [orchestrator] task {task_id} → {status} ({elapsed}s)")
                return {
                    "task": task,
                    "status": status,
                    "diffs_applied": r.get("diffs_applied", 0),
                    "diffs_failed": r.get("diffs_failed", 0),
                }

        raise MaxIterationsExceeded(f"Task {task_id} timed out after {TASK_TIMEOUT}s")
