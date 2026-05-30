from typing import List, Any
from ..core.agent_runner import AgentRunner
from ..core.protocol import AgentMessage


class SequentialOrchestrator:
    """Handles sequential (blocking) agent execution"""

    def __init__(self, runner: AgentRunner):
        self.runner = runner

    async def run_phase(
        self,
        agents: List[str],
        initial_context: Any
    ) -> AgentMessage:
        """Run agents sequentially, each waiting for previous"""

        context = initial_context
        last_result = None

        for agent_name in agents:
            print(f"[Sequential] Running {agent_name}...")
            result = self.runner.run(agent_name, context)

            # Next agent gets previous output as context
            context = {
                "previous_agent": agent_name,
                "previous_output": result.raw,
                "original_context": initial_context
            }

            last_result = result

        return last_result
