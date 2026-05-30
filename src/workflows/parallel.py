import asyncio
from typing import List, Dict, Any
import networkx as nx


class ParallelExecutor:
    """Handles parallel task execution with dependency management"""

    def __init__(self, runner):
        self.runner = runner

    def build_dependency_graph(self, tasks: List[Dict]) -> nx.DiGraph:
        """Build task dependency graph"""
        G = nx.DiGraph()

        for task in tasks:
            task_id = task.get("id") or task.get("ID")
            if not task_id:
                raise ValueError(f"Task missing ID: {task}")

            G.add_node(task_id, task=task)

            dependencies = task.get("dependencies", task.get("Dependencies", []))
            for dep in dependencies:
                G.add_edge(dep, task_id)

        return G

    def get_execution_groups(self, graph: nx.DiGraph) -> List[List]:
        """Get groups of tasks that can run in parallel"""
        groups = []

        # Topological sort gives execution order
        for generation in nx.topological_generations(graph):
            group = [graph.nodes[node_id]["task"] for node_id in generation]
            groups.append(group)

        return groups

    async def execute_tasks(self, tasks: List[Dict], conversation_loop=None) -> List[Dict]:
        """Execute tasks with parallel/serial logic"""

        # Build dependency graph
        graph = self.build_dependency_graph(tasks)

        # Get execution groups
        groups = self.get_execution_groups(graph)

        all_results = []

        for i, group in enumerate(groups):
            print(f"[Parallel] Executing group {i+1}/{len(groups)} with {len(group)} task(s)")

            if len(group) == 1:
                # Single task - run sequentially
                result = await self._execute_single_task(group[0], conversation_loop)
                all_results.append(result)
            else:
                # Multiple tasks - run in parallel
                results = await asyncio.gather(*[
                    self._execute_single_task(task, conversation_loop)
                    for task in group
                ])
                all_results.extend(results)

        return all_results

    async def _execute_single_task(self, task: Dict, conversation_loop=None) -> Dict:
        """Execute single task with conversation loop"""
        if conversation_loop:
            return await conversation_loop.execute_task(task)
        else:
            # Fallback: direct coder execution without conversation loop
            coder_result = self.runner.run("coder", task)
            return {
                "task": task,
                "result": coder_result
            }
