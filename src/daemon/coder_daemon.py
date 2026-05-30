"""
Coder Daemons — Backend and Frontend specialists.

Routes based on task file extension:
  .py   → backend_coder
  .dart → frontend_coder

Post-coder hook:
  stuck (iteration>=2 and no peer yet) → architect/inbox
  else → compile/inbox (compile agent gates before reviewer)
"""
import time
from pathlib import Path
from .base import AgentDaemon
from ..bus import FileMessageBus
from ..core.agent_runner import AgentRunner

PEER_TRIGGER_ITERATION = 2  # escalate to architect after this many reviewer rejections


def _detect_type(task: dict) -> str:
    """Detect backend vs frontend from file extension."""
    target = task.get("files", "").strip("`").split(",")[0].strip().strip("`")
    if target.endswith(".dart") or "/frontend/" in target:
        return "frontend"
    return "backend"


def _make_daemon(agent_name: str, bus: FileMessageBus, runner: AgentRunner, debug: bool) -> AgentDaemon:
    daemon = AgentDaemon(agent_name, bus, runner, debug=debug)

    # PRE-HOOK: inject existing file + repo map + flutter skill + peer/architect guidance
    def inject_context(context: dict) -> dict:
        task = context.get("task", context)
        target = task.get("files", "").strip("`").split(",")[0].strip().strip("`")
        if target and Path(target).exists():
            context["existing_code"] = Path(target).read_text()
            if debug:
                print(f"  [{agent_name} pre-hook] injected {len(context['existing_code'])} chars from {target}")

        # Inject repo map for the target file (symbol-level index to avoid hallucination)
        if target:
            try:
                from ..brain import client as brain_client
                if brain_client.is_running():
                    repo_map_data = brain_client.get_repo_map(target)
                    if repo_map_data.get("symbols"):
                        context["repo_map"] = repo_map_data
                        if debug:
                            print(f"  [{agent_name} pre-hook] injected repo_map: "
                                  f"{len(repo_map_data['symbols'])} symbols for {target}")
            except Exception:
                pass  # Brain server unavailable — silently skip

        # Inject matching Flutter skill for frontend tasks
        if agent_name == "frontend_coder":
            try:
                from ..tools.skill_matcher import find_skill, find_skill_name
                task_desc = task.get("description", "") + " " + task.get("name", "")
                skill_content = find_skill(task_desc)
                if skill_content:
                    skill_name = find_skill_name(task_desc)
                    context["flutter_skill"] = skill_content
                    context["flutter_skill_name"] = skill_name
                    if debug:
                        print(f"  [{agent_name} pre-hook] injected flutter skill: {skill_name}")
            except Exception:
                pass

        # Log if compile errors or architect guidance present
        if context.get("compile_errors") and debug:
            print(f"  [{agent_name} pre-hook] compile errors present: {len(context['compile_errors'])}")
        if context.get("architect_guidance") and debug:
            print(f"  [{agent_name} pre-hook] architect guidance present")
        if context.get("peer_guidance") and debug:
            print(f"  [{agent_name} pre-hook] peer guidance present")

        if task.get("playbook_content"):
            context["playbook_name"] = task.get("playbook")
            context["playbook"] = task["playbook_content"]

        return context

    # POST-HOOK: route to architect (if stuck) or compile agent
    def route(output, msg, bus: FileMessageBus):
        task = msg["payload"].get("task", msg["payload"])
        task_id = msg["task_id"]
        iteration = msg["payload"].get("iteration", 1)
        has_guidance = bool(msg["payload"].get("architect_guidance") or msg["payload"].get("peer_guidance"))

        needs_architect = (
            output.metadata.get("request_peer") or
            (iteration >= PEER_TRIGGER_ITERATION and not has_guidance)
        )

        if needs_architect:
            print(f"  [{agent_name} post-hook] task {task_id} → architect/inbox (iteration {iteration})")
            bus.send("architect", task_id, {
                "task": task,
                "coder_attempt": output.raw,
                "review_feedback": msg["payload"].get("review_feedback", ""),
                "compile_errors": msg["payload"].get("compile_errors", []),
                "iteration": iteration,
                "mode": "guidance",
            }, from_agent=agent_name)
        else:
            print(f"  [{agent_name} post-hook] task {task_id} → compile/inbox (iteration {iteration})")
            bus.send("compile", task_id, {
                "task": task,
                "code_changes": output.raw,
                "iteration": iteration,
            }, from_agent=agent_name)

    daemon.add_pre_hook(inject_context)
    daemon.add_post_hook(route)
    return daemon


def make_backend_coder_daemon(bus: FileMessageBus, runner: AgentRunner, debug: bool = False) -> AgentDaemon:
    return _make_daemon("backend_coder", bus, runner, debug)


def make_frontend_coder_daemon(bus: FileMessageBus, runner: AgentRunner, debug: bool = False) -> AgentDaemon:
    return _make_daemon("frontend_coder", bus, runner, debug)


def make_coder_daemon(bus: FileMessageBus, runner: AgentRunner, debug: bool = False) -> AgentDaemon:
    """Legacy single coder — kept for backward compatibility."""
    return _make_daemon("coder", bus, runner, debug)
