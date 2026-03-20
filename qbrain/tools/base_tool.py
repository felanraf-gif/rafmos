from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
from datetime import datetime


class ToolResult:
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def __str__(self):
        if self.success:
            return f"ToolResult(success=True, data={self.data})"
        return f"ToolResult(success=False, error={self.error})"


class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base tool"
    parameters: Dict = {}
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.usage_count = 0
        self.success_count = 0
        self.total_latency = 0.0
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
    
    def _track_usage(self, success: bool, latency: float):
        self.usage_count += 1
        if success:
            self.success_count += 1
        self.total_latency += latency
    
    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "usage_count": self.usage_count,
            "success_rate": self.success_count / max(1, self.usage_count),
            "avg_latency": self.total_latency / max(1, self.usage_count),
        }
    
    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
