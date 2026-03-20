from typing import Dict, Any
from .base_agent import BaseAgent, AgentState

class ExplorerAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "explorer", config)
        self.exploration_rate = config.get("exploration_rate", 0.8) if config else 0.8
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        return {
            "thought": "Exploring available information and resources...",
            "strategy": "search_and_discover",
            "exploration_mode": True,
        }


class SolverAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "solver", config)
        self.reasoning_depth = config.get("reasoning_depth", 3) if config else 3
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        return {
            "thought": f"Reasoning with depth {self.reasoning_depth}...",
            "strategy": "analyze_and_solve",
        }


class VerifierAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "verifier", config)
        self.strict_mode = config.get("strict_mode", True) if config else True
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        return {
            "thought": "Verifying correctness and completeness...",
            "strategy": "validate",
            "strict": self.strict_mode,
        }


class ResearcherAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "researcher", config)
        self.search_depth = config.get("search_depth", 3) if config else 3
        self.sources_visited = []
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        return {
            "thought": f"Researching topic with depth {self.search_depth}...",
            "strategy": "research",
            "tools_needed": ["web_search", "web_fetch"],
        }
    
    def act(self, action: Dict) -> Any:
        if action.get("type") == "llm":
            prompt = action.get("prompt", "")
            if "research" in prompt.lower() or "find" in prompt.lower():
                action["prompt"] = prompt + "\n\nProvide detailed information with sources."
        return super().act(action)


class CoderAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "coder", config)
        self.language = config.get("language", "python") if config else "python"
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        return {
            "thought": f"Planning and writing {self.language} code...",
            "strategy": "code",
            "language": self.language,
        }
    
    def act(self, action: Dict) -> Any:
        if action.get("type") == "llm":
            prompt = action.get("prompt", "")
            if "code" in prompt.lower() or "write" in prompt.lower() or "program" in prompt.lower():
                action["prompt"] = prompt + f"\n\nWrite clean, working {self.language} code."
        return super().act(action)


class PlannerAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "planner", config)
        self.plan_horizon = config.get("plan_horizon", 5) if config else 5
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        return {
            "thought": f"Creating a plan with horizon {self.plan_horizon}...",
            "strategy": "plan",
            "horizon": self.plan_horizon,
        }
    
    def act(self, action: Dict) -> Any:
        if action.get("type") == "llm":
            prompt = action.get("prompt", "")
            if "plan" in prompt.lower() or "how to" in prompt.lower() or "steps" in prompt.lower():
                action["prompt"] = prompt + "\n\nProvide a clear, step-by-step plan."
        return super().act(action)


class CriticAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "critic", config)
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        return {
            "thought": "Critically analyzing the approach...",
            "strategy": "critique",
        }


class MemoryAgent(BaseAgent):
    def __init__(self, agent_id: str, config: dict = None):
        super().__init__(agent_id, "memory", config)
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        return {
            "thought": "Searching memory for relevant information...",
            "strategy": "recall",
            "tools_needed": ["memory_search"],
        }


AGENT_TYPES = {
    "explorer": ExplorerAgent,
    "solver": SolverAgent,
    "verifier": VerifierAgent,
    "researcher": ResearcherAgent,
    "coder": CoderAgent,
    "planner": PlannerAgent,
    "critic": CriticAgent,
    "memory": MemoryAgent,
}


def create_agent(agent_type: str, agent_id: str, config: dict = None) -> BaseAgent:
    agent_class = AGENT_TYPES.get(agent_type, BaseAgent)
    return agent_class(agent_id, config)
