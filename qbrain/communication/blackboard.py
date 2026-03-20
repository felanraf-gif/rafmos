from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import threading


class Blackboard:
    def __init__(self):
        self._lock = threading.Lock()
        self._knowledge: Dict[str, Any] = {}
        self._partial_solutions: Dict[str, Any] = {}
        self._agents: Dict[str, Dict] = {}
        self._tasks: Dict[str, Dict] = {}
        self._history: List[Dict] = []
    
    def post(self, key: str, value: Any, agent: str = None) -> None:
        with self._lock:
            self._knowledge[key] = {
                "value": value,
                "author": agent,
                "timestamp": datetime.now().isoformat(),
            }
            self._log("POST", key, agent)
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._knowledge.get(key)
            return entry["value"] if entry else None
    
    def get_with_meta(self, key: str) -> Optional[Dict]:
        with self._lock:
            return self._knowledge.get(key)
    
    def search(self, pattern: str) -> List[Dict]:
        with self._lock:
            pattern_lower = pattern.lower()
            results = []
            for key, entry in self._knowledge.items():
                if pattern_lower in key.lower():
                    results.append({"key": key, **entry})
                elif pattern_lower in str(entry.get("value", "")).lower():
                    results.append({"key": key, **entry})
            return results
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._knowledge:
                del self._knowledge[key]
                self._log("DELETE", key)
                return True
            return False
    
    def post_partial(self, task_id: str, solution: Any, agent: str) -> None:
        with self._lock:
            if task_id not in self._partial_solutions:
                self._partial_solutions[task_id] = []
            self._partial_solutions[task_id].append({
                "solution": solution,
                "agent": agent,
                "timestamp": datetime.now().isoformat(),
            })
    
    def get_partials(self, task_id: str) -> List[Dict]:
        with self._lock:
            return self._partial_solutions.get(task_id, [])
    
    def register_agent(self, agent_id: str, agent_type: str, metadata: Dict = None) -> None:
        with self._lock:
            self._agents[agent_id] = {
                "type": agent_type,
                "status": "idle",
                "metadata": metadata or {},
                "registered": datetime.now().isoformat(),
            }
    
    def update_agent_status(self, agent_id: str, status: str) -> None:
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id]["status"] = status
                self._agents[agent_id]["last_update"] = datetime.now().isoformat()
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        with self._lock:
            return self._agents.get(agent_id)
    
    def get_agents(self, agent_type: str = None, status: str = None) -> List[Dict]:
        with self._lock:
            agents = list(self._agents.values())
            if agent_type:
                agents = [a for a in agents if a.get("type") == agent_type]
            if status:
                agents = [a for a in agents if a.get("status") == status]
            return agents
    
    def post_task(self, task_id: str, task: Dict) -> None:
        with self._lock:
            task["task_id"] = task_id
            task["created"] = datetime.now().isoformat()
            task["status"] = "pending"
            self._tasks[task_id] = task
            self._log("TASK_POST", task_id)
    
    def update_task(self, task_id: str, status: str = None, result: Any = None) -> None:
        with self._lock:
            if task_id in self._tasks:
                if status:
                    self._tasks[task_id]["status"] = status
                if result is not None:
                    self._tasks[task_id]["result"] = result
                self._tasks[task_id]["updated"] = datetime.now().isoformat()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_tasks(self, status: str = None) -> List[Dict]:
        with self._lock:
            tasks = list(self._tasks.values())
            if status:
                tasks = [t for t in tasks if t.get("status") == status]
            return tasks
    
    def _log(self, action: str, key: str, agent: str = None) -> None:
        self._history.append({
            "action": action,
            "key": key,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
        })
        if len(self._history) > 1000:
            self._history = self._history[-500:]
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        with self._lock:
            return self._history[-limit:]
    
    def snapshot(self) -> Dict:
        with self._lock:
            return {
                "knowledge": dict(self._knowledge),
                "agents": dict(self._agents),
                "tasks": dict(self._tasks),
                "history_size": len(self._history),
            }
    
    def clear(self) -> None:
        with self._lock:
            self._knowledge.clear()
            self._partial_solutions.clear()
            self._agents.clear()
            self._tasks.clear()
            self._history.clear()


_global_blackboard = None

def get_blackboard() -> Blackboard:
    global _global_blackboard
    if _global_blackboard is None:
        _global_blackboard = Blackboard()
    return _global_blackboard
