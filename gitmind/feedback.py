import json
import os
import fcntl
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import threading

MAX_REVIEWS = 10000
MAX_DAYS = 90

@dataclass
class ReviewFeedback:
    mr_iid: int
    project_id: int
    comment_id: int
    content: str
    timestamp: str
    status: str  # pending, accepted, rejected, outdated
    feedback_type: str  # bug, security, quality, performance
    ai_confidence: float
    was_helpful: Optional[bool] = None


class FeedbackStorage:
    _lock = threading.Lock()
    
    def __init__(self, path: str = None):
        self.path = path or os.path.join(
            os.path.dirname(__file__), 
            "review_feedback.json"
        )
        self.reviews: List[Dict] = []
        self.load()
    
    def _cleanup_old_reviews(self) -> None:
        cutoff = datetime.now() - timedelta(days=MAX_DAYS)
        self.reviews = [
            r for r in self.reviews 
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]
        if len(self.reviews) > MAX_REVIEWS:
            self.reviews = self.reviews[-MAX_REVIEWS:]
    
    def add_review(self, mr_iid: int, project_id: int, 
                   comment_id: int, content: str,
                   ai_confidence: float = 0.5) -> bool:
        with self._lock:
            self.load()
            
            self._cleanup_old_reviews()
            
            feedback = ReviewFeedback(
                mr_iid=mr_iid,
                project_id=project_id,
                comment_id=comment_id,
                content=content[:500],
                timestamp=datetime.now().isoformat(),
                status="pending",
                feedback_type=self._classify_feedback(content),
                ai_confidence=ai_confidence
            )
            self.reviews.append(asdict(feedback))
            
            success = self._save_safe()
            return success
    
    def _classify_feedback(self, content: str) -> str:
        content_lower = content.lower()
        if any(w in content_lower for w in ["security", "sql", "xss", "injection", "password"]):
            return "security"
        elif any(w in content_lower for w in ["bug", "error", "wrong", "incorrect"]):
            return "bug"
        elif any(w in content_lower for w in ["performance", "slow", "memory"]):
            return "performance"
        return "quality"
    
    def mark_helpful(self, mr_iid: int, project_id: int, helpful: bool) -> bool:
        with self._lock:
            self.load()
            
            for review in reversed(self.reviews):
                if review["mr_iid"] == mr_iid and review["project_id"] == project_id:
                    if review["status"] == "pending":
                        review["was_helpful"] = helpful
                        review["status"] = "accepted" if helpful else "rejected"
                        return self._save_safe()
            return False
    
    def mark_outdated(self, mr_iid: int, project_id: int) -> bool:
        with self._lock:
            self.load()
            
            for review in reversed(self.reviews):
                if review["mr_iid"] == mr_iid and review["project_id"] == project_id:
                    if review["status"] == "pending":
                        review["status"] = "outdated"
                        return self._save_safe()
            return False
    
    def _save_safe(self) -> bool:
        try:
            with open(self.path, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(self.reviews, f, indent=2)
                    return True
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception:
            return False
    
    def load(self) -> None:
        try:
            with open(self.path, "r") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    self.reviews = json.load(f)
                except (json.JSONDecodeError, Exception):
                    self.reviews = []
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except FileNotFoundError:
            self.reviews = []
    
    def get_stats(self) -> Dict:
        with self._lock:
            total = len(self.reviews)
            if total == 0:
                return {"total": 0, "accepted": 0, "rejected": 0, "accuracy": 0}
            
            accepted = sum(1 for r in self.reviews if r["status"] == "accepted")
            rejected = sum(1 for r in self.reviews if r["status"] == "rejected")
            
            by_type = {}
            for r in self.reviews:
                ft = r["feedback_type"]
                if ft not in by_type:
                    by_type[ft] = {"total": 0, "accepted": 0, "rejected": 0}
                by_type[ft]["total"] += 1
                if r["status"] == "accepted":
                    by_type[ft]["accepted"] += 1
                elif r["status"] == "rejected":
                    by_type[ft]["rejected"] += 1
            
            return {
                "total": total,
                "accepted": accepted,
                "rejected": rejected,
                "accuracy": accepted / (accepted + rejected) if (accepted + rejected) > 0 else 0,
                "by_type": by_type
            }
    
    def get_recent(self, n: int = 10) -> List[Dict]:
        with self._lock:
            return self.reviews[-n:].copy()


_global_storage = None

def get_feedback_storage() -> FeedbackStorage:
    global _global_storage
    if _global_storage is None:
        _global_storage = FeedbackStorage()
    return _global_storage
