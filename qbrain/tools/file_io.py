from .base_tool import BaseTool, ToolResult
import os
import json
from pathlib import Path


class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read file contents"
    parameters = {
        "path": {"type": "string", "description": "File path to read"},
        "max_length": {"type": "integer", "description": "Max characters", "default": 10000},
    }
    
    def execute(self, path: str, max_length: int = 10000) -> ToolResult:
        try:
            abs_path = os.path.abspath(path)
            if not os.path.exists(abs_path):
                return ToolResult(success=False, error=f"File not found: {path}")
            
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read(max_length)
            
            return ToolResult(success=True, data={
                "path": abs_path,
                "content": content,
                "length": len(content),
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class FileWriteTool(BaseTool):
    name = "file_write"
    description = "Write content to a file"
    parameters = {
        "path": {"type": "string", "description": "File path to write"},
        "content": {"type": "string", "description": "Content to write"},
        "append": {"type": "boolean", "description": "Append mode", "default": False},
    }
    
    def execute(self, path: str, content: str, append: bool = False) -> ToolResult:
        try:
            abs_path = os.path.abspath(path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            mode = "a" if append else "w"
            with open(abs_path, mode, encoding="utf-8") as f:
                f.write(content)
            
            return ToolResult(success=True, data={
                "path": abs_path,
                "bytes_written": len(content),
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
