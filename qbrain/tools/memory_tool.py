from .base_tool import BaseTool, ToolResult
import json
import os
from datetime import datetime
from typing import List, Dict, Any


class MemoryStoreTool(BaseTool):
    name = "memory_store"
    description = "Store information in agent memory"
    parameters = {
        "key": {"type": "string", "description": "Memory key"},
        "value": {"type": "string", "description": "Value to store"},
        "metadata": {"type": "object", "description": "Additional metadata"},
    }
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.memory_file = config.get("memory_file", "agent_memory.json") if config else "agent_memory.json"
        self._ensure_memory_file()
    
    def _ensure_memory_file(self):
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump({}, f)
    
    def execute(self, key: str, value: str, metadata: dict = None) -> ToolResult:
        try:
            with open(self.memory_file, "r") as f:
                memory = json.load(f)
            
            memory[key] = {
                "value": value,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
            }
            
            with open(self.memory_file, "w") as f:
                json.dump(memory, f, indent=2)
            
            return ToolResult(success=True, data={"key": key, "stored": True})
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class MemorySearchTool(BaseTool):
    name = "memory_search"
    description = "Search agent memory"
    parameters = {
        "query": {"type": "string", "description": "Search query"},
        "limit": {"type": "integer", "description": "Max results", "default": 10},
    }
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.memory_file = config.get("memory_file", "agent_memory.json") if config else "agent_memory.json"
    
    def execute(self, query: str, limit: int = 10) -> ToolResult:
        try:
            if not os.path.exists(self.memory_file):
                return ToolResult(success=True, data=[])
            
            with open(self.memory_file, "r") as f:
                memory = json.load(f)
            
            query_lower = query.lower()
            results = []
            
            for key, value in memory.items():
                if query_lower in key.lower() or query_lower in str(value.get("value", "")).lower():
                    results.append({
                        "key": key,
                        "value": value.get("value"),
                        "timestamp": value.get("timestamp"),
                    })
            
            return ToolResult(success=True, data=results[:limit])
        except Exception as e:
            return ToolResult(success=False, error=str(e))
