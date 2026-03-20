from .base_tool import BaseTool, ToolResult


class HttpClientTool(BaseTool):
    name = "http_request"
    description = "Make HTTP requests to any API"
    parameters = {
        "method": {"type": "string", "description": "HTTP method"},
        "url": {"type": "string", "description": "URL to request"},
        "headers": {"type": "object", "description": "HTTP headers"},
        "json": {"type": "object", "description": "JSON body"},
    }
    
    def execute(self, method: str = "GET", url: str = "", 
                headers: dict = None, json: dict = None, 
                data: str = None) -> ToolResult:
        try:
            import requests
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                data=data,
                timeout=30,
            )
            
            return ToolResult(success=True, data={
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:10000],
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
