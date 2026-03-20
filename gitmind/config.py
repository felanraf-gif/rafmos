import os

# GitLab Configuration
GITLAB_CONFIG = {
    "gitlab_url": os.environ.get("GITLAB_URL", "https://gitlab.com"),
    "api_version": "v4",
    "timeout": 30,
}

# OAuth Configuration
OAUTH_CONFIG = {
    "app_id": os.environ.get("GITLAB_APP_ID", ""),
    "app_secret": os.environ.get("GITLAB_APP_SECRET", ""),
    "callback_url": os.environ.get("GITLAB_CALLBACK_URL", ""),
}

# LLM Configuration
LLM_CONFIG = {
    "provider": os.environ.get("LLM_PROVIDER", "groq"),
    "base_url": os.environ.get("LLM_URL", "http://localhost:1234/v1"),
    "model": os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile"),
    "temperature": 0.7,
    "max_tokens": 4096,
}

# Groq Configuration
GROQ_CONFIG = {
    "api_key": os.environ.get("GROQ_API_KEY", ""),
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 4096,
}

# Application Configuration
APP_CONFIG = {
    "host": os.environ.get("HOST", "0.0.0.0"),
    "port": int(os.environ.get("PORT", "8000")),
    "debug": os.environ.get("DEBUG", "false").lower() == "true",
    "secret_key": os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production"),
}

# Database Configuration
DB_CONFIG = {
    "url": os.environ.get("DATABASE_URL", ""),
}

# Rate Limiting
RATE_LIMIT = {
    "free_tier": 50,  # requests per month
    "pro_tier": 1000,
}

# Features Toggle
FEATURES = {
    "code_review": True,
    "issue_response": True,
    "mr_description": True,
    "bug_analysis": True,
    "security_scan": False,
}


def get_gitlab_config():
    return GITLAB_CONFIG.copy()


def get_llm_config():
    return LLM_CONFIG.copy()


def get_app_config():
    return APP_CONFIG.copy()
