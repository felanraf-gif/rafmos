from typing import Dict, List
from gitmind.feedback import get_feedback_storage
from gitmind.prompts import get_review_prompt


class LearningEngine:
    def __init__(self):
        self.storage = get_feedback_storage()
        self.prompt_adjustments = {
            "security": {"weight": 1.0, "threshold": 0.6, "min_confidence": 0.7},
            "bug": {"weight": 1.0, "threshold": 0.7, "min_confidence": 0.8},
            "quality": {"weight": 1.0, "threshold": 0.5, "min_confidence": 0.6},
            "performance": {"weight": 1.0, "threshold": 0.5, "min_confidence": 0.6},
        }
        self.feedback_history = []
    
    def analyze_performance(self) -> Dict:
        stats = self.storage.get_stats()
        adjustments = {}
        
        for ftype, data in stats.get("by_type", {}).items():
            total = data["total"]
            if total < 3:
                continue
            
            accepted = data["accepted"]
            rejected = data["rejected"]
            accuracy = accepted / (accepted + rejected) if (accepted + rejected) > 0 else 0
            
            current = self.prompt_adjustments.get(ftype, {})
            threshold = current.get("threshold", 0.5)
            
            if accuracy >= threshold:
                adjustments[ftype] = {
                    "status": "good",
                    "accuracy": accuracy,
                    "message": f"Dokładność {ftype}: {accuracy:.0%} - prompty OK"
                }
            else:
                adjustments[ftype] = {
                    "status": "needs_improvement",
                    "accuracy": accuracy,
                    "message": f"Dokładność {ftype}: {accuracy:.0%} - wymaga poprawy"
                }
        
        return {
            "overall": stats,
            "adjustments": adjustments
        }
    
    def get_improved_prompt(self, base_prompt: str, feedback_type: str = None) -> str:
        stats = self.storage.get_stats()
        by_type = stats.get("by_type", {})
        
        improvements = []
        
        for ftype, data in by_type.items():
            total = data["total"]
            if total < 5:
                continue
            
            accepted = data["accepted"]
            rejected = data["rejected"]
            
            if accepted + rejected == 0:
                continue
            
            accuracy = accepted / (accepted + rejected)
            
            if accuracy < 0.4:
                improvements.append(f"Bądź bardziej selektywny w kwestii {ftype}. Zgłaszaj tylko Pewne, oczywiste problemy.")
            elif accuracy > 0.85:
                improvements.append(f"Twoje uwagi dotyczące {ftype} są bardzo trafne. Kontynuuj w tym stylu.")
            elif accuracy < 0.6:
                improvements.append(f"Zwiększ pewność przed zgłaszaniem problemów {ftype}.")
        
        if improvements:
            return base_prompt + "\n\n" + "\n".join([f"- {imp}" for imp in improvements])
        
        return base_prompt
    
    def should_report_issue(self, issue_type: str) -> bool:
        config = self.prompt_adjustments.get(issue_type, {})
        min_confidence = config.get("min_confidence", 0.7)
        
        stats = self.storage.get_stats()
        by_type = stats.get("by_type", {})
        data = by_type.get(issue_type, {})
        
        total = data.get("total", 0)
        if total < 5:
            return True
        
        accepted = data.get("accepted", 0)
        rejected = data.get("rejected", 0)
        
        if accepted + rejected == 0:
            return True
        
        accuracy = accepted / (accepted + rejected)
        
        if issue_type == "security" and accuracy < 0.5:
            return False
        if issue_type == "bug" and accuracy < 0.6:
            return False
        
        return True
    
    def get_confidence_for_type(self, issue_type: str) -> float:
        stats = self.storage.get_stats()
        by_type = stats.get("by_type", {})
        data = by_type.get(issue_type, {})
        
        accepted = data.get("accepted", 0)
        rejected = data.get("rejected", 0)
        
        if accepted + rejected == 0:
            return 0.5
        
        return accepted / (accepted + rejected)
    
    def get_report_threshold(self, issue_type: str) -> float:
        config = self.prompt_adjustments.get(issue_type, {})
        base_threshold = config.get("min_confidence", 0.7)
        
        stats = self.storage.get_stats()
        by_type = stats.get("by_type", {})
        data = by_type.get(issue_type, {})
        
        total = data.get("total", 0)
        if total < 10:
            return base_threshold
        
        accuracy = self.get_confidence_for_type(issue_type)
        
        if accuracy > 0.8:
            return base_threshold * 0.9
        elif accuracy < 0.5:
            return base_threshold * 1.2
        
        return base_threshold
    
    def get_tips_for_reviewer(self) -> List[str]:
        stats = self.storage.get_stats()
        tips = []
        
        for ftype, data in stats.get("by_type", {}).items():
            accepted = data.get("accepted", 0)
            rejected = data.get("rejected", 0)
            total = accepted + rejected
            
            if total < 3:
                continue
            
            accuracy = accepted / total if total > 0 else 0
            
            if accuracy < 0.5:
                if ftype == "security":
                    tips.append("Zwiększ ostrożność przy wykrywaniu problemów bezpieczeństwa - często fałszywe alarmy")
                elif ftype == "bug":
                    tips.append("Sprawdź dokładnie logikę przed zgłoszeniem błędów - często fałszywe")
                elif ftype == "quality":
                    tips.append("Oceniaj jakość kodu bardziej liberalnie - za dużo uwag")
                elif ftype == "performance":
                    tips.append("Zidentyfikowane problemy wydajności nie były trafne")
        
        if not tips:
            tips.append("System zbiera feedback. Kontynuuj oznaczanie recenzji jako pomocne/nie pomocne.")
        
        return tips
    
    def learn_from_feedback(self, mr_iid: int, project_id: int, was_helpful: bool) -> Dict:
        recent = self.storage.get_recent(100)
        
        for review in reversed(recent):
            if review["mr_iid"] == mr_iid and review["project_id"] == project_id:
                if review["status"] == "pending":
                    feedback_type = review.get("feedback_type", "quality")
                    
                    if was_helpful:
                        adjustment = self._get_positive_adjustment(feedback_type)
                    else:
                        adjustment = self._get_negative_adjustment(feedback_type)
                    
                    self.feedback_history.append({
                        "mr_iid": mr_iid,
                        "type": feedback_type,
                        "helpful": was_helpful,
                        "adjustment": adjustment
                    })
                    
                    return {
                        "learned": True,
                        "feedback_type": feedback_type,
                        "adjustment": adjustment,
                        "total_lessons": len(self.feedback_history)
                    }
        
        return {"learned": False, "reason": "Review not found or already processed"}
    
    def _get_positive_adjustment(self, feedback_type: str) -> Dict:
        config = self.prompt_adjustments.get(feedback_type, {})
        threshold = config.get("threshold", 0.5)
        
        new_threshold = max(0.4, threshold - 0.05)
        self.prompt_adjustments[feedback_type]["threshold"] = new_threshold
        
        return {
            "action": "reduced_threshold",
            "old_threshold": threshold,
            "new_threshold": new_threshold,
            "reason": f"Pozytywny feedback dla {feedback_type}"
        }
    
    def _get_negative_adjustment(self, feedback_type: str) -> Dict:
        config = self.prompt_adjustments.get(feedback_type, {})
        threshold = config.get("threshold", 0.5)
        min_confidence = config.get("min_confidence", 0.7)
        
        new_threshold = min(0.9, threshold + 0.1)
        new_min_confidence = min(0.95, min_confidence + 0.1)
        
        self.prompt_adjustments[feedback_type]["threshold"] = new_threshold
        self.prompt_adjustments[feedback_type]["min_confidence"] = new_min_confidence
        
        return {
            "action": "increased_threshold",
            "old_threshold": threshold,
            "new_threshold": new_threshold,
            "old_min_confidence": min_confidence,
            "new_min_confidence": new_min_confidence,
            "reason": f"Negatywny feedback dla {feedback_type}"
        }
    
    def get_stats_summary(self) -> str:
        stats = self.storage.get_stats()
        
        total = stats.get("total", 0)
        if total == 0:
            return "Brak danych feedbacku. Zacznij zbierać informacje o recenzjach."
        
        accuracy = stats.get("accuracy", 0)
        accepted = stats.get("accepted", 0)
        rejected = stats.get("rejected", 0)
        
        summary = f"""📊 Statystyki Feedbacku:

• Wszystkie recenzje: {total}
• Zaakceptowane: {accepted} 
• Odrzucone: {rejected}
• Dokładność: {accuracy:.0%}

📈 Dokładność per typ:
"""
        
        for ftype, data in stats.get("by_type", {}).items():
            acc = data["accepted"] / (data["accepted"] + data["rejected"]) if (data["accepted"] + data["rejected"]) > 0 else 0
            summary += f"  • {ftype}: {acc:.0%} ({data['total']} recenzji)\n"
        
        tips = self.get_tips_for_reviewer()
        if tips:
            summary += "\n💡 Wskazówki:\n"
            for tip in tips:
                summary += f"  • {tip}\n"
        
        return summary
    
    def get_learning_status(self) -> Dict:
        return {
            "total_lessons": len(self.feedback_history),
            "recent_lessons": self.feedback_history[-10:],
            "adjustments": self.prompt_adjustments,
            "accuracy": self.storage.get_stats().get("accuracy", 0)
        }


_global_engine = None

def get_learning_engine() -> LearningEngine:
    global _global_engine
    if _global_engine is None:
        _global_engine = LearningEngine()
    return _global_engine
