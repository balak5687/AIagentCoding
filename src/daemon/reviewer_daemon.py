"""
Reviewer Daemon — pre: inject current file state
                  post: approved → apply diff + ack orchestrator
                        rejected/minor → back to coder/inbox with feedback
"""
from pathlib import Path
from ..tools.diff_editor import DiffEditor, EditFailedException
from .base import AgentDaemon
from ..bus import FileMessageBus
from ..core.agent_runner import AgentRunner


def make_reviewer_daemon(bus: FileMessageBus, runner: AgentRunner, debug: bool = False) -> AgentDaemon:
    daemon = AgentDaemon("reviewer", bus, runner, debug=debug)
    diff_editor = DiffEditor()

    # PRE-HOOK: inject current file state so reviewer sees what's actually on disk
    def inject_file_state(context: dict) -> dict:
        task = context.get("task", {})
        target = task.get("files", "").strip("`").split(",")[0].strip().strip("`")
        if target and Path(target).exists():
            context["current_file_state"] = Path(target).read_text()
            if debug:
                print(f"  [reviewer pre-hook] injected current state of {target}")
        return context

    # POST-HOOK: route based on reviewer decision
    def route_and_apply(output, msg, bus: FileMessageBus):
        task_id = msg["task_id"]
        task = msg["payload"].get("task", {})
        iteration = msg["payload"].get("iteration", 1)
        status = output.metadata.get("status", "")

        if status == "approved":
            from ..core.protocol import AgentMessage
            coder_raw = msg["payload"].get("code_changes", "")
            coder_msg = AgentMessage(coder_raw)
            changes = coder_msg.extract_code_changes()
            target = task.get("files", "")

            # Strip backticks and use first file as primary target
            target = target.strip("`").split(",")[0].strip().strip("`")

            applied = 0
            failed = 0

            # New file: if target doesn't exist, extract full code block and write it
            if target and not Path(target).exists():
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                # Extract first replace block as full file content
                if changes:
                    Path(target).write_text(changes[0]["replace"])
                    applied += 1
                    changes = changes[1:]  # remaining changes applied normally
                    if debug:
                        print(f"  [reviewer post-hook] created new file: {target}")

            for change in changes:
                try:
                    if target and Path(target).exists():
                        diff_editor.apply_edit(target, change["search"], change["replace"])
                        applied += 1
                    else:
                        failed += 1
                except EditFailedException as e:
                    print(f"  [reviewer post-hook] diff failed: {e}")
                    failed += 1

            print(f"  [reviewer post-hook] task {task_id} APPROVED — {applied} applied, {failed} failed")

            # Feed approved code into coding brain — only after reviewer sign-off
            if applied > 0 and target and Path(target).exists():
                from ..brain import client as brain_client
                if brain_client.is_running():
                    brain_client.ingest(
                        content=Path(target).read_text(),
                        source=f"approved/{task_id}/{Path(target).name}",
                        brain="coding"
                    )
                    if debug:
                        print(f"  [reviewer post-hook] fed approved code into coding brain: {Path(target).name}")

            bus.ack("reviewer", task_id, {
                "status": "approved",
                "task_id": task_id,
                "diffs_applied": applied,
                "diffs_failed": failed,
            })

        elif status in ("needs_minor_fixes", "rejected"):
            import re as _re
            raw_files = task.get("files", "")
            _m = _re.search(r'`(/[^`]+)`', raw_files)
            _target = _m.group(1) if _m else raw_files
            if "/GreasyNutsReact/" in _target or _target.endswith(('.ts','.tsx','.js','.jsx')):
                _coder = "react_coder"
            elif ".dart" in _target:
                _coder = "frontend_coder"
            else:
                _coder = "backend_coder"
            print(f"  [reviewer post-hook] task {task_id} {status} → {_coder}/inbox (iteration {iteration + 1})")
            bus.send(_coder, task_id, {
                "task": task,
                "review_feedback": output.raw,
                "iteration": iteration + 1,
            }, from_agent="reviewer")

        else:
            print(f"  [reviewer post-hook] task {task_id} unknown status: {status}")
            bus.ack("reviewer", task_id, {"status": "unknown", "task_id": task_id})

    daemon.add_pre_hook(inject_file_state)
    daemon.add_post_hook(route_and_apply)
    return daemon
