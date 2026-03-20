import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWebhookIntegration:
    
    def test_full_review_flow(self):
        from gitmind.webhooks.handler import WebhookHandler
        
        mock_gitlab = MagicMock()
        mock_gitlab.get_mr_changes.return_value = {
            'mr': {
                'title': 'Add new feature',
                'description': 'This adds a new API endpoint'
            },
            'changes': [
                {
                    'diff': '@@ -0,0 +1 @@\n+def hello():\n+    return "Hello"',
                    'new_path': 'app.py',
                    'old_path': 'app.py'
                }
            ]
        }
        mock_gitlab.create_mr_note.return_value = {'id': 123, 'body': 'Test'}
        
        mock_llm = MagicMock()
        mock_llm.generate.return_value = {
            'success': True,
            'content': 'Good code, no issues found.'
        }
        
        handler = WebhookHandler(mock_gitlab, mock_llm)
        
        payload = {
            'object_kind': 'merge_request',
            'object_attributes': {
                'iid': 42,
                'action': 'open',
                'title': 'Add new feature'
            },
            'project': {'id': 123}
        }
        
        result = handler.handle('merge_request', payload)
        
        assert result['success'] is True
        assert result['comment_added'] is True
        
        mock_gitlab.get_mr_changes.assert_called_once_with(123, 42)
        mock_gitlab.create_mr_note.assert_called_once()
        mock_llm.generate.assert_called_once()

    def test_webhook_handles_merge_action(self):
        from gitmind.webhooks.handler import WebhookHandler
        
        mock_gitlab = MagicMock()
        mock_llm = MagicMock()
        
        handler = WebhookHandler(mock_gitlab, mock_llm)
        
        payload = {
            'object_kind': 'merge_request',
            'object_attributes': {
                'iid': 10,
                'action': 'merge'
            },
            'project': {'id': 123}
        }
        
        result = handler.handle('merge_request', payload)
        
        assert 'feedback_marked_outdated' in result
        assert result['feedback_marked_outdated'] is True

    def test_webhook_skips_closed_mr(self):
        from gitmind.webhooks.handler import WebhookHandler
        
        mock_gitlab = MagicMock()
        mock_llm = MagicMock()
        
        handler = WebhookHandler(mock_gitlab, mock_llm)
        
        payload = {
            'object_kind': 'merge_request',
            'object_attributes': {
                'iid': 10,
                'action': 'close'
            },
            'project': {'id': 123}
        }
        
        result = handler.handle('merge_request', payload)
        
        assert 'message' in result
        assert 'not processed' in result['message']
        mock_gitlab.get_mr_changes.assert_not_called()

    def test_webhook_handles_unknown_action(self):
        from gitmind.webhooks.handler import WebhookHandler
        
        mock_gitlab = MagicMock()
        mock_llm = MagicMock()
        
        handler = WebhookHandler(mock_gitlab, mock_llm)
        
        payload = {
            'object_kind': 'merge_request',
            'object_attributes': {
                'iid': 10,
                'action': 'update'
            },
            'project': {'id': 123}
        }
        
        result = handler.handle('merge_request', payload)
        
        assert 'message' in result

    def test_webhook_handles_missing_project_id(self):
        from gitmind.webhooks.handler import WebhookHandler
        
        mock_gitlab = MagicMock()
        mock_llm = MagicMock()
        
        handler = WebhookHandler(mock_gitlab, mock_llm)
        
        payload = {
            'object_kind': 'merge_request',
            'object_attributes': {
                'iid': 10,
                'action': 'open'
            }
        }
        
        result = handler.handle('merge_request', payload)
        
        assert 'error' in result or 'message' in result


class TestGitLabClientRetry:
    
    def test_client_retries_on_503(self):
        from requests.exceptions import HTTPError
        import requests
        
        with patch('requests.Session') as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.text = 'Service Unavailable'
            mock_response.raise_for_status.side_effect = HTTPError('503 Server Error')
            
            mock_session.return_value.request.return_value = mock_response
            
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test')
            
            with pytest.raises(HTTPError):
                client.get_project('123')


class TestSanitizationIntegration:
    
    def test_review_comment_sanitized(self):
        from gitmind.webhooks.handler import WebhookHandler, sanitize_secrets
        
        mock_gitlab = MagicMock()
        mock_gitlab.get_mr_changes.return_value = {
            'mr': {'title': 'Add API', 'description': 'Test'},
            'changes': [{'diff': '+API_KEY="sk-test123"', 'new_path': 'test.py', 'old_path': 'test.py'}]
        }
        mock_gitlab.create_mr_note.return_value = {'id': 1}
        
        mock_llm = MagicMock()
        mock_llm.generate.return_value = {
            'success': True,
            'content': 'Found API key sk-1234567890abcdefghijklmn in the code!'
        }
        
        handler = WebhookHandler(mock_gitlab, mock_llm)
        
        result = handler.process_mr_review('123', 1)
        
        mock_gitlab.create_mr_note.assert_called_once()
        call_args = mock_gitlab.create_mr_note.call_args
        comment_body = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get('body', '')
        
        assert 'sk-1234567890' not in comment_body
        assert '[HIDDEN]' in comment_body


class TestCacheIntegration:
    
    def test_cache_used_on_second_call(self):
        from gitmind.cache import SimpleCache
        
        cache = SimpleCache(max_size=10, ttl=60)
        
        cache.set('key1', 'value1')
        
        result1 = cache.get('key1')
        assert result1 == 'value1'
        
        result2 = cache.get('key1')
        assert result2 == 'value1'
        
        stats = cache.get_stats()
        assert stats['total_hits'] >= 1

    def test_cache_expires(self):
        from gitmind.cache import SimpleCache
        import time
        
        cache = SimpleCache(max_size=10, ttl=1)
        
        cache.set('key1', 'value1')
        
        result1 = cache.get('key1')
        assert result1 == 'value1'
        
        time.sleep(1.1)
        
        result2 = cache.get('key1')
        assert result2 is None

    def test_cache_eviction(self):
        from gitmind.cache import SimpleCache
        
        cache = SimpleCache(max_size=2, ttl=60)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        result1 = cache.get('key1')
        assert result1 is None
        
        result2 = cache.get('key2')
        assert result2 == 'value2'
        
        result3 = cache.get('key3')
        assert result3 == 'value3'
