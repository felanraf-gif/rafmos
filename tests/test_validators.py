import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gitmind.validators import (
    InputValidator,
    ValidationError,
    validate_mr_payload,
    validate_review_request,
    validate_chat_request
)


class TestInputValidatorString:
    
    def test_validate_string_success(self):
        result = InputValidator.validate_string("hello", "test")
        assert result == "hello"
    
    def test_validate_string_required_failure(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_string(None, "test", required=True)
    
    def test_validate_string_not_string(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_string(123, "test")
    
    def test_validate_string_too_long(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_string("a" * 20000, "test", max_length=100)
    
    def test_validate_string_sanitizes(self):
        result = InputValidator.validate_string("  hello  ", "test")
        assert result == "hello"
    
    def test_validate_string_removes_control_chars(self):
        result = InputValidator.validate_string("hello\x00world", "test")
        assert "\x00" not in result


class TestInputValidatorInteger:
    
    def test_validate_integer_success(self):
        result = InputValidator.validate_integer(42, "test")
        assert result == 42
    
    def test_validate_integer_from_string(self):
        result = InputValidator.validate_integer("42", "test")
        assert result == 42
    
    def test_validate_integer_required_failure(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_integer(None, "test", required=True)
    
    def test_validate_integer_not_number(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_integer("abc", "test")
    
    def test_validate_integer_below_min(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_integer(0, "test", min_val=1)
    
    def test_validate_integer_above_max(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_integer(100, "test", max_val=50)


class TestInputValidatorDict:
    
    def test_validate_dict_success(self):
        result = InputValidator.validate_dict({"key": "value"}, "test")
        assert result == {"key": "value"}
    
    def test_validate_dict_required_failure(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_dict(None, "test")
    
    def test_validate_dict_not_dict(self):
        with pytest.raises(ValidationError):
            InputValidator.validate_dict("not a dict", "test")


class TestValidateMRPayload:
    
    def test_valid_payload(self):
        payload = {
            'object_attributes': {'iid': 1},
            'project': {'id': 123}
        }
        valid, error = validate_mr_payload(payload)
        assert valid is True
        assert error is None
    
    def test_missing_mr_iid(self):
        payload = {
            'object_attributes': {},
            'project': {'id': 123}
        }
        valid, error = validate_mr_payload(payload)
        assert valid is False
        assert 'mr_iid' in error.lower()
    
    def test_missing_project_id(self):
        payload = {
            'object_attributes': {'iid': 1},
            'project': {}
        }
        valid, error = validate_mr_payload(payload)
        assert valid is False
        assert 'project_id' in error.lower()
    
    def test_invalid_mr_iid(self):
        payload = {
            'object_attributes': {'iid': -1},
            'project': {'id': 123}
        }
        valid, error = validate_mr_payload(payload)
        assert valid is False


class TestValidateReviewRequest:
    
    def test_valid_request(self):
        data = {'mr_iid': 1, 'project_id': 123}
        valid, error = validate_review_request(data)
        assert valid is True
    
    def test_missing_mr_iid(self):
        data = {'project_id': 123}
        valid, error = validate_review_request(data)
        assert valid is False
        assert 'mr_iid' in error.lower()
    
    def test_missing_project_id(self):
        data = {'mr_iid': 1}
        valid, error = validate_review_request(data)
        assert valid is False
        assert 'project_id' in error.lower()
    
    def test_negative_values(self):
        data = {'mr_iid': -1, 'project_id': -1}
        valid, error = validate_review_request(data)
        assert valid is False


class TestValidateChatRequest:
    
    def test_valid_request(self):
        data = {'message': 'Hello'}
        valid, error = validate_chat_request(data)
        assert valid is True
    
    def test_missing_message(self):
        data = {}
        valid, error = validate_chat_request(data)
        assert valid is False
        assert 'message' in error.lower()
    
    def test_message_too_long(self):
        data = {'message': 'a' * 10000}
        valid, error = validate_chat_request(data)
        assert valid is False
