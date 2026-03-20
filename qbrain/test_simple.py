import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import get_registry
from llm import create_client
from agents import create_agent
from learning.engine import get_learning_engine
from config import LLM_CONFIG


def test():
    print("Testing components...")
    
    print("\n1. Tools:")
    tools = get_registry()
    print(f"   {tools.list_tools()}")
    
    print("\n2. LLM:")
    llm = create_client(LLM_CONFIG)
    r = llm.generate("Hi")
    print(f"   {r.get('success')}")
    
    print("\n3. Agents:")
    agent = create_agent("solver", "solver_1")
    print(f"   {agent.agent_id}, {agent.agent_type}")
    
    print("\n4. Learning:")
    learning = get_learning_engine()
    print(f"   {learning}")
    
    print("\n5. Full execution:")
    from agents import BaseAgent
    agent = create_agent("solver", "test")
    agent.set_llm_client(llm)
    agent.set_tools_registry(tools)
    
    print("   Calling LLM...")
    result = agent._call_llm("What is 2+2?", {})
    print(f"   Success: {result.get('success')}")
    print(f"   Content: {result.get('content')}")
    
    print("\nDONE!")


if __name__ == "__main__":
    test()
