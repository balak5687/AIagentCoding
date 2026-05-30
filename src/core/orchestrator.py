import asyncio
import re
from typing import Dict, List, Any
from ..workflows.sequential import SequentialOrchestrator
from ..workflows.parallel import ParallelExecutor
from ..workflows.conversation import ConversationLoop
from ..tools.playbook_loader import PlaybookLoader


class SDLCOrchestrator:
    """Main orchestrator coordinating all phases"""

    def __init__(self, runner, config):
        self.runner = runner
        self.config = config
        self.sequential = SequentialOrchestrator(runner)
        self.parallel = ParallelExecutor(runner)
        self.conversation = ConversationLoop(runner)
        self.playbook_loader = PlaybookLoader()

    async def process_github_issue(self, issue_url: str):
        """Complete SDLC workflow"""

        print("=== PHASE 1: Analysis (Sequential) ===")

        # Sequential phase: scanning, design, planning
        initial_context = {"github_issue": issue_url}

        # For now, we'll implement a simplified flow
        # In production, you'd have github_scanner and context_agent
        design = self.runner.run("designer", initial_context)
        print(f"Design completed with confidence: {design.metadata.get('confidence', 'N/A')}")

        plan = self.runner.run("planner", design.raw)
        print(f"Plan completed with confidence: {plan.metadata.get('confidence', 'N/A')}")

        # Extract tasks from plan
        tasks = self._parse_tasks(plan)
        print(f"Extracted {len(tasks)} tasks from plan")

        # Enhance tasks with playbooks
        tasks = self._enrich_tasks_with_playbooks(tasks)

        if not tasks:
            return {"status": "error", "reason": "No tasks extracted from plan"}

        print("\n=== PHASE 2: Implementation (Parallel + Conversation) ===")

        # Execute with parallel/serial logic
        task_results = await self.parallel.execute_tasks(tasks, self.conversation)

        print(f"\n=== PHASE 3: Complete ===")
        print(f"Successfully completed {len(task_results)} tasks")

        return {
            "status": "success",
            "tasks_completed": len(task_results),
            "results": task_results
        }

    def _parse_tasks(self, plan_message) -> List[Dict]:
        """Parse tasks from planner output"""
        tasks = []

        # Extract Task Breakdown section
        task_breakdown = plan_message.sections.get("Task Breakdown", "")

        if not task_breakdown:
            print("[WARNING] No 'Task Breakdown' section found in plan")
            return tasks

        # Parse each task (### Task N: Name)
        task_pattern = r'### Task \d+: (.+?)\n(.*?)(?=### Task \d+:|$)'
        matches = re.findall(task_pattern, task_breakdown, re.DOTALL)

        for task_name, task_body in matches:
            task = {"name": task_name.strip()}

            # Extract fields
            id_match = re.search(r'- \*\*ID\*\*: (.+)', task_body)
            desc_match = re.search(r'- \*\*Description\*\*: (.+)', task_body)
            files_match = re.search(r'- \*\*Files\*\*: (.+)', task_body)
            deps_match = re.search(r'- \*\*Dependencies\*\*: \[(.*?)\]', task_body)

            if id_match:
                task["id"] = id_match.group(1).strip()
            if desc_match:
                task["description"] = desc_match.group(1).strip()
            if files_match:
                task["files"] = files_match.group(1).strip()
            if deps_match:
                deps_str = deps_match.group(1).strip()
                task["dependencies"] = [d.strip() for d in deps_str.split(",")] if deps_str else []
            else:
                task["dependencies"] = []

            # Fallback: use task name as ID if not specified
            if "id" not in task:
                task["id"] = f"task_{len(tasks) + 1}"

            tasks.append(task)

        return tasks

    def _enrich_tasks_with_playbooks(self, tasks: List[Dict]) -> List[Dict]:
        """Add playbook information to tasks that match playbooks"""
        for task in tasks:
            # Check if task specifies a playbook
            playbook_name = task.get("playbook")

            if playbook_name and playbook_name != "null":
                # Load the playbook
                playbook = self.playbook_loader.get_playbook(playbook_name)
                if playbook:
                    task["playbook_content"] = self.playbook_loader.format_playbook_for_agent(playbook)
                    task["approach"] = "deterministic"
                    print(f"  Task '{task.get('name')}' using playbook: {playbook_name}")
                else:
                    print(f"  Warning: Playbook {playbook_name} not found for task '{task.get('name')}'")
                    task["approach"] = "cognitive"
            else:
                # Try to find a matching playbook
                task_desc = task.get("description", "") + " " + task.get("name", "")
                matching_playbook = self.playbook_loader.find_matching_playbook(task_desc)

                if matching_playbook:
                    playbook_name = matching_playbook.get("_file", "unknown")
                    task["playbook"] = playbook_name
                    task["playbook_content"] = self.playbook_loader.format_playbook_for_agent(matching_playbook)
                    task["approach"] = "deterministic"
                    print(f"  Task '{task.get('name')}' auto-matched playbook: {playbook_name}")
                else:
                    task["approach"] = "cognitive"

        return tasks
