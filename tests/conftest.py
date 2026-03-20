import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['TESTING'] = 'true'
os.environ['GROQ_API_KEY'] = 'test-key'
os.environ['GITLAB_TOKEN'] = 'test-token'


@pytest.fixture
def app():
    from gitmind.main import app as flask_app
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_gitlab():
    mock = MagicMock()
    mock.get_mr_changes.return_value = {
        'mr': {'title': 'Test MR', 'description': 'Test'},
        'changes': []
    }
    mock.create_mr_note.return_value = {'id': 123}
    return mock


@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock.generate.return_value = {
        'success': True,
        'content': 'Test review content'
    }
    return mock


@pytest.fixture
def sample_mr_payload():
    return {
        'object_kind': 'merge_request',
        'object_attributes': {
            'iid': 1,
            'action': 'open',
            'title': 'Test MR',
            'description': 'Test description'
        },
        'project': {'id': 12345}
    }


@pytest.fixture
def sample_mr_with_code():
    return {
        'object_kind': 'merge_request',
        'object_attributes': {
            'iid': 2,
            'action': 'open',
            'title': 'Add API module',
            'description': 'New API implementation'
        },
        'project': {'id': 12345},
        'mr': {
            'title': 'Add API module',
            'description': 'New API implementation',
            'changes': [{
                'diff': '@@ -0,0 +1 @@\n+API_KEY = "sk-test123"',
                'new_path': 'api.py',
                'old_path': 'api.py'
            }]
        }
    }
