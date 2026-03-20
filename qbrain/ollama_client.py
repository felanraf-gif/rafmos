import subprocess
import json

MODEL = "qwen-agent"   # ten który stworzyłeś

def ask_llm(state, failures):
    prompt = f"""
You are an autonomous AI agent improving your own system.

PROJECT STATE:
{state}

FAILED ATTEMPTS:
{failures if failures else "None"}

Your task:
Propose ONE concrete action to improve the system.
Return only the action description.
"""

    cmd = ["ollama", "run", MODEL, prompt]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()
