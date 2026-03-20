from .base_tool import BaseTool, ToolResult
import requests
import os
from urllib.parse import quote


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for information"
    parameters = {
        "query": {"type": "string", "description": "Search query"},
        "num_results": {"type": "integer", "description": "Number of results", "default": 5}
    }
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.llm_client = None
    
    def set_llm_client(self, client):
        self.llm_client = client
    
    def execute(self, query: str, num_results: int = 5) -> ToolResult:
        # Try Exa
        exa_key = os.environ.get("EXA_API_KEY") or "158476c9-1bc5-425b-ba87-12e20d14c683"
        if exa_key:
            result = self._search_exa(query, num_results, exa_key)
            if result.success:
                return result
        
        # Try Serper
        serper_key = os.environ.get("SERPER_API_KEY")
        if serper_key:
            result = self._search_serper(query, num_results, serper_key)
            if result.success:
                return result
        
        # Use DuckDuckGo
        result = self._search_ddg(query)
        if result.success:
            return result
        
        # Fallback: use LLM if available
        if self.llm_client:
            return self._search_llm_fallback(query)
        
        return ToolResult(success=False, error="All search methods failed. Set EXA_API_KEY or SERPER_API_KEY for better results.")
    
    def _search_exa(self, query: str, num_results: int, api_key: str) -> ToolResult:
        try:
            from exa_py import Exa
            exa = Exa(api_key=api_key)
            results = exa.search(query=query, num_results=num_results)
            
            parsed = []
            for r in results.results:
                parsed.append({
                    "title": r.title,
                    "url": r.url,
                    "snippet": getattr(r, 'snippet', ''),
                })
            
            return ToolResult(success=True, data=parsed)
        except Exception as e:
            return ToolResult(success=False, error=f"Exa: {e}")
    
    def _search_serper(self, query: str, num_results: int, api_key: str) -> ToolResult:
        try:
            url = "https://google.serper.dev/search"
            headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
            payload = {"q": query, "num": num_results}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("organic", [])[:num_results]:
                results.append({
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "snippet": item.get("snippet"),
                })
            
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, error=f"Serper: {e}")
    
    def _search_ddg(self, query: str) -> ToolResult:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            
            response = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for result in soup.select(".result")[:5]:
                title_elem = result.select_one(".result__title")
                link_elem = result.select_one(".result__url")
                snippet_elem = result.select_one(".result__snippet")
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = ""
                    if link_elem:
                        link = link_elem.get_text(strip=True)
                        if link and not link.startswith("http"):
                            link = "https://" + link
                    
                    snippet = ""
                    if snippet_elem:
                        snippet = snippet_elem.get_text(strip=True)
                    
                    if title:
                        results.append({
                            "title": title,
                            "url": link,
                            "snippet": snippet,
                        })
            
            if results:
                return ToolResult(success=True, data=results)
            
            return ToolResult(success=False, error="No results")
        except Exception as e:
            return ToolResult(success=False, error=f"DDG: {e}")
    
    def _search_llm_fallback(self, query: str) -> ToolResult:
        if not self.llm_client:
            return ToolResult(success=False, error="No LLM client")
        
        try:
            result = self.llm_client.generate(
                f"Provide a brief answer to this question: {query}"
            )
            
            if result.get("success"):
                return ToolResult(success=True, data=[{
                    "title": query,
                    "url": "",
                    "snippet": result.get("content", "")[:500],
                }])
            
            return ToolResult(success=False, error="LLM failed")
        except Exception as e:
            return ToolResult(success=False, error=f"LLM fallback: {e}")
