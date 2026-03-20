import re
from typing import Any, Dict, Optional, Tuple
from functools import wraps


class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class InputValidator:
    
    MAX_STRING_LENGTH = 10000
    MAX_ARRAY_LENGTH = 100
    MAX_DEPTH = 10
    
    @staticmethod
    def validate_string(value: Any, field: str, max_length: int = None, required: bool = True) -> Optional[str]:
        if value is None or value == '':
            if required:
                raise ValidationError(field, f"{field} is required")
            return None
        
        if not isinstance(value, str):
            raise ValidationError(field, f"{field} must be a string")
        
        if len(value) > (max_length or InputValidator.MAX_STRING_LENGTH):
            raise ValidationError(field, f"{field} exceeds maximum length of {max_length or InputValidator.MAX_STRING_LENGTH}")
        
        sanitized = InputValidator.sanitize_string(value)
        return sanitized
    
    @staticmethod
    def validate_integer(value: Any, field: str, min_val: int = None, max_val: int = None, required: bool = True) -> Optional[int]:
        if value is None:
            if required:
                raise ValidationError(field, f"{field} is required")
            return None
        
        try:
            int_val = int(value)
        except (ValueError, TypeError):
            raise ValidationError(field, f"{field} must be an integer")
        
        if min_val is not None and int_val < min_val:
            raise ValidationError(field, f"{field} must be at least {min_val}")
        
        if max_val is not None and int_val > max_val:
            raise ValidationError(field, f"{field} must be at most {max_val}")
        
        return int_val
    
    @staticmethod
    def validate_dict(value: Any, field: str, required: bool = True, max_depth: int = None) -> Optional[Dict]:
        if value is None:
            if required:
                raise ValidationError(field, f"{field} is required")
            return None
        
        if not isinstance(value, dict):
            raise ValidationError(field, f"{field} must be an object")
        
        current_depth = max_depth or InputValidator.MAX_DEPTH
        sanitized = InputValidator.sanitize_dict(value, current_depth)
        
        return sanitized
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        if not isinstance(value, str):
            return str(value)
        
        value = value.strip()
        
        value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
        
        return value
    
    @staticmethod
    def sanitize_dict(value: Dict, max_depth: int = 10) -> Dict:
        if max_depth <= 0:
            return {}
        
        result = {}
        for k, v in value.items():
            if not isinstance(k, str):
                k = str(k)
            
            k = InputValidator.sanitize_string(k)
            
            if isinstance(v, dict):
                result[k] = InputValidator.sanitize_dict(v, max_depth - 1)
            elif isinstance(v, list):
                result[k] = InputValidator.sanitize_list(v, max_depth - 1)
            elif isinstance(v, str):
                result[k] = InputValidator.sanitize_string(v)
            elif isinstance(v, (int, float, bool)):
                result[k] = v
            elif v is None:
                result[k] = None
            else:
                result[k] = str(v)
        
        return result
    
    @staticmethod
    def sanitize_list(value: list, max_depth: int = 10) -> list:
        if max_depth <= 0:
            return []
        
        if len(value) > InputValidator.MAX_ARRAY_LENGTH:
            value = value[:InputValidator.MAX_ARRAY_LENGTH]
        
        result = []
        for item in value:
            if isinstance(item, dict):
                result.append(InputValidator.sanitize_dict(item, max_depth - 1))
            elif isinstance(item, list):
                result.append(InputValidator.sanitize_list(item, max_depth - 1))
            elif isinstance(item, str):
                result.append(InputValidator.sanitize_string(item))
            elif isinstance(item, (int, float, bool)):
                result.append(item)
            elif item is None:
                result.append(None)
            else:
                result.append(str(item))
        
        return result


def validate_mr_payload(payload: Dict) -> Tuple[bool, Optional[str]]:
    try:
        validator = InputValidator()
        
        validator.validate_dict(payload, "payload")
        
        object_attrs = payload.get('object_attributes')
        if object_attrs is None:
            raise ValidationError("object_attributes", "object_attributes is required")
        
        object_attrs = validator.validate_dict(object_attrs, "object_attributes")
        mr_iid = object_attrs.get('iid') if object_attrs else None
        validator.validate_integer(mr_iid, "mr_iid", min_val=1, required=True)
        
        project = payload.get('project')
        if project is None:
            raise ValidationError("project", "project is required")
        
        project = validator.validate_dict(project, "project")
        project_id = project.get('id') if project else None
        validator.validate_integer(project_id, "project_id", min_val=1, required=True)
        
        return True, None
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_review_request(data: Dict) -> Tuple[bool, Optional[str]]:
    try:
        validator = InputValidator()
        
        mr_iid = validator.validate_integer(data.get('mr_iid'), "mr_iid", min_val=1, required=True)
        project_id = validator.validate_integer(data.get('project_id'), "project_id", min_val=1, required=True)
        
        if data.get('action'):
            validator.validate_string(data.get('action'), "action", max_length=50)
        
        return True, None
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_chat_request(data: Dict) -> Tuple[bool, Optional[str]]:
    try:
        validator = InputValidator()
        
        message = validator.validate_string(data.get('message'), "message", max_length=5000, required=True)
        
        return True, None
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {str(e)}"
