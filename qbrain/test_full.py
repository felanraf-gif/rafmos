import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import Orchestrator
from agents import BaseAgent


class ExplorerAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "explorer", config)


class SolverAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "solver", config)


class VerifierAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "verifier", config)


def test_orchestrator():
    print("Initializing Multi-Agent System...")
    
    from tools import get_registry
    tools = get_registry()
    print(f"Tools: {tools.list_tools()}")
    
    orchestrator = Orchestrator()
    
    explorer = ExplorerAgent("explorer_1")
    solver = SolverAgent("solver_1")
    verifier = VerifierAgent("verifier_1")
    
    orchestrator.register_agent("explorer_1", explorer)
    orchestrator.register_agent("solver_1", solver)
    orchestrator.register_agent("verifier_1", verifier)
    
    print("\nAgents registered!")
    
    print("\n" + "="*50)
    print("Running task: What is 2 + 2?")
    print("="*50)
    
    result = orchestrator.run("What is 2 + 2? Show me the calculation.")
    
    print(f"\nStatus: {result.get('status')}")
    print(f"Result: {result.get('result')}")
    
    status = orchestrator.get_status()
    print(f"\nAgent stats:")
    for agent_id, stats in status.get("agents", {}).items():
        print(f"  {agent_id}: {stats.get('success_rate', 0):.2%} success")


if __name__ == "__main__":
    test_orchestrator()
