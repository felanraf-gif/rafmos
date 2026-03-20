import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import get_registry
from llm import create_client, get_system_prompt
from communication import get_blackboard
from agents import create_agent, AGENT_TYPES
from learning.engine import get_learning_engine
from config import LLM_CONFIG


class AdvancedOrchestrator:
    def __init__(self):
        self.llm = create_client(LLM_CONFIG)
        self.blackboard = get_blackboard()
        self.tools = get_registry()
        self.learning = get_learning_engine()
        
        self.agents = {}
        self.task_history = []
    
    def register_agent(self, agent_type: str, agent_id: str = None):
        if agent_id is None:
            agent_id = f"{agent_type}_{len(self.agents) + 1}"
        
        agent = create_agent(agent_type, agent_id)
        agent.set_tools_registry(self.tools)
        agent.set_blackboard(self.blackboard)
        agent.set_llm_client(self.llm)
        
        self.agents[agent_id] = agent
        self.blackboard.register_agent(agent_id, agent_type)
        
        return agent
    
    def suggest_agent_for_task(self, task: str) -> str:
        task_lower = task.lower()
        
        if any(w in task_lower for w in ["search", "find", "research", "information", "what is", "who is"]):
            return "researcher"
        elif any(w in task_lower for w in ["code", "write", "program", "function", "implement"]):
            return "coder"
        elif any(w in task_lower for w in ["plan", "how to", "steps", "strategy"]):
            return "planner"
        elif any(w in task_lower for w in ["verify", "check", "validate", "correct", "ensure"]):
            return "verifier"
        elif any(w in task_lower for w in ["remember", "recall", "memory", "stored"]):
            return "memory"
        elif any(w in task_lower for w in ["criticize", "analyze", "review", "evaluate"]):
            return "critic"
        elif any(w in task_lower for w in ["explore", "discover", "find"]):
            return "explorer"
        else:
            return "solver"
    
    def execute_task(self, task: str) -> dict:
        agent_type = self.suggest_agent_for_task(task)
        print(f"[Orchestrator] Suggested agent: {agent_type}")
        
        if agent_type not in [a.agent_type for a in self.agents.values()]:
            self.register_agent(agent_type)
        
        for agent in self.agents.values():
            if agent.agent_type == agent_type:
                break
        else:
            agent = list(self.agents.values())[0]
        
        thought = agent.think(task)
        
        prompt = f"""Task: {task}

Think step by step and provide a complete answer.
{thought.get('thought', '')}

"""
        
        if agent_type == "researcher":
            prompt += "Search for relevant information and provide sources."
        elif agent_type == "coder":
            prompt += "Write clean, working code if needed."
        elif agent_type == "planner":
            prompt += "Create a clear step-by-step plan."
        
        result = agent._call_llm(prompt, {})
        
        success = result.get("success", False)
        reward = 1.0 if success else 0.0
        
        self.learning.record_experience(
            task_type=agent_type,
            action="llm_call",
            result=result.get("content", ""),
            reward=reward
        )
        
        self.learning.record_agent_performance(agent.agent_id, reward)
        
        agent.learn({"type": "success" if success else "failure"})
        
        self.task_history.append({
            "task": task,
            "agent": agent.agent_id,
            "agent_type": agent_type,
            "success": success,
        })
        
        if self.learning.should_evolve():
            print("[Orchestrator] Running evolution...")
            evolutions = self.learning.evolve(self.agents)
            print(f"[Orchestrator] Evolutions: {evolutions}")
        
        return {
            "task": task,
            "agent": agent.agent_id,
            "agent_type": agent_type,
            "result": result.get("content", result.get("error", "Unknown error")),
            "success": success,
        }
    
    def get_status(self) -> dict:
        insights = self.learning.get_insights()
        
        return {
            "agents": {
                aid: {
                    "type": a.agent_type,
                    "success_rate": self.learning.get_agent_success_rate(aid),
                    "state": a.state.value,
                }
                for aid, a in self.agents.items()
            },
            "learning": insights,
            "total_tasks": len(self.task_history),
        }


def main():
    print("=" * 60)
    print("  ADVANCED MULTI-AGENT SYSTEM")
    print("  With Learning, Evolution & Multiple Agent Types")
    print("=" * 60)
    
    tools = get_registry()
    print(f"\nTools: {', '.join(tools.list_tools())}")
    
    orchestrator = AdvancedOrchestrator()
    
    agent_configs = [
        ("solver", "solver_1"),
        ("researcher", "researcher_1"),
        ("coder", "coder_1"),
        ("planner", "planner_1"),
    ]
    
    for agent_type, agent_id in agent_configs:
        orchestrator.register_agent(agent_type, agent_id)
    
    print(f"\nAgents: {', '.join(orchestrator.agents.keys())}")
    
    print("\n" + "=" * 60)
    
    test_tasks = [
        "What is Python?",
        "Write a function to calculate fibonacci",
        "How to make coffee?",
        "Create a plan to learn programming",
    ]
    
    for task in test_tasks:
        print(f"\n>>> Task: {task}")
        result = orchestrator.execute_task(task)
        print(f"    Agent: {result['agent_type']}")
        print(f"    Result: {result['result'][:200]}...")
    
    print("\n" + "=" * 60)
    print("STATUS:")
    status = orchestrator.get_status()
    
    print("\nAgent Performance:")
    for aid, info in status["agents"].items():
        print(f"  {aid} ({info['type']}): {info['success_rate']:.0%} success")
    
    print("\nLearning Insights:")
    learning = status["learning"]
    print(f"  Total experiences: {learning['total_experiences']}")
    print(f"  Tool success rates: {learning['tool_success_rates']}")
    
    print("\n" + "=" * 60)
    print("DONE!")


if __name__ == "__main__":
    main()
