"""
AgentDaemon base — watches inbox, runs pre-hooks, invokes claude, runs post-hooks.
Each daemon runs as a persistent process in its own tmux pane.

Parallel execution: when multiple messages land in inbox simultaneously (same
dependency group), the daemon spawns one thread per message up to MAX_CONCURRENCY.
Each thread runs its own subprocess.run(claude) call — fully independent.
"""
import time
import traceback
import threading
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from ..bus import FileMessageBus
from ..core.agent_runner import AgentRunner

POLL_INTERVAL = 2   # seconds between inbox checks
MAX_CONCURRENCY = 4  # max parallel claude subprocesses per daemon


class AgentDaemon:

    def __init__(self, agent_name: str, bus: FileMessageBus, runner: AgentRunner,
                 debug: bool = False, max_concurrency: int = MAX_CONCURRENCY):
        self.agent_name = agent_name
        self.bus = bus
        self.runner = runner
        self.debug = debug
        self.max_concurrency = max_concurrency
        self._pre_hooks: List[Callable] = []
        self._post_hooks: List[Callable] = []
        self._running = False
        self._semaphore = threading.Semaphore(max_concurrency)
        self._active = 0
        self._lock = threading.Lock()

    def add_pre_hook(self, fn: Callable) -> None:
        self._pre_hooks.append(fn)

    def add_post_hook(self, fn: Callable) -> None:
        self._post_hooks.append(fn)

    def run(self) -> None:
        """Main loop — drains inbox, spawns a thread per message up to max_concurrency."""
        self._running = True
        print(f"[{self.agent_name}] daemon started (max_concurrency={self.max_concurrency})")

        while self._running:
            # Drain all available messages and dispatch in parallel
            dispatched = 0
            while True:
                # Only pick a message if we have capacity
                if not self._semaphore.acquire(blocking=False):
                    break  # At capacity — wait for a slot to free

                msg = self.bus.receive(self.agent_name)
                if msg is None:
                    self._semaphore.release()
                    break  # Inbox empty

                task_id = msg.get("task_id", "unknown")
                with self._lock:
                    self._active += 1

                print(f"[{self.agent_name}] dispatching task {task_id} "
                      f"(active={self._active}/{self.max_concurrency})")

                t = threading.Thread(
                    target=self._process_with_semaphore,
                    args=(msg,),
                    daemon=True,
                    name=f"{self.agent_name}-{task_id}"
                )
                t.start()
                dispatched += 1

            if dispatched == 0:
                self._on_idle()
                time.sleep(POLL_INTERVAL)

    def _process_with_semaphore(self, msg: Dict[str, Any]) -> None:
        """Wrapper that ensures semaphore is released after processing."""
        task_id = msg.get("task_id", "unknown")
        try:
            self._check_branch_guard(msg)
            self._process(msg)
        except Exception as e:
            print(f"[{self.agent_name}] ERROR on task {task_id}: {e}")
            if self.debug:
                traceback.print_exc()
            self.bus.ack(self.agent_name, task_id, {
                "status": "error",
                "error": str(e),
                "task_id": task_id,
            })
        finally:
            self._semaphore.release()
            with self._lock:
                self._active -= 1
            if self.debug:
                print(f"[{self.agent_name}] task {task_id} done (active={self._active})")

    def _process(self, msg: Dict[str, Any]) -> None:
        task_id = msg["task_id"]
        context = msg["payload"]

        # Run pre-hooks (each can enrich context)
        for hook in self._pre_hooks:
            context = hook(context) or context

        # Invoke claude via AgentRunner
        output = self.runner.run(self.agent_name, context)

        # Run post-hooks (routing, diff application, etc.)
        for hook in self._post_hooks:
            hook(output, msg, self.bus)

        if self.debug:
            print(f"[{self.agent_name}] task {task_id} complete — status: {output.metadata.get('status')}")

    def _on_idle(self) -> None:
        """Called when inbox is empty. Override for watchdog logic."""
        pass

    def _check_branch_guard(self, msg: Dict[str, Any]) -> None:
        """Abort hard if any target repo is on a protected branch."""
        import subprocess
        protected = {"main", "master", "dev", "prod", "production"}
        task = msg.get("payload", {}).get("task", {})
        target = task.get("files", "")
        if not target:
            return
        # Find git repo root for the target file
        target_path = target.strip("`").split(",")[0].strip()
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(Path(target_path).parent),
                capture_output=True, text=True
            )
            repo_root = result.stdout.strip()
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_root, capture_output=True, text=True
            ).stdout.strip()
            if branch in protected:
                raise RuntimeError(
                    f"BRANCH GUARD: refusing to work — repo at {repo_root} is on protected branch '{branch}'. "
                    f"Switch to a feature/testing branch first."
                )
            if self.debug:
                print(f"  [branch guard] ✓ {branch} is safe")
        except RuntimeError:
            raise
        except Exception:
            pass  # Not a git repo or can't determine — allow through

    def stop(self) -> None:
        self._running = False
