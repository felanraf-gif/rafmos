from flask import Flask, request, jsonify
from typing import Dict, Any, Callable, List
import hmac
import hashlib
import logging

from gitmind.llm.client import LLMClient
from gitmind.api.gitlab_client import GitLabClient
from gitmind.prompts import get_review_prompt
from gitmind.feedback import get_feedback_storage
from gitmind.learning import get_learning_engine
from gitmind.cache import mr_cache, llm_cache, cache_key
from gitmind.formatters import format_review_comment, extract_stats_from_content
import re

logging.basicConfig(level=logging.INFO)


def sanitize_secrets(text: str) -> str:
    if text is None:
        return None
    
    patterns = [
        (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{8,})', r'\1[HIDDEN]'),
        (r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-\.]{8,})', r'\1[HIDDEN]'),
        (r'(password["\']?\s*[:=]\s*["\']?)([^\s"\']{4,})', r'\1[HIDDEN]'),
        (r'(secret["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{8,})', r'\1[HIDDEN]'),
        (r'(bearer\s+)([a-zA-Z0-9_\-\.]{10,})', r'\1[HIDDEN]'),
        (r'(sk\-)[a-zA-Z0-9]{20,}', r'\1[HIDDEN]'),
        (r'(gsk_)[a-zA-Z0-9]{20,}', r'\1[HIDDEN]'),
        (r'(ghp_)[a-zA-Z0-9]{20,}', r'\1[HIDDEN]'),
        (r'(glpat\-)[a-zA-Z0-9_\-\.]{10,}', r'\1[HIDDEN]'),
        (r'"([a-zA-Z_]+)"\s*:\s*"([a-zA-Z0-9_\-]{20,})"', r'"\1": "[HIDDEN]"'),
        (r"'([a-zA-Z_]+)'\s*[:=]\s*'([a-zA-Z0-9_\-]{20,})'", r'"\1": "[HIDDEN]"'),
        (r'(eyJ[a-zA-Z0-9_\-]{20,})', r'[JWT HIDDEN]'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text
logger = logging.getLogger(__name__)


class WebhookHandler:
    def __init__(self, gitlab_client: GitLabClient, llm_client: LLMClient, secret_token: str = None):
        self.gitlab = gitlab_client
        self.llm = llm_client
        self.secret_token = secret_token
        self.handlers: Dict[str, Callable] = {}
        self.feedback_storage = get_feedback_storage()
        self.learning_engine = get_learning_engine()
        
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        self.register("merge_request", self.handle_merge_request)
        self.register("issue", self.handle_issue)
        self.register("note", self.handle_note)
        self.register("push", self.handle_push)
    
    def register(self, event_type: str, handler: Callable):
        self.handlers[event_type] = handler
    
    def verify_token(self, token: str) -> bool:
        if not self.secret_token:
            return True
        return hmac.compare_digest(token, self.secret_token)
    
    def handle(self, event_type: str, payload: Dict) -> Dict:
        handler = self.handlers.get(event_type)
        if handler:
            try:
                return handler(payload)
            except Exception as e:
                logger.error(f"Error handling {event_type}: {e}")
                return {"error": str(e)}
        return {"message": f"No handler for {event_type}"}
    
    def handle_merge_request(self, payload: Dict) -> Dict:
        action = payload.get("object_attributes", {}).get("action")
        project_id = payload.get("project", {}).get("id")
        mr_iid = payload.get("object_attributes", {}).get("iid")
        
        if action == "open" or action == "reopen":
            return self.process_mr_review(project_id, mr_iid)
        elif action == "merge":
            self.feedback_storage.mark_outdated(mr_iid, project_id)
            return {"message": "MR merged", "feedback_marked_outdated": True}
        
        return {"message": f"Action {action} not processed"}
    
    def process_mr_review(self, project_id: str, mr_iid: int) -> Dict:
        cache_k = cache_key(project_id, mr_iid)
        
        cached = mr_cache.get(cache_k)
        if cached:
            logger.info(f"Using cached MR data for !{mr_iid}")
            mr, changes = cached['mr'], cached['changes']
        else:
            mr_changes = self.gitlab.get_mr_changes(project_id, mr_iid)
            mr = mr_changes.get("mr", {})
            changes = mr_changes.get("changes", [])
            mr_cache.set(cache_k, {'mr': mr, 'changes': changes})
        
        review_content = self._prepare_review_content(mr, changes)
        
        response = self.llm.generate(
            prompt=review_content,
            system_prompt=get_review_prompt()
        )
        
        if response.get("success"):
            sanitized_content = sanitize_secrets(response['content'])
            stats = extract_stats_from_content(sanitized_content)
            formatted_content = format_review_comment(sanitized_content, stats)
            comment = f"## 🧠 AI Code Review\n\n{formatted_content}"
            
            try:
                note_result = self.gitlab.create_mr_note(project_id, mr_iid, comment)
                comment_id = note_result.get("id", 0)
                
                self.feedback_storage.add_review(
                    mr_iid=mr_iid,
                    project_id=int(project_id),
                    comment_id=comment_id,
                    content=response['content'],
                    ai_confidence=0.7
                )
                
                logger.info(f"Review saved for MR !{mr_iid}, comment_id: {comment_id}")
                
                return {"success": True, "comment_added": True, "feedback_saved": True}
            except Exception as e:
                logger.error(f"Failed to add feedback: {e}")
                return {"success": True, "comment_added": False, "error": str(e)}
        
        return {"success": False, "error": "LLM generation failed"}
    
    def _prepare_review_content(self, mr: Dict, changes: List[Dict]) -> str:
        content = f"""# Merge Request Review

## Title: {mr.get('title')}
## Description: {mr.get('description', 'No description')}

## Changes:

"""
        
        for change in changes[:10]:
            diff = change.get("diff", "")
            new_file = change.get("new_path", "")
            old_file = change.get("old_path", "")
            
            content += f"\n### File: {new_file or old_file}\n"
            content += f"```diff\n{diff[:2000]}\n```\n"
        
        content += "\n\nPlease provide a code review focusing on:\n"
        content += "1. Potential bugs or issues\n"
        content += "2. Code quality and best practices\n"
        content += "3. Security concerns\n"
        content += "4. Performance implications\n"
        
        return content
    
    def handle_issue(self, payload: Dict) -> Dict:
        action = payload.get("object_attributes", {}).get("action")
        project_id = payload.get("project", {}).get("id")
        issue_iid = payload.get("object_attributes", {}).get("iid")
        
        if action == "open":
            return self.process_issue_response(project_id, issue_iid)
        
        return {"message": f"Action {action} not processed"}
    
    def process_issue_response(self, project_id: str, issue_iid: int) -> Dict:
        issue = self.gitlab.get_issue(project_id, issue_iid)
        
        prompt = f"""Issue Title: {issue.get('title')}
Issue Description: {issue.get('description', 'No description')}

Please provide helpful assistance with this issue. Ask clarifying questions if needed and suggest solutions."""

        response = self.llm.generate(
            prompt=prompt,
            system_prompt="You are a helpful AI assistant for GitLab issues. Be informative and helpful."
        )
        
        if response.get("success"):
            comment = f"## AI Assistant\n\n{response['content']}"
            
            try:
                self.gitlab.create_issue_note(project_id, issue_iid, comment)
                return {"success": True, "comment_added": True}
            except Exception as e:
                return {"success": True, "comment_added": False, "error": str(e)}
        
        return {"success": False}
    
    def handle_note(self, payload: Dict) -> Dict:
        note_type = payload.get("noteable_type")
        
        if note_type == "MergeRequest":
            return self.handle_mr_comment(payload)
        elif note_type == "Issue":
            return self.handle_issue_comment(payload)
        
        return {"message": "Note type not processed"}
    
    def handle_mr_comment(self, payload: Dict) -> Dict:
        project_id = payload.get("project", {}).get("id")
        mr_iid = payload.get("merge_request", {}).get("iid")
        comment = payload.get("comment", {}).get("body", "")
        
        if comment.startswith("@gitmind") or "help" in comment.lower():
            return self.process_ai_assist(project_id, mr_iid, comment)
        
        return {"message": "Not an AI command"}
    
    def handle_issue_comment(self, payload: Dict) -> Dict:
        return {"message": "Issue comment processed"}
    
    def process_ai_assist(self, project_id: str, mr_iid: int, comment: str) -> Dict:
        prompt = comment.replace("@gitmind", "").strip()
        
        mr = self.gitlab.get_mr_changes(project_id, mr_iid)
        context = f"MR Title: {mr.get('mr', {}).get('title', '')}\n"
        
        prompt_with_context = f"{context}\n\nUser question: {prompt}"
        
        response = self.llm.generate(prompt_with_context)
        
        if response.get("success"):
            sanitized = sanitize_secrets(response['content'])
            self.gitlab.create_mr_note(project_id, mr_iid, f"## AI Response\n\n{sanitized}")
        
        return {"success": True}
    
    def handle_push(self, payload: Dict) -> Dict:
        return {"message": "Push event received"}


def create_webhook_handler(gitlab_token: str, llm_config: Dict, secret: str = None) -> WebhookHandler:
    gitlab = GitLabClient(token=gitlab_token)
    llm = LLMClient(llm_config)
    return WebhookHandler(gitlab, llm, secret)
