import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm import create_client


def test_llm():
    print("Testing LLM...")
    
    from config import LLM_CONFIG
    client = create_client(LLM_CONFIG)
    
    print(f"Model: {client.model}")
    print(f"URL: {client.base_url}")
    
    print("\nSending request...")
    result = client.generate("What is 2 + 2? Answer briefly.")
    
    print(f"\nSuccess: {result.get('success')}")
    if result.get('success'):
        print(f"Response: {result.get('content')}")
    else:
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    test_llm()
