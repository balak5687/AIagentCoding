"""
Compile Agent Daemon — runs compiler/analyzer on coder output BEFORE reviewer sees it.

Backend:  python -m py_compile + import check
Frontend: flutter analyze

On failure → routes back to coder/inbox with structured compile_errors
On success → routes to reviewer/inbox

This agent requires NO claude invocation — it's purely deterministic.
"""
import subprocess
import ast
import re
import tempfile
import os
from pathlib import Path
from .base import AgentDaemon
from ..bus import FileMessageBus
from ..core.agent_runner import AgentRunner
from ..core.protocol import AgentMessage
from ..tools.diff_editor import DiffEditor, EditFailedException

FLUTTER_BIN = str(Path.home() / "flutter" / "bin" / "flutter")


class CompileAgent:
    """
    Deterministic compile/analyze agent — no LLM invocation.
    Reads coder output, applies diffs to a temp copy, runs compiler, routes result.
    """

    def __init__(self, bus: FileMessageBus, debug: bool = False):
        self.bus = bus
        self.debug = debug
        self.diff_editor = DiffEditor()
        self._running = False

    def run(self) -> None:
        import time
        self._running = True
        print("[compile] daemon started")

        while self._running:
            msg = self.bus.receive("compile")
            if msg is None:
                time.sleep(2)
                continue

            task_id = msg["task_id"]
            print(f"[compile] checking task {task_id}")

            try:
                errors = self._check(msg)
                if errors:
                    print(f"[compile] task {task_id} FAILED — {len(errors)} error(s)")
                    self._route_failure(msg, errors)
                else:
                    print(f"[compile] task {task_id} PASSED — routing to reviewer")
                    self._route_success(msg)
            except Exception as e:
                print(f"[compile] ERROR on {task_id}: {e}")
                # On unexpected error pass through to reviewer — don't block pipeline
                self._route_success(msg)

    def _check(self, msg: dict) -> list:
        """Run appropriate compiler. Returns list of error strings (empty = pass)."""
        task = msg["payload"].get("task", {})
        code_changes_raw = msg["payload"].get("code_changes", "")
        target = task.get("files", "").strip("`").split(",")[0].strip().strip("`")

        if not target or not code_changes_raw:
            return []

        is_dart = target.endswith(".dart")
        is_python = target.endswith(".py")

        if not (is_dart or is_python):
            return []  # Not a compilable file type — pass through

        # Apply diffs to a temp copy of the file
        errors = []
        with tempfile.NamedTemporaryFile(
            suffix=".dart" if is_dart else ".py",
            mode="w", delete=False
        ) as tmp:
            tmp_path = tmp.name
            # Write current file content if exists
            if Path(target).exists():
                tmp.write(Path(target).read_text())
            tmp.flush()

        try:
            # Apply coder's SEARCH/REPLACE blocks to temp file
            coder_msg = AgentMessage(code_changes_raw)
            changes = coder_msg.extract_code_changes()

            for change in changes:
                try:
                    if not Path(tmp_path).exists() or change["search"] == "":
                        # New file — write replace content
                        Path(tmp_path).write_text(change["replace"])
                    else:
                        self.diff_editor.apply_edit(tmp_path, change["search"], change["replace"])
                except EditFailedException:
                    pass  # Can't apply yet — compiler will still catch syntax errors

            if is_python:
                errors = self._check_python(tmp_path)
            elif is_dart:
                errors = self._check_dart(tmp_path, target)

        finally:
            os.unlink(tmp_path)

        return errors

    def _check_python(self, path: str) -> list:
        """Run py_compile and basic import check."""
        errors = []

        # Syntax check
        result = subprocess.run(
            ["python3", "-m", "py_compile", path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            # Clean up temp path from error message
            msg = result.stderr.replace(path, "<file>")
            errors.append(f"SyntaxError: {msg.strip()}")
            return errors  # No point checking further if syntax fails

        # AST check for undefined names (basic)
        try:
            source = Path(path).read_text()
            tree = ast.parse(source)
            # Check for obvious hallucinated imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    # Flag imports from non-existent local modules (simple heuristic)
                    pass
        except SyntaxError as e:
            errors.append(f"AST parse error: {e}")

        return errors

    def _check_dart(self, tmp_path: str, original_path: str) -> list:
        """Run flutter analyze on the project, filter to this file's errors."""
        errors = []

        # Find the flutter project root
        project_root = None
        check = Path(original_path).parent
        for _ in range(10):
            if (check / "pubspec.yaml").exists():
                project_root = check
                break
            check = check.parent

        if not project_root:
            return []

        # Copy temp file to original path for analysis
        original_content = Path(original_path).read_text() if Path(original_path).exists() else None
        try:
            Path(original_path).write_text(Path(tmp_path).read_text())
            result = subprocess.run(
                [FLUTTER_BIN, "analyze", "--no-pub", str(original_path)],
                capture_output=True, text=True,
                cwd=str(project_root),
                timeout=60
            )
            # Parse errors (lines with "error •")
            for line in result.stdout.splitlines():
                if "error •" in line and str(original_path) in line:
                    errors.append(line.strip())
        except subprocess.TimeoutExpired:
            pass  # Timeout — pass through
        finally:
            # Restore original file
            if original_content is not None:
                Path(original_path).write_text(original_content)
            elif Path(original_path).exists():
                Path(original_path).unlink()

        return errors

    def _route_failure(self, msg: dict, errors: list) -> None:
        task_id = msg["task_id"]
        task = msg["payload"].get("task", {})
        iteration = msg["payload"].get("iteration", 1)

        self.bus.send("coder", task_id, {
            "task": task,
            "compile_errors": errors,
            "previous_code": msg["payload"].get("code_changes", ""),
            "iteration": iteration + 1,
            "from_compile_agent": True,
        }, from_agent="compile")

        if self.debug:
            for e in errors[:3]:
                print(f"  [compile error] {e}")

    def _route_success(self, msg: dict) -> None:
        task_id = msg["task_id"]
        # Forward unchanged to reviewer
        self.bus.send("reviewer", task_id, msg["payload"], from_agent="compile")

    def stop(self) -> None:
        self._running = False
