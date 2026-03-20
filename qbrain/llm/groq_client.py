import requests
from typing import Dict, List, Any, Optional
import json
import time


class GroqClient:
    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile", 
                 temperature: float = 0.7, max_tokens: int = 4096,
                 timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key or ""
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.history: List[Dict] = []
    
    def generate(self, prompt: str, system_prompt: str = None, 
                 temperature: float = None, 
                 max_tokens: int = None,
                 timeout: int = None) -> Dict:
        
        timeout = timeout or self.timeout
        
        for attempt in range(self.max_retries):
            try:
                result = self._call_api(prompt, system_prompt, temperature, max_tokens, timeout)
                return result
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                return {"success": False, "error": f"Connection failed after {self.max_retries} retries: {str(e)}"}
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue
                return {"success": False, "error": f"HTTP Error: {e.response.status_code}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def _call_api(self, prompt: str, system_prompt: str, temperature: float, 
                 max_tokens: int, timeout: int) -> Dict:
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
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=timeout,
        )
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message", "API Error")}
        
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
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60,
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                return {"success": False, "error": result["error"].get("message", "API Error")}
            
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
    
    def get_available_models(self) -> List[str]:
        return [
            "gemma-3-4b-it",
            "gemma-3-7b-it", 
            "llama-3.1-8b-instant",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
        ]


def create_groq_client(config: Dict = None) -> GroqClient:
    config = config or {}
    return GroqClient(
        api_key=config.get("api_key", ""),
        model=config.get("model", "llama-3.3-70b-versatile"),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4096),
    )
