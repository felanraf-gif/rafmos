from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    FINISHED = "finished"
    ERROR = "error"


@dataclass
class Belief:
    key: str
    value: Any
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"


@dataclass
class Goal:
    description: str
    priority: int = 1
    deadline: Optional[datetime] = None
    status: str = "pending"
    progress: float = 0.0


class BaseAgent:
    def __init__(self, agent_id: str, agent_type: str, config: Dict = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config or {}
        
        self.state = AgentState.IDLE
        self.beliefs: Dict[str, Belief] = {}
        self.goals: List[Goal] = []
        self.history: List[Dict] = []
        
        self.tools_registry = None
        self.blackboard = None
        self.llm_client = None
        
        self.success_count = 0
        self.failure_count = 0
    
    def set_tools_registry(self, registry):
        self.tools_registry = registry
    
    def set_blackboard(self, blackboard):
        self.blackboard = blackboard
    
    def set_llm_client(self, client):
        self.llm_client = client
    
    def perceive(self, observation: Any) -> None:
        if isinstance(observation, dict):
            for key, value in observation.items():
                self.beliefs[key] = Belief(
                    key=key,
                    value=value,
                    confidence=0.8,
                    source=self.agent_id,
                )
    
    def think(self, task: Any) -> Dict:
        self.state = AgentState.THINKING
        result = {
            "thought": "Thinking...",
            "plan": [],
            "confidence": 0.5,
        }
        self._log("think", task)
        return result
    
    def act(self, action: Dict) -> Any:
        self.state = AgentState.ACTING
        
        if not action:
            return None
        
        action_type = action.get("type")
        
        if action_type == "tool":
            return self._execute_tool(action.get("tool"), action.get("params", {}))
        elif action_type == "llm":
            return self._call_llm(action.get("prompt"), action.get("params", {}))
        elif action_type == "communicate":
            return self._communicate(action.get("receiver"), action.get("message"))
        elif action_type == "blackboard":
            return self._blackboard_op(action.get("operation"), action.get("key"), action.get("value"))
        
        return None
    
    def _execute_tool(self, tool_name: str, params: Dict) -> Any:
        if self.tools_registry:
            result = self.tools_registry.execute(tool_name, **params)
            self._log("tool", {"tool": tool_name, "success": result.success})
            return result.to_dict() if hasattr(result, "to_dict") else result
        return {"error": "No tools registry"}
    
    def _call_llm(self, prompt: str, params: Dict) -> Any:
        if self.llm_client:
            result = self.llm_client.generate(prompt, **params)
            self._log("llm", {"prompt": prompt[:50], "success": True})
            return result
        return {"error": "No LLM client"}
    
    def _communicate(self, receiver: str, message: Any) -> Any:
        if self.blackboard:
            self.blackboard.post(
                f"msg_{receiver}",
                message,
                agent=self.agent_id,
            )
        return {"sent": True, "to": receiver}
    
    def _blackboard_op(self, operation: str, key: str, value: Any = None) -> Any:
        if not self.blackboard:
            return {"error": "No blackboard"}
        
        if operation == "post":
            self.blackboard.post(key, value, self.agent_id)
            return {"posted": key}
        elif operation == "get":
            return {"key": key, "value": self.blackboard.get(key)}
        elif operation == "search":
            return {"results": self.blackboard.search(value)}
        
        return {"error": f"Unknown operation: {operation}"}
    
    def learn(self, feedback: Dict) -> None:
        feedback_type = feedback.get("type")
        
        if feedback_type == "success":
            self.success_count += 1
        elif feedback_type == "failure":
            self.failure_count += 1
        
        self._log("learn", feedback)
    
    def add_goal(self, goal: Goal) -> None:
        self.goals.append(goal)
    
    def remove_goal(self, description: str) -> None:
        self.goals = [g for g in self.goals if g.description != description]
    
    def get_belief(self, key: str) -> Optional[Any]:
        belief = self.beliefs.get(key)
        return belief.value if belief else None
    
    def set_belief(self, key: str, value: Any, confidence: float = 1.0) -> None:
        self.beliefs[key] = Belief(
            key=key,
            value=value,
            confidence=confidence,
            source=self.agent_id,
        )
    
    def get_stats(self) -> Dict:
        total = self.success_count + self.failure_count
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state.value,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_count / max(1, total),
            "beliefs_count": len(self.beliefs),
            "goals_count": len(self.goals),
        }
    
    def _log(self, action: str, data: Any) -> None:
        self.history.append({
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "state": self.state.value,
        })
        if len(self.history) > 500:
            self.history = self.history[-250:]
