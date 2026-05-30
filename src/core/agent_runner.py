"""
Agent Runner - Invokes agents via Claude Code CLI.
Queries Project Brain Server (background process) for context — no model loading here.
"""
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from .protocol import AgentMessage
from ..brain import client as brain_client

# designer/planner need deep reasoning → opus (1M context)
# coder/reviewer/peer need fast execution → sonnet (1M context)
OPUS_AGENTS = {"designer", "planner", "architect"}


class AgentRunner:
    def __init__(self, mode="claude-code", config=None):
        self.mode = mode
        self.config = config or {}
        self.debug = self.config.get("debug", False)
        self._current_agent = ""

    def run(self, agent_name: str, context: Any, max_retries: int = 3) -> AgentMessage:
        self._current_agent = agent_name

        agent_prompt = self._load_agent(agent_name)

        for attempt in range(max_retries):
            try:
                full_prompt = self._build_prompt(agent_prompt, context, attempt, agent_name)
                raw_output = self._invoke(full_prompt)

                if self.debug:
                    # Save raw output for debugging
                    output_file = Path(f"/tmp/agent_{agent_name}_output_attempt{attempt}.md")
                    output_file.write_text(raw_output)
                    print(f"[DEBUG] Raw output saved: {output_file}")
                    print(f"[DEBUG] First 500 chars: {raw_output[:500]}")

                message = AgentMessage(raw_output)

                if self._validate_output(agent_name, message):
                    # Only feed reviewer output into brain — not coder (unreviewed code pollutes)
                    if agent_name not in ("coder", "peer"):
                        self._feed_back_to_brain(agent_name, message)
                    return message

                context = self._add_retry_feedback(context, message, attempt)

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                context = self._add_error_feedback(context, e, attempt)

        raise RuntimeError(f"{agent_name} failed after {max_retries} attempts")

    def _load_agent(self, agent_name: str) -> str:
        agent_path = Path(f"agents/{agent_name}.md")
        if not agent_path.exists():
            raise FileNotFoundError(f"Agent definition not found: {agent_path}")
        return agent_path.read_text()

    def _fetch_brain_context(self, agent_name: str, context: Any) -> str:
        """Query the Brain Server (background process) for relevant context.
        Returns empty string if server not running — agents degrade gracefully."""
        if not brain_client.is_running():
            if self.debug:
                print(f"[DEBUG] Brain server not running — skipping context enrichment")
            return ""

        code_query = None
        knowledge_query = None

        if isinstance(context, dict):
            if agent_name == "designer":
                knowledge_query = context.get("requirement") or context.get("issue_description", "")
                code_query = "existing architecture dashboard patterns"
            elif agent_name == "planner":
                knowledge_query = str(context.get("design", ""))[:300]
            elif agent_name in ("coder", "backend_coder", "frontend_coder"):
                task = context.get("task", context)
                desc = task.get("description", task.get("name", ""))
                files = task.get("files", "")
                code_query = f"{desc} {files}".strip()[:200]
                knowledge_query = desc[:150]
            elif agent_name in ("reviewer",):
                task = context.get("task", {})
                code_query = task.get("files", "code patterns security conventions")
            elif agent_name == "architect":
                knowledge_query = str(context.get("design", context.get("coder_attempt", "")))[:300]
                code_query = "existing patterns architecture"

        try:
            ctx = brain_client.get_context(
                agent_name=agent_name,
                code_query=code_query,
                knowledge_query=knowledge_query,
                top_k=3
            )
            if ctx and "No relevant context" not in ctx:
                if self.debug:
                    print(f"[DEBUG] Brain context fetched: {len(ctx)} chars")
                return f"\n\n---\n\n# Project Brain Context\n\n{ctx}\n"
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Brain query failed: {e}")

        return ""

    def _build_prompt(self, agent_def: str, context: Any, attempt: int, agent_name: str = "") -> str:
        prompt = agent_def

        # Query brain server for context (lightweight HTTP call)
        brain_context = self._fetch_brain_context(agent_name, context)
        if brain_context:
            prompt += brain_context

        prompt += "\n\n---\n\n# Task Context\n\n"

        if isinstance(context, dict):
            prompt += yaml.dump(context, default_flow_style=False, sort_keys=False)
        else:
            prompt += str(context)

        if attempt > 0:
            prompt += f"\n\n(Retry attempt {attempt + 1})"

        return prompt

    def _invoke(self, prompt: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        try:
            model = self.config.get("model") or ("opus" if self._current_agent in OPUS_AGENTS else "sonnet")

            cmd = [
                "claude", "--print",
                "--model", model,
                "--dangerously-skip-permissions",
            ]

            if self.debug:
                print(f"[DEBUG] Agent: {self._current_agent} | Model: {model} | Prompt: {len(prompt)} chars")

            result = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                timeout=self.config.get("timeout_seconds", 600),
                stdout=subprocess.PIPE,
                stderr=None if self.debug else subprocess.PIPE
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude CLI exit {result.returncode}: {result.stderr or '(check terminal)'}")

            return result.stdout

        finally:
            if not self.debug:
                os.unlink(prompt_file)
            else:
                print(f"[DEBUG] Prompt preserved: {prompt_file}")

    def _feed_back_to_brain(self, agent_name: str, message: AgentMessage) -> None:
        """Feed agent output back into the live brain so future agents learn from it."""
        if not brain_client.is_running() or not message.content:
            return
        brain_target = "coding" if agent_name == "coder" else "functionality"
        brain_client.ingest(
            content=message.content,
            source=f"agent/{agent_name}/output",
            brain=brain_target
        )
        if self.debug:
            print(f"[DEBUG] Fed {agent_name} output back into {brain_target} brain")

    def _validate_output(self, agent_name: str, message: AgentMessage) -> bool:
        # Accept if either status OR agent field is present in frontmatter
        if "status" not in message.metadata and "agent" not in message.metadata:
            if self.debug:
                print(f"[DEBUG] Validation failed: missing status/agent in frontmatter. Got metadata: {message.metadata}")
            return False
        return True

    def _add_retry_feedback(self, context: Any, message: AgentMessage, attempt: int) -> Any:
        if isinstance(context, dict):
            context = context.copy()
            context["retry_feedback"] = {
                "attempt": attempt + 1,
                "previous_output": message.metadata,
                "previous_content": message.content[:2000] if message.content else "",
                "message": "Output validation failed. Ensure YAML frontmatter with agent: and status: fields is present."
            }
        return context

    def _add_error_feedback(self, context: Any, error: Exception, attempt: int) -> Any:
        if isinstance(context, dict):
            context = context.copy()
            context["error_feedback"] = {
                "attempt": attempt + 1,
                "error": str(error),
                "message": f"Execution failed: {error}. Please try again."
            }
        return context
