from .base_tool import BaseTool, ToolResult


class WebFetchTool(BaseTool):
    name = "web_fetch"
    description = "Fetch content from a URL"
    parameters = {
        "url": {"type": "string", "description": "URL to fetch"},
        "max_length": {"type": "integer", "description": "Max characters", "default": 5000}
    }
    
    def execute(self, url: str, max_length: int = 5000) -> ToolResult:
        try:
            import requests
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            content = response.text[:max_length]
            
            return ToolResult(success=True, data={
                "url": url,
                "status": response.status_code,
                "content": content,
                "length": len(content),
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
