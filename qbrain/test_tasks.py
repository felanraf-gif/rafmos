import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import get_registry
from llm import create_client
from learning.engine import get_learning_engine
from config import LLM_CONFIG


class SimpleAgent:
    def __init__(self):
        self.llm = create_client(LLM_CONFIG)
        self.tools = get_registry()
        self.learning = get_learning_engine()
    
    def run(self, task: str) -> str:
        print(f"\n>>> Task: {task}")
        
        # Check if needs search FIRST
        if any(w in task.lower() for w in ["search", "find", "who is", "how to", "latest", "news", "what is"]):
            print("   [Search] Searching...")
            result = self.tools.execute("web_search", query=task, num_results=3)
            if result.success and result.data:
                print(f"   [Search] Found {len(result.data)} results")
                for r in result.data[:2]:
                    print(f"      - {r.get('title', 'N/A')}")
                answer = "Search results: " + "; ".join([r.get('title', '') for r in result.data[:3]])
                return answer
        
        # Check if needs calculation
        if any(w in task.lower() for w in ["calculate", "compute", "+", "-", "*", "/", "="]):
            import re
            match = re.search(r'[\d\+\-\*\/\(\)\s]+', task)
            if match:
                expr = match.group().strip()
                if any(op in expr for op in ['+', '-', '*', '/']):
                    result = self.tools.execute("calculator", expression=expr)
                    if result.success:
                        print(f"   [Calc] {expr} = {result.data.get('result')}")
                        return f"Result: {result.data.get('result')}"
        
        # Check if needs code
        if any(w in task.lower() for w in ["code", "write", "program", "function"]):
            print("   [Coder] Generating code...")
        
        # Default: use LLM
        print("   [LLM] Reasoning...")
        result = self.llm.generate(task)
        
        if result.get("success"):
            answer = result.get("content", "")
            print(f"   [Result] {answer[:200]}")
            
            self.learning.record_experience(
                task_type="general",
                action="llm",
                result=answer,
                reward=1.0
            )
            
            return answer
        
        return f"Error: {result.get('error')}"


# Test tasks
if __name__ == "__main__":
    agent = SimpleAgent()
    
    tasks = [
        "What is 2 + 2?",
        "Calculate 10 * 5",
        "What is Python programming?",
        "How does neural network work?",
    ]
    
    for task in tasks:
        try:
            answer = agent.run(task)
            print(f"\nAnswer: {answer[:200]}")
            print("-" * 40)
        except Exception as e:
            print(f"Error: {e}")
