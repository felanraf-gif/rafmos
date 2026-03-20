import requests

class LLMAdvisor:
    def think(self, prompt):
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "qwen-agent",
            "prompt": prompt,
            "stream": False
        })
        return r.json()["response"]