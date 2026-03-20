import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import get_registry


def test_tools():
    print("Testing Tools...")
    
    tools = get_registry()
    print(f"Available tools: {tools.list_tools()}")
    
    print("\n1. Testing calculator:")
    result = tools.execute("calculator", expression="2 + 2")
    print(f"   Result: {result.to_dict()}")
    
    print("\n2. Testing python_exec:")
    result = tools.execute("python_exec", code="print(2+2)")
    print(f"   Result: {result.to_dict()}")
    
    print("\n3. Testing file_read:")
    result = tools.execute("file_read", path="config.py")
    print(f"   Result: success={result.success}, length={result.data.get('length') if result.data else 0}")
    
    print("\n4. Testing file_write:")
    result = tools.execute("file_write", path="/tmp/test_agent.txt", content="Hello from agent!")
    print(f"   Result: {result.to_dict()}")
    
    print("\n5. Testing memory_store:")
    result = tools.execute("memory_store", key="test_key", value="test_value")
    print(f"   Result: {result.to_dict()}")
    
    print("\n6. Testing memory_search:")
    result = tools.execute("memory_search", query="test")
    print(f"   Result: {result.to_dict()}")
    
    print("\n" + "="*50)
    print("Tool stats:")
    print(tools.get_stats())


if __name__ == "__main__":
    test_tools()
