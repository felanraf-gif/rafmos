import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import get_registry
from llm import create_client
from agents import create_agent
from learning.engine import get_learning_engine
from config import LLM_CONFIG


class SmartOrchestrator:
    def __init__(self):
        self.llm = create_client(LLM_CONFIG)
        self.tools = get_registry()
        self.learning = get_learning_engine()
        self.agents = {}
        
        self._init_agents()
    
    def _init_agents(self):
        agent_types = ["solver", "researcher", "coder", "planner"]
        for at in agent_types:
            agent = create_agent(at, f"{at}_1")
            agent.set_llm_client(self.llm)
            agent.set_tools_registry(self.tools)
            self.agents[at] = agent
    
    def execute(self, task: str) -> dict:
        print(f"\n{'='*50}")
        print(f"Task: {task}")
        print('='*50)
        
        plan = self._create_plan(task)
        print(f"\nPlan: {plan.get('steps', [])}")
        
        results = []
        for step in plan.get("steps", []):
            step_type = step.get("type")
            
            if step_type == "tool":
                tool_name = step.get("tool")
                params = step.get("params", {})
                print(f"\n[Tool] {tool_name}: {params}")
                
                result = self.tools.execute(tool_name, **params)
                print(f"Result: {result.data}")
                results.append({"step": step, "result": result.to_dict()})
                
                self.learning.record_experience(
                    task_type=step_type,
                    action=tool_name,
                    result=result.data,
                    reward=1.0 if result.success else 0.0
                )
            
            elif step_type == "llm":
                prompt = step.get("prompt", "")
                print(f"\n[LLM] {prompt[:100]}...")
                
                result = self.llm.generate(prompt)
                content = result.get("content", "")
                print(f"Response: {content[:200]}...")
                results.append({"step": step, "result": content})
                
                self.learning.record_experience(
                    task_type="llm",
                    action="generate",
                    result=content,
                    reward=1.0 if result.get("success") else 0.0
                )
        
        final_answer = self._synthesize(task, results)
        
        return {
            "task": task,
            "plan": plan,
            "results": results,
            "answer": final_answer,
        }
    
    def _create_plan(self, task: str) -> dict:
        tool_list = self.tools.list_tools()
        
        prompt = f"""Task: {task}

You have these tools available:
{', '.join(tool_list)}

Create a step-by-step plan to complete this task.
Respond in JSON format:
{{
    "steps": [
        {{"type": "tool", "tool": "tool_name", "params": {{"param": "value"}}}},
        {{"type": "llm", "prompt": "what to ask"}}
    ]
}}

Choose the best tools for each step. Use "llm" for reasoning, "tool" for actions.
"""
        
        result = self.llm.generate(prompt)
        
        if result.get("success"):
            try:
                content = result["content"]
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                plan_data = eval(content.strip())
                
                steps = []
                for s in plan_data.get("steps", []):
                    step_type = s.get("type", "llm")
                    if step_type == "tool":
                        steps.append({
                            "type": "tool",
                            "tool": s.get("tool", s.get("action")),
                            "params": s.get("params", s.get("arguments", {}))
                        })
                    else:
                        steps.append({"type": "llm", "prompt": s.get("prompt", s.get("content", ""))})
                
                return {"steps": steps}
            except Exception as e:
                print(f"Parse error: {e}")
        
        return {"steps": [{"type": "llm", "prompt": task}]}
    
    def _synthesize(self, task: str, results: list) -> str:
        prompt = f"""Original task: {task}

Results from steps:
{self._format_results(results)}

Provide a final answer that addresses the original task."""
        
        result = self.llm.generate(prompt)
        return result.get("content", "No result")
    
    def _format_results(self, results: list) -> str:
        formatted = []
        for r in results:
            step = r.get("step", {})
            result = r.get("result", {})
            
            if isinstance(result, dict):
                data = result.get("data", str(result))
            else:
                data = str(result)[:200]
            
            formatted.append(f"- {step.get('type')}: {data}")
        
        return "\n".join(formatted)
    
    def chat(self):
        print("\n" + "="*50)
        print("SMART MULTI-AGENT SYSTEM")
        print("Tools: " + ", ".join(self.tools.list_tools()))
        print("="*50)
        
        while True:
            try:
                task = input("\n>>> ").strip()
                if not task:
                    continue
                if task.lower() in ["quit", "exit", "q"]:
                    break
                
                result = self.execute(task)
                print(f"\n{'='*50}")
                print("ANSWER:")
                print(result["answer"])
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nBye!")


def main():
    orchestrator = SmartOrchestrator()
    orchestrator.chat()


if __name__ == "__main__":
    main()
