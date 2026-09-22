"""Ollama auto-detection — checks localhost:11434 and lists available models."""

import urllib.request
import urllib.error
import json

OLLAMA_BASE = "http://localhost:11434"


def detect_ollama() -> dict | None:
    """
    Check if Ollama is running locally.
    Returns {"running": True, "models": [...]} or None if not found.
    """
    try:
        req = urllib.request.urlopen(f"{OLLAMA_BASE}/api/tags", timeout=2)
        data = json.loads(req.read())
        models = [m["name"] for m in data.get("models", [])]
        return {"running": True, "models": models, "base_url": OLLAMA_BASE}
    except Exception:
        return None


def pick_ollama_model(models: list[str]) -> str:
    """
    Pick the best available Ollama model.
    Prefers larger/smarter models when multiple are installed.
    """
    # Preference order — first match wins
    preferred = [
        "llama3.2", "llama3.1", "llama3", "llama2",
        "mistral", "mixtral", "gemma2", "gemma",
        "phi3", "phi", "qwen2", "deepseek-coder",
        "codellama", "neural-chat",
    ]
    for pref in preferred:
        for model in models:
            if model.startswith(pref):
                return f"ollama/{model}"
    # Fall back to first available
    return f"ollama/{models[0]}" if models else "ollama/llama3"
