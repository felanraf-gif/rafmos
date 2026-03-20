from typing import Dict, List, Optional
from . import BaseTool, ToolResult


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_stats: Dict[str, Dict] = {}
    
    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        self._tool_stats[tool.name] = {
            "calls": 0,
            "success": 0,
            "failures": 0,
        }
    
    def unregister(self, name: str) -> bool:
        if name in self._tools:
            del self._tools[name]
            del self._tool_stats[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        return list(self._tools.keys())
    
    def get_all_schemas(self) -> List[Dict]:
        return [tool.get_schema() for tool in self._tools.values()]
    
    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        import time
        start = time.time()
        
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        try:
            result = tool.execute(**kwargs)
            latency = time.time() - start
            tool._track_usage(result.success, latency)
            
            self._tool_stats[tool_name]["calls"] += 1
            if result.success:
                self._tool_stats[tool_name]["success"] += 1
            else:
                self._tool_stats[tool_name]["failures"] += 1
            
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )
    
    def get_stats(self) -> Dict:
        return {
            name: {
                "calls": stats["calls"],
                "success_rate": stats["success"] / max(1, stats["calls"]),
            }
            for name, stats in self._tool_stats.items()
        }
    
    def get_best_tool(self, task_type: str) -> Optional[str]:
        stats = {k: v["success"] / max(1, v["calls"]) 
                 for k, v in self._tool_stats.items() if v["calls"] > 0}
        if not stats:
            return None
        return max(stats, key=stats.get)


_global_registry = None

def get_registry() -> ToolRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
        _register_default_tools()
    return _global_registry

def _register_default_tools():
    from .web_search import WebSearchTool
    from .web_fetch import WebFetchTool
    from .http_client import HttpClientTool
    from .python_exec import PythonExecTool
    from .file_io import FileReadTool, FileWriteTool
    from .calculator import CalculatorTool
    from .memory_tool import MemoryStoreTool, MemorySearchTool
    from .specialized import ArxivSearchTool, GitHubTool, WikiTool, NewsTool, WeatherTool
    
    registry = _global_registry
    registry.register(WebSearchTool())
    registry.register(WebFetchTool())
    registry.register(HttpClientTool())
    registry.register(PythonExecTool())
    registry.register(FileReadTool())
    registry.register(FileWriteTool())
    registry.register(CalculatorTool())
    registry.register(MemoryStoreTool())
    registry.register(MemorySearchTool())
    registry.register(ArxivSearchTool())
    registry.register(GitHubTool())
    registry.register(WikiTool())
    registry.register(NewsTool())
    registry.register(WeatherTool())
    registry.register(CalculatorTool())
    registry.register(MemoryStoreTool())
    registry.register(MemorySearchTool())
