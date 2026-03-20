from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import os


@dataclass
class Experience:
    task_type: str
    action: str
    result: Any
    reward: float
    timestamp: datetime = field(default_factory=datetime.now)


class ExperienceBuffer:
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer: List[Experience] = []
    
    def add(self, experience: Experience):
        self.buffer.append(experience)
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)
    
    def get_recent(self, n: int = 100) -> List[Experience]:
        return self.buffer[-n:]
    
    def get_by_task(self, task_type: str) -> List[Experience]:
        return [e for e in self.buffer if e.task_type == task_type]
    
    def clear(self):
        self.buffer.clear()


class LearningEngine:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        self.experience_buffer = ExperienceBuffer(
            max_size=self.config.get("max_experiences", 10000)
        )
        
        self.strategies: Dict[str, float] = {}
        self.tool_preferences: Dict[str, Dict[str, float]] = {}
        self.agent_performance: Dict[str, List[float]] = {}
        
        self.evolution_interval = self.config.get("evolution_interval", 100)
        self.task_count = 0
        
        self.load()
    
    def record_experience(self, task_type: str, action: str, result: Any, reward: float):
        exp = Experience(task_type, action, result, reward)
        self.experience_buffer.add(exp)
        
        if action not in self.tool_preferences:
            self.tool_preferences[action] = {"success": 0, "total": 0}
        
        self.tool_preferences[action]["total"] += 1
        if reward > 0.5:
            self.tool_preferences[action]["success"] += 1
    
    def record_agent_performance(self, agent_id: str, score: float):
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = []
        
        self.agent_performance[agent_id].append(score)
        
        if len(self.agent_performance[agent_id]) > 100:
            self.agent_performance[agent_id].pop(0)
    
    def get_best_tool_for_task(self, task_type: str) -> Optional[str]:
        task_experiences = self.experience_buffer.get_by_task(task_type)
        
        if not task_experiences:
            return None
        
        tool_scores: Dict[str, float] = {}
        for exp in task_experiences:
            if exp.action not in tool_scores:
                tool_scores[exp.action] = 0
            tool_scores[exp.action] += exp.reward
        
        if not tool_scores:
            return None
        
        return max(tool_scores, key=tool_scores.get)
    
    def get_tool_success_rate(self, tool_name: str) -> float:
        prefs = self.tool_preferences.get(tool_name)
        if not prefs or prefs["total"] == 0:
            return 0.5
        return prefs["success"] / prefs["total"]
    
    def get_agent_success_rate(self, agent_id: str) -> float:
        scores = self.agent_performance.get(agent_id, [])
        if not scores:
            return 0.5
        return sum(scores) / len(scores)
    
    def should_evolve(self) -> bool:
        self.task_count += 1
        return self.task_count % self.evolution_interval == 0
    
    def evolve(self, agents: Dict[str, Any]) -> Dict[str, Any]:
        if not agents:
            return {"message": "No agents to evolve"}
        
        evolutions = {}
        
        for agent_id, agent in agents.items():
            current_rate = self.get_agent_success_rate(agent_id)
            
            if current_rate < 0.3:
                evolutions[agent_id] = {
                    "action": "replace",
                    "reason": f"Low success rate: {current_rate:.2%}",
                }
            elif current_rate < 0.5:
                evolutions[agent_id] = {
                    "action": "retrain",
                    "reason": f"Below average: {current_rate:.2%}",
                    "suggestion": "Increase exploration rate",
                }
            elif current_rate > 0.8:
                evolutions[agent_id] = {
                    "action": "promote",
                    "reason": f"High success rate: {current_rate:.2%}",
                }
        
        self.task_count = 0
        
        return evolutions
    
    def get_insights(self) -> Dict:
        tool_rates = {
            tool: self.get_tool_success_rate(tool)
            for tool in self.tool_preferences.keys()
        }
        
        agent_rates = {
            agent: self.get_agent_success_rate(agent)
            for agent in self.agent_performance.keys()
        }
        
        return {
            "tool_success_rates": tool_rates,
            "agent_success_rates": agent_rates,
            "total_experiences": len(self.experience_buffer.buffer),
            "task_count": self.task_count,
        }
    
    def save(self, path: str = None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "learning_state.json")
        
        data = {
            "tool_preferences": self.tool_preferences,
            "agent_performance": {
                k: v for k, v in self.agent_performance.items()
            },
            "task_count": self.task_count,
        }
        
        with open(path, "w") as f:
            json.dump(data, f)
    
    def load(self, path: str = None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "learning_state.json")
        
        if not os.path.exists(path):
            return
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            self.tool_preferences = data.get("tool_preferences", {})
            self.agent_performance = data.get("agent_performance", {})
            self.task_count = data.get("task_count", 0)
        except:
            pass


_global_learning_engine = None

def get_learning_engine(config: Dict = None) -> LearningEngine:
    global _global_learning_engine
    if _global_learning_engine is None:
        _global_learning_engine = LearningEngine(config)
    return _global_learning_engine
