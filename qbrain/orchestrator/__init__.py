from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json

from communication import get_blackboard
from tools import get_registry
from llm import create_client, create_groq_client, get_system_prompt, format_prompt
from config import LLM_CONFIG, GROQ_CONFIG, TOOLS_CONFIG, ORCHESTRATOR_CONFIG


@dataclass
class Task:
    task_id: str
    description: str
    status: str = "pending"
    assigned_agent: Optional[str] = None
    result: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class Orchestrator:
    def __init__(self, config: Dict = None, llm_provider: str = "groq"):
        self.config = config or {}
        
        if llm_provider == "groq":
            self.llm = create_groq_client(GROQ_CONFIG)
            print(f"[Orchestrator] Using Groq: {GROQ_CONFIG['model']}")
        else:
            self.llm = create_client(LLM_CONFIG)
            print(f"[Orchestrator] Using LMStudio: {LLM_CONFIG['model']}")
        
        self.blackboard = get_blackboard()
        self.tools = get_registry()
        
        self.agents: Dict[str, Any] = {}
        self.tasks: Dict[str, Task] = {}
        
        self.max_iterations = ORCHESTRATOR_CONFIG["max_iterations"]
        self.timeout = ORCHESTRATOR_CONFIG["timeout_seconds"]
    
    def register_agent(self, agent_id: str, agent: Any) -> None:
        self.agents[agent_id] = agent
        agent.set_tools_registry(self.tools)
        agent.set_blackboard(self.blackboard)
        agent.set_llm_client(self.llm)
        
        self.blackboard.register_agent(agent_id, agent.agent_type)
    
    def create_task(self, description: str, dependencies: List[str] = None) -> Task:
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            task_id=task_id,
            description=description,
            dependencies=dependencies or [],
        )
        self.tasks[task_id] = task
        self.blackboard.post_task(task_id, {
            "description": description,
            "dependencies": dependencies,
        })
        return task
    
    def execute_task(self, task: Task) -> Dict:
        task.status = "running"
        self.blackboard.update_task(task.task_id, status="running")
        
        plan = self._plan_task(task)
        
        if not plan or not plan.get("success"):
            task.status = "failed"
            task.result = {"error": "Planning failed"}
            return {"success": False, "task": task}
        
        subtasks = plan.get("subtasks", [])
        results = []
        
        for subtask in subtasks:
            agent_type = subtask.get("agent_type", "solver")
            agent = self._get_available_agent(agent_type)
            
            if not agent:
                results.append({"error": f"No {agent_type} agent available"})
                continue
            
            task.assigned_agent = agent.agent_id
            self.blackboard.update_agent_status(agent.agent_id, "working")
            
            result = self._execute_subtask(agent, subtask)
            results.append(result)
            
            self.blackboard.update_agent_status(agent.agent_id, "idle")
            
            if subtask.get("requires_verification"):
                verified = self._verify_result(result)
                results[-1]["verified"] = verified
        
        final_result = self._synthesize_results(results, task)
        
        if self._is_success(final_result):
            task.status = "completed"
            task.result = final_result
        else:
            task.status = "failed"
            task.result = final_result
        
        task.completed_at = datetime.now()
        self.blackboard.update_task(task.task_id, status=task.status, result=task.result)
        
        return {"success": task.status == "completed", "task": task}
    
    def _plan_task(self, task: Task) -> Dict:
        prompt = f"""Task: {task.description}

Break this down into subtasks. For each subtask specify:
- description: what to do
- agent_type: EXPLORER, SOLVER, or VERIFIER
- requires_verification: true/false

Respond with JSON: {{"subtasks": [{{"description": "...", "agent_type": "...", "requires_verification": false}}]}}"""

        result = self.llm.generate(prompt, system_prompt=get_system_prompt("orchestrator"))
        
        if result.get("success"):
            try:
                content = result["content"]
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                plan = json.loads(content.strip())
                return {"success": True, **plan}
            except json.JSONDecodeError:
                return {"success": False, "error": "Parse error"}
        
        return {"success": False, "error": result.get("error", "LLM failed")}
    
    def _get_available_agent(self, agent_type: str) -> Optional[Any]:
        for agent in self.agents.values():
            if agent.agent_type == agent_type:
                agent_info = self.blackboard.get_agent(agent.agent_id)
                if agent_info and agent_info.get("status") == "idle":
                    return agent
        return list(self.agents.values())[0] if self.agents else None
    
    def _execute_subtask(self, agent: Any, subtask: Dict) -> Dict:
        description = subtask.get("description", "")
        
        thought = agent.think(description)
        
        action = {
            "type": "llm",
            "prompt": f"""Task: {description}

Think step by step and execute the task. Use tools if needed.
Report your final answer clearly.""",
        }
        
        result = agent.act(action)
        
        agent.learn({"type": "success" if result else "failure"})
        
        return {
            "agent": agent.agent_id,
            "description": description,
            "result": result,
        }
    
    def _verify_result(self, result: Dict) -> Dict:
        verifier = self._get_available_agent("verifier")
        if not verifier:
            return {"verified": True}
        
        prompt = f"""Verify this result:
{json.dumps(result, indent=2)}

Is the result correct? Respond with JSON:
{{"correct": true/false, "issues": ["issue1", "issue2"]}}"""

        llm_result = self.llm.generate(prompt, system_prompt=get_system_prompt("verifier"))
        
        if llm_result.get("success"):
            try:
                content = llm_result["content"]
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                return json.loads(content.strip())
            except:
                pass
        
        return {"verified": False}
    
    def _synthesize_results(self, results: List[Dict], task: Task) -> Dict:
        prompt = f"""Original task: {task.description}

Results from subtasks:
{json.dumps(results, indent=2)}

Synthesize these results into a final answer. Respond with JSON:
{{"summary": "...", "final_answer": "...", "confidence": 0.0-1.0}}"""

        result = self.llm.generate(prompt)
        
        if result.get("success"):
            try:
                content = result["content"]
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
            except:
                pass
        
        return {"summary": "Results collected", "final_answer": str(results)}
    
    def _is_success(self, result: Dict) -> bool:
        confidence = result.get("confidence", 0.5)
        return confidence >= 0.7
    
    def run(self, task_description: str) -> Dict:
        task = self.create_task(task_description)
        
        for i in range(self.max_iterations):
            result = self.execute_task(task)
            
            if result.get("success"):
                break
        
        return {
            "task_id": task.task_id,
            "status": task.status,
            "result": task.result,
        }
    
    def get_status(self) -> Dict:
        return {
            "agents": {aid: a.get_stats() for aid, a in self.agents.items()},
            "tasks": {tid: {"status": t.status, "description": t.description} 
                     for tid, t in self.tasks.items()},
            "blackboard": self.blackboard.snapshot(),
        }
