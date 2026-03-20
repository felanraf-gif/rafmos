import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gitmind.webhooks.handler import sanitize_secrets


class TestSecretSanitization:
    
    def test_hides_openai_keys(self):
        text = 'Found API key sk-1234567890abcdefghijklmn'
        result = sanitize_secrets(text)
        assert 'sk-1234567890' not in result
        assert 'sk-' in result
        assert '[HIDDEN]' in result

    def test_hides_groq_keys(self):
        text = 'Token: gsk_AbCdEfGhIjKlMnOpQrStUvWx123456789'
        result = sanitize_secrets(text)
        assert 'gsk_AbCdEfGhIj' not in result
        assert '[HIDDEN]' in result

    def test_hides_github_tokens(self):
        text = 'GitHub token: ghp_AbCdEfGhIjKlMnOpQrStUvWx123456789'
        result = sanitize_secrets(text)
        assert 'ghp_AbCdEfGhIj' not in result
        assert '[HIDDEN]' in result

    def test_hides_gitlab_tokens(self):
        text = 'GitLab token: glpat-AbCdEfGhIjKlMnOpQrStUvWx123456789'
        result = sanitize_secrets(text)
        assert 'glpat-AbCdEf' not in result
        assert '[HIDDEN]' in result

    def test_hides_bearer_tokens(self):
        text = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0'
        result = sanitize_secrets(text)
        assert 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' not in result
        assert '[HIDDEN]' in result

    def test_hides_password_in_code(self):
        text = 'password = "supersecret123"'
        result = sanitize_secrets(text)
        assert 'supersecret123' not in result
        assert '[HIDDEN]' in result

    def test_hides_dict_style_tokens(self):
        text = '{"token": "abc123xyz789longtokenvalue"}'
        result = sanitize_secrets(text)
        assert 'abc123xyz789longtokenvalue' not in result
        assert '[HIDDEN]' in result

    def test_preserves_normal_text(self):
        text = 'This is a normal code review with no secrets.'
        result = sanitize_secrets(text)
        assert text == result

    def test_preserves_non_secret_urls(self):
        text = 'Check out https://example.com/api/users'
        result = sanitize_secrets(text)
        assert 'https://example.com' in result

    def test_handles_empty_string(self):
        result = sanitize_secrets('')
        assert result == ''

    def test_handles_none(self):
        result = sanitize_secrets(None)
        assert result is None

    def test_hides_database_passwords(self):
        text = 'db_password = "PostgresSecretPass123"'
        result = sanitize_secrets(text)
        assert 'PostgresSecretPass123' not in result
        assert '[HIDDEN]' in result

    def test_hides_jwt_tokens(self):
        text = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        result = sanitize_secrets(text)
        assert '[JWT HIDDEN]' in result

    def test_case_insensitive(self):
        text = 'API_KEY = "sk-ABC123"'
        result = sanitize_secrets(text)
        assert 'sk-ABC123' not in result
        assert '[HIDDEN]' in result

    def test_preserves_code_without_secrets(self):
        text = '''
        def hello():
            print("Hello World")
            return 42
        '''
        result = sanitize_secrets(text)
        assert 'def hello' in result
        assert 'return 42' in result

    def test_multiple_secrets_in_text(self):
        text = '''
        API_KEY = "sk-test123456789"
        GITHUB_TOKEN = "ghp_abcdefghij1234567890"
        '''
        result = sanitize_secrets(text)
        assert 'sk-test123456789' not in result
        assert 'ghp_abcdefghij1234567890' not in result
        assert result.count('[HIDDEN]') == 2
