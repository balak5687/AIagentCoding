"""
FileMessageBus — agents communicate via JSON files in .agent-bus/
Each message: .agent-bus/{agent}/inbox/{timestamp}_{task_id}.json
"""
import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List

BUS_ROOT = Path(".agent-bus")


class FileMessageBus:

    def __init__(self, bus_root: Path = BUS_ROOT):
        self.root = bus_root

    def _inbox(self, agent: str) -> Path:
        p = self.root / agent / "inbox"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _outbox(self, agent: str) -> Path:
        p = self.root / agent / "outbox"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def send(self, to: str, task_id: str, payload: Dict[str, Any], from_agent: str = "orchestrator") -> Path:
        """Drop a message into an agent's inbox."""
        msg = {
            "id": str(uuid.uuid4()),
            "task_id": task_id,
            "from": from_agent,
            "timestamp": time.time(),
            "payload": payload,
        }
        ts = int(time.time() * 1000)
        path = self._inbox(to) / f"{ts}_{task_id}.json"
        path.write_text(json.dumps(msg, indent=2))
        return path

    def receive(self, agent: str) -> Optional[Dict[str, Any]]:
        """Read and remove the oldest message from inbox. Returns None if empty."""
        inbox = self._inbox(agent)
        messages = sorted(inbox.glob("*.json"))
        if not messages:
            return None
        msg_file = messages[0]
        msg = json.loads(msg_file.read_text())
        msg_file.unlink()
        return msg

    def pending(self, agent: str) -> int:
        return len(list(self._inbox(agent).glob("*.json")))

    def peek(self, agent: str) -> List[Dict]:
        inbox = self._inbox(agent)
        return [json.loads(f.read_text()) for f in sorted(inbox.glob("*.json"))]

    def ack(self, agent: str, task_id: str, result: Dict[str, Any]) -> None:
        """Write result to outbox for orchestrator to collect."""
        ts = int(time.time() * 1000)
        path = self._outbox(agent) / f"{ts}_{task_id}.json"
        path.write_text(json.dumps({
            "task_id": task_id,
            "result": result,
            "timestamp": time.time()
        }, indent=2))

    def collect_results(self, agent: str) -> List[Dict]:
        """Collect and remove all completed results from outbox."""
        outbox = self._outbox(agent)
        results = []
        for f in sorted(outbox.glob("*.json")):
            results.append(json.loads(f.read_text()))
            f.unlink()
        return results

    def wait_for_task(self, agent: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Check outbox for a specific task_id result. Returns result dict or None."""
        outbox = self._outbox(agent)
        for f in sorted(outbox.glob(f"*_{task_id}.json")):
            result = json.loads(f.read_text())
            f.unlink()
            return result
        return None
