from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import re


class InsightsEngine:
    def __init__(self):
        self.min_data_points = 3
    
    def get_all_insights(self, feedback_data: List[Dict]) -> Dict:
        if len(feedback_data) < self.min_data_points:
            return {
                "status": "insufficient_data",
                "message": f"Potrzeba minimum {self.min_data_points} recenzji. Masz {len(feedback_data)}.",
                "insights": None
            }
        
        return {
            "status": "ready",
            "total_reviews": len(feedback_data),
            "insights": {
                "accuracy": self._calculate_accuracy(feedback_data),
                "patterns": self._analyze_patterns(feedback_data),
                "recommendations": self._generate_recommendations(feedback_data),
                "trends": self._analyze_trends(feedback_data)
            }
        }
    
    def _calculate_accuracy(self, data: List[Dict]) -> Dict:
        total = len(data)
        accepted = sum(1 for r in data if r.get("status") == "accepted")
        rejected = sum(1 for r in data if r.get("status") == "rejected")
        pending = sum(1 for r in data if r.get("status") == "pending")
        
        processed = accepted + rejected
        accuracy = accepted / processed if processed > 0 else 0
        
        by_type = {}
        for item in data:
            ftype = item.get("feedback_type", "quality")
            if ftype not in by_type:
                by_type[ftype] = {"accepted": 0, "rejected": 0, "pending": 0}
            
            status = item.get("status", "pending")
            if status in by_type[ftype]:
                by_type[ftype][status] += 1
        
        accuracy_by_type = {}
        for ftype, counts in by_type.items():
            processed = counts["accepted"] + counts["rejected"]
            if processed > 0:
                accuracy_by_type[ftype] = {
                    "accuracy": counts["accepted"] / processed,
                    "accepted": counts["accepted"],
                    "rejected": counts["rejected"]
                }
        
        return {
            "overall": round(accuracy, 3),
            "accepted": accepted,
            "rejected": rejected,
            "pending": pending,
            "total": total,
            "by_type": accuracy_by_type
        }
    
    def _analyze_patterns(self, data: List[Dict]) -> Dict:
        if not data:
            return {}
        
        timestamps = []
        issue_types = []
        
        for item in data:
            if "timestamp" in item:
                timestamps.append(item["timestamp"])
            ftype = item.get("feedback_type", "unknown")
            issue_types.append(ftype)
        
        type_counts = Counter(issue_types)
        most_common = type_counts.most_common(5)
        
        patterns = {
            "most_common_issues": [
                {"type": t, "count": c, "percentage": round(c / len(data) * 100, 1)}
                for t, c in most_common
            ],
            "avg_issues_per_review": round(len(data) / max(len(set(item.get("mr_iid", 0) for item in data)), 1), 2)
        }
        
        confidence_scores = [r.get("ai_confidence", 0.5) for r in data]
        if confidence_scores:
            patterns["avg_ai_confidence"] = round(sum(confidence_scores) / len(confidence_scores), 3)
        
        return patterns
    
    def _analyze_trends(self, data: List[Dict]) -> Dict:
        if len(data) < 10:
            return {"status": "insufficient_data", "message": "Potrzeba więcej danych dla trendów"}
        
        sorted_data = sorted(data, key=lambda x: x.get("timestamp", ""))
        
        recent = sorted_data[-5:]
        older = sorted_data[-10:-5] if len(sorted_data) >= 10 else sorted_data[:5]
        
        recent_acc = self._calculate_accuracy(recent).get("overall", 0)
        older_acc = self._calculate_accuracy(older).get("overall", 0) if older else 0
        
        trend = "stable"
        if recent_acc > older_acc + 0.1:
            trend = "improving"
        elif recent_acc < older_acc - 0.1:
            trend = "declining"
        
        return {
            "status": "analyzed",
            "accuracy_trend": trend,
            "recent_accuracy": recent_acc,
            "older_accuracy": older_acc,
            "interpretation": self._interpret_trend(trend)
        }
    
    def _interpret_trend(self, trend: str) -> str:
        interpretations = {
            "improving": "System się poprawia - jakość recenzji rośnie",
            "declining": "System wymaga uwagi - jakość może się pogarszać",
            "stable": "System jest stabilny - jakość utrzymuje się na stałym poziomie"
        }
        return interpretations.get(trend, "Nie można określić trendu")
    
    def _generate_recommendations(self, data: List[Dict]) -> List[Dict]:
        recommendations = []
        
        accuracy_data = self._calculate_accuracy(data)
        accuracy = accuracy_data.get("overall", 0)
        
        if accuracy >= 0.9:
            recommendations.append({
                "type": "positive",
                "priority": "high",
                "message": "Świetna jakość! Accuracy na poziomie 90%+. Kontynuuj obecny styl.",
                "action": "maintain"
            })
        elif accuracy >= 0.7:
            recommendations.append({
                "type": "neutral",
                "priority": "medium",
                "message": "Dobra jakość (70-90%). Można jeszcze poprawić.",
                "action": "optimize"
            })
        else:
            recommendations.append({
                "type": "warning",
                "priority": "high",
                "message": "Accuracy poniżej 70%. Wymaga analizy i poprawy promptów.",
                "action": "review"
            })
        
        by_type = accuracy_data.get("by_type", {})
        for ftype, stats in by_type.items():
            if stats.get("accuracy", 0) < 0.5 and stats.get("accepted", 0) + stats.get("rejected", 0) >= 3:
                recommendations.append({
                    "type": "improvement",
                    "priority": "medium",
                    "message": f"Typ '{ftype}' ma niską accuracy ({stats['accuracy']:.0%}). Rozważ większą pewność przed raportowaniem.",
                    "action": "increase_threshold"
                })
            elif stats.get("accuracy", 0) >= 0.9 and stats.get("accepted", 0) >= 3:
                recommendations.append({
                    "type": "positive",
                    "priority": "low",
                    "message": f"Typ '{ftype}' ma wysoką accuracy ({stats['accuracy']:.0%}). Ten styl działa!",
                    "action": "maintain"
                })
        
        if len(data) < 10:
            recommendations.append({
                "type": "info",
                "priority": "low",
                "message": f"Zebrano {len(data)} recenzji. Więcej danych = lepsze insights.",
                "action": "collect_more"
            })
        
        return recommendations
    
    def get_patterns(self, data: List[Dict]) -> Dict:
        return self._analyze_patterns(data)
    
    def get_recommendations(self, data: List[Dict]) -> List[Dict]:
        return self._generate_recommendations(data)


_insights_engine = None


def get_insights_engine() -> InsightsEngine:
    global _insights_engine
    if _insights_engine is None:
        _insights_engine = InsightsEngine()
    return _insights_engine
