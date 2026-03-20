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


def main():
    print("Initializing Multi-Agent System...")
    
    from tools import get_registry
    tools = get_registry()
    print(f"Tools loaded: {tools.list_tools()}")
    
    orchestrator = Orchestrator()
    
    explorer = ExplorerAgent("explorer_1")
    solver = SolverAgent("solver_1")
    verifier = VerifierAgent("verifier_1")
    
    orchestrator.register_agent("explorer_1", explorer)
    orchestrator.register_agent("solver_1", solver)
    orchestrator.register_agent("verifier_1", verifier)
    
    print("\nAgents registered:")
    print(f"  - Explorer: {explorer.agent_id}")
    print(f"  - Solver: {solver.agent_id}")
    print(f"  - Verifier: {verifier.agent_id}")
    
    print("\n" + "="*50)
    
    while True:
        try:
            task = input("\nEnter task (or 'quit' to exit): ").strip()
            
            if task.lower() in ["quit", "exit", "q"]:
                print("Shutting down...")
                break
            
            if not task:
                continue
            
            print(f"\nExecuting: {task}")
            result = orchestrator.run(task)
            
            print("\n" + "="*50)
            print("RESULT:")
            print(f"  Status: {result.get('status')}")
            print(f"  Result: {result.get('result')}")
            
            status = orchestrator.get_status()
            print(f"\nAgent stats:")
            for agent_id, stats in status.get("agents", {}).items():
                print(f"  {agent_id}: {stats.get('success_rate', 0):.2%} success")
        
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
