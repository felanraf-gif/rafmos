import requests
from typing import Dict, List, Any, Optional
import json


class QwenClient:
    def __init__(self, base_url: str = "http://localhost:1234/v1", 
                 model: str = "qwen2.5", 
                 temperature: float = 0.7,
                 max_tokens: int = 4096):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history: List[Dict] = []
    
    def generate(self, prompt: str, system_prompt: str = None, 
                 temperature: float = None, 
                 max_tokens: int = None) -> Dict:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            
            self.history.append({
                "prompt": prompt,
                "response": content,
                "model": self.model,
            })
            
            return {
                "success": True,
                "content": content,
                "usage": result.get("usage", {}),
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to LLM server. Is LMStudio running?",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def chat(self, messages: List[Dict], 
             temperature: float = None,
             max_tokens: int = None) -> Dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "content": content,
                "usage": result.get("usage", {}),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def generate_json(self, prompt: str, schema: Dict = None) -> Dict:
        system_prompt = "You must respond with valid JSON only."
        if schema:
            system_prompt += f" The JSON must follow this schema: {json.dumps(schema)}"
        
        result = self.generate(prompt, system_prompt=system_prompt)
        
        if result.get("success"):
            try:
                content = result["content"]
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                parsed = json.loads(content.strip())
                return {"success": True, "data": parsed}
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"JSON parse error: {e}"}
        
        return result
    
    def clear_history(self) -> None:
        self.history.clear()
    
    def get_history(self) -> List[Dict]:
        return self.history.copy()


def create_client(config: Dict = None) -> QwenClient:
    config = config or {}
    return QwenClient(
        base_url=config.get("base_url", "http://localhost:1234/v1"),
        model=config.get("model", "qwen2.5"),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4096),
    )
