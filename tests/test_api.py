import json
import pytest
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    def test_health_returns_status(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'

    def test_health_includes_metrics(self, client):
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'memory_mb' in data
        assert 'cpu_percent' in data
        assert 'timestamp' in data


class TestWebhookEndpoint:
    def test_webhook_requires_json(self, client):
        response = client.post('/webhook', data='not json')
        assert response.status_code == 400

    def test_webhook_unknown_event_type(self, client):
        response = client.post('/webhook',
            json={'object_kind': 'unknown'},
            headers={'X-Gitlab-Event': 'Unknown Hook'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'No handler' in data.get('message', '')

    def test_webhook_merge_request_opens_review(self, client, sample_mr_payload):
        with patch('gitmind.main.webhook_handler') as mock_handler:
            mock_handler.handle.return_value = {
                'success': True,
                'comment_added': True
            }
            response = client.post('/webhook',
                json=sample_mr_payload,
                headers={'X-Gitlab-Event': 'Merge Request Hook'}
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True


class TestReviewEndpoint:
    def test_review_requires_json(self, client):
        response = client.post('/api/review', data='not json')
        assert response.status_code == 400

    def test_review_requires_mr_iid(self, client):
        response = client.post('/api/review',
            json={'project_id': 12345}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_review_requires_project_id(self, client):
        response = client.post('/api/review',
            json={'mr_iid': 1}
        )
        assert response.status_code == 400

    def test_review_success(self, client, sample_mr_payload):
        with patch('gitmind.main.webhook_handler') as mock_handler:
            mock_handler.handle.return_value = {
                'success': True,
                'comment_added': True
            }
            response = client.post('/api/review', json={
                'mr_iid': 1,
                'project_id': 12345,
                'action': 'open'
            })
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True


class TestChatEndpoint:
    def test_chat_requires_message(self, client):
        response = client.post('/api/chat', json={})
        assert response.status_code == 400

    def test_chat_success(self, client):
        with patch('gitmind.main.llm_client') as mock_llm:
            mock_llm.generate.return_value = {
                'success': True,
                'content': 'Test response'
            }
            response = client.post('/api/chat', json={
                'message': 'Hello'
            })
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'response' in data


class TestFeedbackEndpoint:
    def test_feedback_stats(self, client):
        response = client.get('/api/feedback/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'stats' in data
        assert 'analysis' in data

    def test_feedback_recent(self, client):
        response = client.get('/api/feedback/recent')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'feedback' in data
