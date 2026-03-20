import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import Orchestrator
from agents import BaseAgent
from tools import get_registry


class ExplorerAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "explorer", config)


class SolverAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "solver", config)


class VerifierAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "verifier", config)


def test():
    print("Initializing Multi-Agent System...")
    
    tools = get_registry()
    print(f"Tools loaded: {tools.list_tools()}")
    
    orchestrator = Orchestrator()
    
    explorer = ExplorerAgent("explorer_1")
    solver = SolverAgent("solver_1")
    verifier = VerifierAgent("verifier_1")
    
    orchestrator.register_agent("explorer_1", explorer)
    orchestrator.register_agent("solver_1", solver)
    orchestrator.register_agent("verifier_1", verifier)
    
    print("\nTesting tool: calculator")
    result = tools.execute("calculator", expression="2 + 2")
    print(f"Result: {result.to_dict()}")
    
    print("\nTesting with simple task:")
    result = orchestrator.run("What is 2 + 2? Show me the calculation.")
    
    print(f"\nStatus: {result.get('status')}")
    print(f"Result: {result.get('result')}")


if __name__ == "__main__":
    test()
