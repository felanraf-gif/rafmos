from .base_tool import BaseTool, ToolResult
import requests
import json


class ArxivSearchTool(BaseTool):
    name = "arxiv_search"
    description = "Search arXiv for scientific papers"
    parameters = {
        "query": {"type": "string", "description": "Search query"},
        "max_results": {"type": "integer", "description": "Max results", "default": 5}
    }
    
    def execute(self, query: str, max_results: int = 5) -> ToolResult:
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            from xml.etree import ElementTree
            root = ElementTree.fromstring(response.text)
            
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            results = []
            for entry in root.findall("atom:entry", ns)[:max_results]:
                results.append({
                    "title": entry.find("atom:title", ns).text.strip(),
                    "summary": entry.find("atom:summary", ns).text.strip()[:300],
                    "authors": [a.text for a in entry.findall("atom:author/atom:name", ns)],
                    "published": entry.find("atom:published", ns).text,
                    "pdf": entry.find("atom:id", ns).text.replace("abs", "pdf"),
                })
            
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GitHubTool(BaseTool):
    name = "github"
    description = "Search GitHub repositories"
    parameters = {
        "query": {"type": "string", "description": "Search query"},
        "repo": {"type": "string", "description": "Specific repo (user/repo)"},
        "action": {"type": "string", "description": "search, repo, issues", "default": "search"}
    }
    
    def execute(self, query: str = "", repo: str = None, action: str = "search") -> ToolResult:
        try:
            if action == "search":
                return self._search_repos(query)
            elif action == "repo" and repo:
                return self._get_repo(repo)
            elif action == "issues" and repo:
                return self._get_issues(repo)
            else:
                return ToolResult(success=False, error="Invalid action")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _search_repos(self, query: str) -> ToolResult:
        url = "https://api.github.com/search/repositories"
        params = {"q": query, "per_page": 5}
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get("items", [])[:5]:
            results.append({
                "name": item["name"],
                "full_name": item["full_name"],
                "description": item["description"],
                "stars": item["stargazers_count"],
                "language": item["language"],
                "url": item["html_url"],
            })
        
        return ToolResult(success=True, data=results)
    
    def _get_repo(self, repo: str) -> ToolResult:
        url = f"https://api.github.com/repos/{repo}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return ToolResult(success=True, data={
            "name": data["name"],
            "description": data["description"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "language": data["language"],
            "topics": data["topics"],
            "readme": data.get("default_branch"),
        })
    
    def _get_issues(self, repo: str) -> ToolResult:
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {"state": "open", "per_page": 5}
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        issues = []
        for item in response.json()[:5]:
            issues.append({
                "title": item["title"],
                "number": item["number"],
                "state": item["state"],
                "url": item["html_url"],
            })
        
        return ToolResult(success=True, data=issues)


class WikiTool(BaseTool):
    name = "wikipedia"
    description = "Search Wikipedia"
    parameters = {
        "query": {"type": "string", "description": "Search query"},
        "lang": {"type": "string", "description": "Language code", "default": "en"}
    }
    
    def execute(self, query: str, lang: str = "en") -> ToolResult:
        try:
            url = f"https://{lang}.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 5,
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("query", {}).get("search", [])[:5]:
                results.append({
                    "title": item["title"],
                    "snippet": item["snippet"].replace("<", "").replace(">", ""),
                    "pageid": item["pageid"],
                })
            
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class NewsTool(BaseTool):
    name = "news"
    description = "Get latest news"
    parameters = {
        "query": {"type": "string", "description": "Topic (optional)"},
        "lang": {"type": "string", "description": "Language", "default": "en"}
    }
    
    def execute(self, query: str = "", lang: str = "en") -> ToolResult:
        try:
            if query:
                url = "https://newsdata.io/api/1/news"
                params = {
                    "apikey": os.environ.get("NEWSDATA_API_KEY", ""),
                    "q": query,
                    "language": lang,
                }
                if not os.environ.get("NEWSDATA_API_KEY"):
                    return ToolResult(success=False, error="NEWSDATA_API_KEY not set")
            else:
                url = "https://newsdata.io/api/1/news"
                params = {
                    "apikey": os.environ.get("NEWSDATA_API_KEY", ""),
                    "category": "technology",
                }
                if not os.environ.get("NEWSDATA_API_KEY"):
                    return self._fallback_news(query, lang)
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("results", [])[:5]:
                results.append({
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "pubDate": item.get("pubDate"),
                    "source_id": item.get("source_id"),
                    "link": item.get("link"),
                })
            
            return ToolResult(success=True, data=results)
        except Exception as e:
            return self._fallback_news(query, lang)
    
    def _fallback_news(self, query: str, lang: str) -> ToolResult:
        return ToolResult(success=True, data=[{
            "title": f"News search for: {query or 'general'}",
            "description": "Set NEWSDATA_API_KEY for live news",
            "link": "",
        }])


class WeatherTool(BaseTool):
    name = "weather"
    description = "Get weather for a city"
    parameters = {
        "city": {"type": "string", "description": "City name"},
    }
    
    def execute(self, city: str) -> ToolResult:
        try:
            api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
            if not api_key:
                return ToolResult(success=False, error="OPENWEATHERMAP_API_KEY not set")
            
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric",
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return ToolResult(success=True, data={
                "city": data["name"],
                "country": data["sys"]["country"],
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))


import os
