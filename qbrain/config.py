import os

LLM_CONFIG = {
    "provider": "groq",
    "base_url": "http://localhost:1234/v1",
    "model": "gemma-3-4b-it",
    "temperature": 0.7,
    "max_tokens": 4096,
}

GROQ_CONFIG = {
    "api_key": os.environ.get("GROQ_API_KEY", ""),
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 4096,
}

LMSTUDIO_CONFIG = {
    "base_url": "http://localhost:1234/v1",
    "model": "qwen2.5-7b-instruct.gguf",
    "temperature": 0.7,
    "max_tokens": 4096,
}

TOOLS_CONFIG = {
    "enabled": [
        "web_search",
        "web_fetch", 
        "http_request",
        "python_exec",
        "file_read",
        "file_write",
        "calculator",
        "memory_store",
        "memory_search",
    ],
    "web_search": {
        "provider": "exa",
        "default_limit": 10,
    },
    "http_request": {
        "timeout": 30,
    },
    "python_exec": {
        "timeout": 30,
        "max_output_size": 10000,
    },
}

AGENT_CONFIG = {
    "explorer": {
        "exploration_rate": 0.8,
        "curiosity_weight": 0.3,
    },
    "solver": {
        "exploitation_rate": 0.9,
        "reasoning_depth": 3,
    },
    "verifier": {
        "strict_mode": True,
        "retry_on_fail": 2,
    },
}

MEMORY_CONFIG = {
    "max_memories": 10000,
    "similarity_threshold": 0.8,
    "forget_rate": 0.1,
}

ORCHESTRATOR_CONFIG = {
    "max_iterations": 3,
    "timeout_seconds": 60,
    "consensus_threshold": 0.8,
}

LEARNING_CONFIG = {
    "feedback_window": 20,
    "evolution_interval": 100,
    "success_threshold": 0.7,
    "failure_threshold": 0.3,
}

def get_llm_config():
    return LLM_CONFIG.copy()

def get_groq_config():
    return GROQ_CONFIG.copy()

def get_lmstudio_config():
    return LMSTUDIO_CONFIG.copy()

def get_tools_config():
    return TOOLS_CONFIG.copy()

def get_agent_config(agent_type=None):
    if agent_type and agent_type in AGENT_CONFIG:
        return AGENT_CONFIG[agent_type].copy()
    return AGENT_CONFIG.copy()
