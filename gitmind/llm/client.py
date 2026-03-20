import requests
from typing import Dict, List, Optional
import json


class LLMClient:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.base_url = self.config.get("base_url", "http://localhost:1234/v1")
        self.model = self.config.get("model", "qwen2.5-7b-instruct.gguf")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.history: List[Dict] = []
    
    def generate(self, prompt: str, system_prompt: str = None, 
                temperature: float = None, max_tokens: int = None) -> Dict:
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
                "error": "Cannot connect to LLM server",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def chat(self, messages: List[Dict], 
             temperature: float = None, max_tokens: int = None) -> Dict:
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
    
    def clear_history(self):
        self.history.clear()
    
    def get_history(self) -> List[Dict]:
        return self.history.copy()


# Prompt templates for GitLab operations
CODE_REVIEW_SYSTEM = """You are an expert code reviewer with 15+ years of experience reviewing code in production systems.

Your task is to review code changes and provide CRITICAL, ACTIONABLE feedback.

## Review Checklist - ALWAYS CHECK:

### SECURITY (CRITICAL)
- Passwords/auth stored in plaintext?
- SQL injection vulnerabilities?
- XSS vulnerabilities?
- Hardcoded secrets/API keys?
- Unvalidated user input?
- Improper error messages leaking info?

### LOGIC BUGS
- Off-by-one errors?
- Wrong operators (+ instead of -, * instead of /)?
- Wrong conditions (== vs =, && vs ||)?
- Null/None handling?
- Empty input handling?
- Division by zero?

### CODE QUALITY
- Unused variables?
- Magic numbers?
- Missing error handling?
- No tests?
- Code duplication?

### PERFORMANCE
- N+1 queries?
- Memory leaks?
- Unnecessary loops?

## Response Format:
Respond in Polish. Start with "## AI Code Review" header.

For each issue found:
1. **Severity**: CRITICAL / HIGH / MEDIUM / LOW
2. **File & Line**: Which file and approximate location
3. **Problem**: What is wrong
4. **Fix**: How to fix it

If code is good: "Code looks solid. No major issues found." """


ISSUE_RESPONSE_SYSTEM = """You are a helpful AI assistant for GitLab Issues.
Your task is to help users with their questions and issues.

Guidelines:
- Be helpful and informative
- Ask clarifying questions when needed
- Provide code examples when relevant
- Be polite and professional"""


MR_DESCRIPTION_SYSTEM = """You are an expert developer creating GitLab Merge Request descriptions.
Your task is to create clear, comprehensive descriptions for merge requests.

Include:
1. Summary of changes
2. Motivation/context
3. Key changes
4. Testing performed
5. Related issues"""


def create_llm_client(config: Dict = None) -> LLMClient:
    return LLMClient(config)
