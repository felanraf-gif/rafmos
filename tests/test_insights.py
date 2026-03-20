import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gitmind.insights import InsightsEngine, get_insights_engine


class TestInsightsEngine:
    
    def test_engine_initialization(self):
        engine = InsightsEngine()
        assert engine.min_data_points == 3
        assert isinstance(engine, InsightsEngine)
    
    def test_singleton(self):
        engine1 = get_insights_engine()
        engine2 = get_insights_engine()
        assert engine1 is engine2


class TestInsufficientData:
    
    def test_insufficient_data(self):
        engine = InsightsEngine()
        data = [{"status": "accepted"}, {"status": "pending"}]
        
        result = engine.get_all_insights(data)
        
        assert result["status"] == "insufficient_data"
        assert result["insights"] is None


class TestAccuracyCalculation:
    
    def test_full_accuracy(self):
        engine = InsightsEngine()
        data = [
            {"status": "accepted", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "bug"}
        ]
        
        result = engine.get_all_insights(data)
        
        assert result["status"] == "ready"
        assert result["insights"]["accuracy"]["overall"] == 1.0
        assert result["insights"]["accuracy"]["accepted"] == 3
        assert result["insights"]["accuracy"]["rejected"] == 0
    
    def test_partial_accuracy(self):
        engine = InsightsEngine()
        data = [
            {"status": "accepted", "feedback_type": "security"},
            {"status": "rejected", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "bug"},
            {"status": "rejected", "feedback_type": "bug"}
        ]
        
        result = engine.get_all_insights(data)
        
        assert result["insights"]["accuracy"]["overall"] == 0.5
        assert result["insights"]["accuracy"]["accepted"] == 2
        assert result["insights"]["accuracy"]["rejected"] == 2
    
    def test_zero_processed(self):
        engine = InsightsEngine()
        data = [
            {"status": "pending", "feedback_type": "security"},
            {"status": "pending", "feedback_type": "bug"},
            {"status": "pending", "feedback_type": "quality"}
        ]
        
        result = engine.get_all_insights(data)
        
        assert result["status"] == "ready"
        assert result["insights"]["accuracy"]["overall"] == 0
        assert result["insights"]["accuracy"]["pending"] == 3


class TestPatternsAnalysis:
    
    def test_most_common_issues(self):
        engine = InsightsEngine()
        data = [
            {"status": "accepted", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "bug"},
            {"status": "accepted", "feedback_type": "quality"}
        ]
        
        patterns = engine._analyze_patterns(data)
        
        assert len(patterns["most_common_issues"]) > 0
        assert patterns["most_common_issues"][0]["type"] == "security"
        assert patterns["most_common_issues"][0]["count"] == 2


class TestRecommendations:
    
    def test_high_accuracy_recommendation(self):
        engine = InsightsEngine()
        data = [
            {"status": "accepted", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "security"}
        ]
        
        recommendations = engine._generate_recommendations(data)
        
        assert any(r["type"] == "positive" for r in recommendations)
        assert any("90%" in r["message"] or "świetna" in r["message"].lower() for r in recommendations)
    
    def test_low_accuracy_recommendation(self):
        engine = InsightsEngine()
        data = [
            {"status": "rejected", "feedback_type": "quality"},
            {"status": "rejected", "feedback_type": "quality"},
            {"status": "rejected", "feedback_type": "quality"},
            {"status": "rejected", "feedback_type": "quality"}
        ]
        
        recommendations = engine._generate_recommendations(data)
        
        assert any(r["type"] == "warning" for r in recommendations)


class TestTrends:
    
    def test_insufficient_for_trends(self):
        engine = InsightsEngine()
        data = [{"status": "accepted"} for _ in range(5)]
        
        trends = engine._analyze_trends(data)
        
        assert trends["status"] == "insufficient_data"
    
    def test_stable_trend(self):
        engine = InsightsEngine()
        data = [{"status": "accepted", "feedback_type": "security", "timestamp": f"2024-01-{i:02d}"}
                for i in range(15)]
        
        trends = engine._analyze_trends(data)
        
        assert trends["status"] == "analyzed"
        assert "interpretation" in trends


class TestAccuracyByType:
    
    def test_by_type_accuracy(self):
        engine = InsightsEngine()
        data = [
            {"status": "accepted", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "security"},
            {"status": "rejected", "feedback_type": "security"},
            {"status": "accepted", "feedback_type": "bug"}
        ]
        
        result = engine.get_all_insights(data)
        by_type = result["insights"]["accuracy"]["by_type"]
        
        assert "security" in by_type
        assert by_type["security"]["accuracy"] == 2/3
        assert by_type["security"]["accepted"] == 2
        assert by_type["security"]["rejected"] == 1
