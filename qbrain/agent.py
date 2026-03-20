import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import get_registry
from llm import create_client, create_groq_client
from learning.engine import get_learning_engine
from config import LLM_CONFIG, GROQ_CONFIG


class SimpleAgent:
    def __init__(self, provider: str = "groq"):
        if provider == "groq":
            self.llm = create_groq_client(GROQ_CONFIG)
            print(f"[Groq] Using {GROQ_CONFIG['model']}")
        else:
            self.llm = create_client(LLM_CONFIG)
            print(f"[LMStudio] Using {LLM_CONFIG['model']}")
        
        self.tools = get_registry()
        self.learning = get_learning_engine()
    
    def run(self, task: str) -> str:
        print(f"\n>>> Task: {task}")
        
        # Check if needs search FIRST (before code/calc to catch "what is")
        if any(w in task.lower() for w in ["search", "find", "who is", "how to", "latest", "news"]):
            print("   [Search] Searching...")
            result = self.tools.execute("web_search", query=task, num_results=3)
            if result.success and result.data:
                print(f"   [Search] Found {len(result.data)} results")
                for r in result.data[:2]:
                    print(f"      - {r.get('title', 'N/A')}")
                # Use search results
                answer = f"Search results for '{task}': " + "; ".join([r.get('title', '') for r in result.data[:3]])
                return answer
        
        # Check if needs calculation
        if any(w in task.lower() for w in ["calculate", "compute", "+", "-", "*", "/", "="]):
            # Try calculator
            expr = self._extract_expression(task)
            if expr:
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
    
    def _extract_expression(self, text: str) -> str:
        import re
        # Look for mathematical expression
        match = re.search(r'[\d\+\-\*\/\(\)\s]+', text)
        if match:
            expr = match.group().strip()
            # Verify it's mostly numbers and operators
            if any(op in expr for op in ['+', '-', '*', '/']):
                return expr
        return None


def main():
    print("=" * 50)
    print("  SIMPLE AGENT - Ready to help!")
    print("=" * 50)
    
    agent = SimpleAgent()
    
    print("\nTools: " + ", ".join(agent.tools.list_tools()))
    
    while True:
        try:
            task = input("\n>>> ").strip()
            if not task:
                continue
            if task.lower() in ["quit", "exit", "q"]:
                break
            
            answer = agent.run(task)
            print(f"\nAnswer: {answer}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nBye!")


if __name__ == "__main__":
    main()
