import pytest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGitLabClient:
    
    def test_client_initialization(self):
        with patch('requests.Session'):
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test-token')
            assert client.token == 'test-token'
            assert client.gitlab_url == 'https://gitlab.com'
            assert client.api_url == 'https://gitlab.com/api/v4'

    def test_client_custom_url(self):
        with patch('requests.Session'):
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(
                token='test-token',
                gitlab_url='https://selfhosted-gitlab.com'
            )
            assert client.api_url == 'https://selfhosted-gitlab.com/api/v4'

    def test_set_token(self):
        with patch('requests.Session'):
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient()
            client.set_token('new-token')
            assert client.token == 'new-token'

    def test_get_project(self):
        with patch('requests.Session') as mock_session:
            mock_response = MagicMock()
            mock_response.json.return_value = {'id': 123, 'name': 'test'}
            mock_session.return_value.request.return_value = mock_response
            
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test')
            result = client.get_project('123')
            
            mock_session.return_value.request.assert_called_once()
            call_args = mock_session.return_value.request.call_args
            assert call_args[0][0] == 'GET'
            assert '/projects/123' in call_args[0][1]

    def test_get_mr_changes(self):
        with patch('requests.Session') as mock_session:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'mr': {'title': 'Test'},
                'changes': []
            }
            mock_session.return_value.request.return_value = mock_response
            
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test')
            result = client.get_mr_changes('123', 1)
            
            assert result['mr']['title'] == 'Test'

    def test_create_mr_note(self):
        with patch('requests.Session') as mock_session:
            mock_response = MagicMock()
            mock_response.json.return_value = {'id': 456, 'body': 'test'}
            mock_session.return_value.request.return_value = mock_response
            
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test')
            result = client.create_mr_note('123', 1, 'Test comment')
            
            call_args = mock_session.return_value.request.call_args
            assert call_args[0][0] == 'POST'
            assert 'notes' in call_args[0][1]

    def test_get_merge_requests(self):
        with patch('requests.Session') as mock_session:
            mock_response = MagicMock()
            mock_response.json.return_value = [
                {'iid': 1, 'title': 'MR 1'},
                {'iid': 2, 'title': 'MR 2'}
            ]
            mock_session.return_value.request.return_value = mock_response
            
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test')
            result = client.get_merge_requests('123', state='opened')
            
            assert len(result) == 2
            assert result[0]['iid'] == 1

    def test_get_file_content_decodes_base64(self):
        with patch('requests.Session') as mock_session:
            import base64
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'content': base64.b64encode(b'print("hello")').decode()
            }
            mock_session.return_value.request.return_value = mock_response
            
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test')
            result = client.get_file_content('123', 'test.py')
            
            assert result == 'print("hello")'

    def test_get_branches(self):
        with patch('requests.Session') as mock_session:
            mock_response = MagicMock()
            mock_response.json.return_value = [
                {'name': 'main'},
                {'name': 'develop'}
            ]
            mock_session.return_value.request.return_value = mock_response
            
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test')
            result = client.get_branches('123')
            
            assert len(result) == 2
            assert result[0]['name'] == 'main'

    def test_search_code(self):
        with patch('requests.Session') as mock_session:
            mock_response = MagicMock()
            mock_response.json.return_value = [
                {'filename': 'test.py'}
            ]
            mock_session.return_value.request.return_value = mock_response
            
            from gitmind.api.gitlab_client import GitLabClient
            client = GitLabClient(token='test')
            result = client.search_code('123', 'TODO')
            
            call_args = mock_session.return_value.request.call_args
            assert 'search' in str(call_args)
