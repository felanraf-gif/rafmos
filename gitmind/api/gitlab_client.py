import requests
from typing import Dict, List, Optional, Any
import base64


class GitLabClient:
    def __init__(self, token: str = None, gitlab_url: str = "https://gitlab.com"):
        self.token = token
        self.gitlab_url = gitlab_url
        self.api_url = f"{gitlab_url}/api/v4"
        self.session = requests.Session()
        if token:
            self.session.headers.update({"PRIVATE-TOKEN": token})
    
    def set_token(self, token: str):
        self.token = token
        self.session.headers.update({"PRIVATE-TOKEN": token})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.api_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_current_user(self) -> Dict:
        return self._request("GET", "/user")
    
    def get_project(self, project_id: str) -> Dict:
        return self._request("GET", f"/projects/{project_id}")
    
    def get_projects(self, membership: bool = True, owned: bool = False) -> List[Dict]:
        params = {"membership": membership, "owned": owned}
        return self._request("GET", "/projects", params=params)
    
    def get_merge_requests(self, project_id: str, state: str = "opened") -> List[Dict]:
        params = {"state": state}
        return self._request("GET", f"/projects/{project_id}/merge_requests", params=params)
    
    def get_mr_changes(self, project_id: str, mr_iid: int) -> Dict:
        return self._request("GET", f"/projects/{project_id}/merge_requests/{mr_iid}/changes")
    
    def get_mr_diff(self, project_id: str, mr_iid: int) -> List[Dict]:
        return self._request("GET", f"/projects/{project_id}/merge_requests/{mr_iid}/diffs")
    
    def get_mr_discussions(self, project_id: str, mr_iid: int) -> List[Dict]:
        return self._request("GET", f"/projects/{project_id}/merge_requests/{mr_iid}/discussions")
    
    def create_mr_note(self, project_id: str, mr_iid: int, body: str) -> Dict:
        data = {"body": body}
        return self._request("POST", f"/projects/{project_id}/merge_requests/{mr_iid}/notes", json=data)
    
    def create_mr_discussion(self, project_id: str, mr_iid: int, body: str, position: Dict = None) -> Dict:
        data = {"body": body}
        if position:
            data["position"] = position
        return self._request("POST", f"/projects/{project_id}/merge_requests/{mr_iid}/discussions", json=data)
    
    def get_issues(self, project_id: str, state: str = "opened") -> List[Dict]:
        params = {"state": state}
        return self._request("GET", f"/projects/{project_id}/issues", params=params)
    
    def get_issue(self, project_id: str, issue_iid: int) -> Dict:
        return self._request("GET", f"/projects/{project_id}/issues/{issue_iid}")
    
    def create_issue_note(self, project_id: str, issue_iid: int, body: str) -> Dict:
        data = {"body": body}
        return self._request("POST", f"/projects/{project_id}/issues/{issue_iid}/notes", json=data)
    
    def get_file_content(self, project_id: str, file_path: str, ref: str = "main") -> str:
        endpoint = f"/projects/{project_id}/repository/files/{file_path.replace('/', '%2F')}"
        params = {"ref": ref}
        data = self._request("GET", endpoint, params=params)
        if "content" in data:
            return base64.b64decode(data["content"]).decode("utf-8")
        return ""
    
    def get_commit(self, project_id: str, sha: str) -> Dict:
        return self._request("GET", f"/projects/{project_id}/repository/commits/{sha}")
    
    def get_commit_diff(self, project_id: str, sha: str) -> List[Dict]:
        return self._request("GET", f"/projects/{project_id}/repository/commits/{sha}/diff")
    
    def get_branches(self, project_id: str) -> List[Dict]:
        return self._request("GET", f"/projects/{project_id}/repository/branches")
    
    def get_tags(self, project_id: str) -> List[Dict]:
        return self._request("GET", f"/projects/{project_id}/repository/tags")
    
    def get_project_members(self, project_id: str) -> List[Dict]:
        return self._request("GET", f"/projects/{project_id}/members/all")
    
    def get_pipeline(self, project_id: str, pipeline_id: int) -> Dict:
        return self._request("GET", f"/projects/{project_id}/pipelines/{pipeline_id}")
    
    def get_pipeline_jobs(self, project_id: str, pipeline_id: int) -> List[Dict]:
        return self._request("GET", f"/projects/{project_id}/pipelines/{pipeline_id}/jobs")
    
    def search_projects(self, query: str) -> List[Dict]:
        params = {"search": query, "scope": "blobs"}
        return self._request("GET", "/projects", params=params)
    
    def search_code(self, project_id: str, query: str) -> List[Dict]:
        params = {"scope": "blobs", "search": query}
        return self._request("GET", f"/projects/{project_id}/search", params=params)


def create_gitlab_client(token: str = None, gitlab_url: str = "https://gitlab.com") -> GitLabClient:
    return GitLabClient(token=token, gitlab_url=gitlab_url)
