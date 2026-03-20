import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gitmind.formatters import (
    format_review_comment,
    extract_severity,
    extract_stats_from_content,
    format_ai_response,
    SEVERITY_EMOJI,
    CATEGORY_EMOJI
)


class TestFormatterBasics:
    
    def test_severity_emojis_defined(self):
        assert 'CRITICAL' in SEVERITY_EMOJI
        assert 'HIGH' in SEVERITY_EMOJI
        assert 'MEDIUM' in SEVERITY_EMOJI
        assert 'LOW' in SEVERITY_EMOJI
    
    def test_category_emojis_defined(self):
        assert 'security' in CATEGORY_EMOJI
        assert 'bug' in CATEGORY_EMOJI
        assert 'performance' in CATEGORY_EMOJI


class TestExtractSeverity:
    
    def test_extract_critical(self):
        assert extract_severity("**Severity**: CRITICAL") == "CRITICAL"
        assert extract_severity("**Severity**: critical") == "CRITICAL"
    
    def test_extract_high(self):
        assert extract_severity("**Severity**: HIGH") == "HIGH"
    
    def test_extract_medium(self):
        assert extract_severity("**Severity**: MEDIUM") == "MEDIUM"
    
    def test_extract_low(self):
        assert extract_severity("**Severity**: LOW") == "LOW"
    
    def test_extract_default(self):
        assert extract_severity("Some other text") == "INFO"


class TestExtractStats:
    
    def test_counts_severities(self):
        content = """
        **Severity**: CRITICAL
        Found security issue
        
        **Severity**: HIGH
        Found potential bug
        
        **Severity**: MEDIUM
        Minor issue
        """
        stats = extract_stats_from_content(content)
        
        assert stats['critical'] >= 1
        assert stats['high'] >= 1
        assert stats['medium'] >= 1
        assert stats['total'] >= 3


class TestFormatReviewComment:
    
    def test_formats_with_emoji(self):
        content = "**Severity**: CRITICAL\n**Problem**: Found API key"
        result = format_review_comment(content)
        
        assert '🔴' in result
        assert 'CRITICAL' in result
        assert 'Found API key' in result
    
    def test_adds_footer(self):
        content = "Code looks good"
        result = format_review_comment(content)
        
        assert '*Wystawione przez GitMind AI*' in result
    
    def test_formats_no_issues(self):
        content = "Code looks good, no issues found"
        result = format_review_comment(content)
        
        assert '✅' in result


class TestFormatAiResponse:
    
    def test_no_issues_response(self):
        response = "No issues found"
        result = format_ai_response(response)
        
        assert '✅' in result
    
    def test_polish_no_issues(self):
        response = "Brak problemów w kodzie"
        result = format_ai_response(response)
        
        assert '✅' in result
    
    def test_normal_response(self):
        response = "Found a bug in line 5"
        result = format_ai_response(response)
        
        assert result == response
