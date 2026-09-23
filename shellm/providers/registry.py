"""
Model resolution — determines which model + credentials to use.

Priority order:
  1. Ollama running locally          → free, zero config
  2. ~/.shellm/config.yaml default   → user's saved preference
  3. Environment variables           → ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY
  4. Nothing found                   → prompt user to run `shellm configure`
"""

import os
from typing import Optional, Tuple
from .ollama import detect_ollama, pick_ollama_model
from ..config import load_config


def resolve_model(model_flag: Optional[str]) -> Tuple[str, dict]:
    """
    Determine model string and extra kwargs for litellm.completion.

    Returns:
        (model_string, extra_kwargs)
        extra_kwargs may contain api_base, api_key, etc.
    """
    # Explicit --model flag always wins
    if model_flag:
        return _apply_env_key(model_flag), {}

    # 1. Saved config — user's explicit choice beats everything
    cfg = load_config()
    if cfg.get("default_provider") and cfg.get("providers"):
        provider = cfg["default_provider"]
        pcfg = cfg["providers"].get(provider, {})
        if pcfg.get("model"):
            model = pcfg["model"]
            extra = {}
            if pcfg.get("api_key"):
                extra["api_key"] = pcfg["api_key"]
            if pcfg.get("api_base"):
                extra["api_base"] = pcfg["api_base"]
            print(f"  ⚙  Using \033[32m{provider}\033[0m → {model}\n")
            return model, extra

    # 2. Ollama auto-detect (free, zero-config fallback)
    ollama = detect_ollama()
    if ollama and ollama["models"]:
        model = pick_ollama_model(ollama["models"])
        print(f"  🦙 Ollama detected — using \033[32m{model}\033[0m (free, local)\n")
        return model, {"api_base": ollama["base_url"]}

    # 3. Environment variable keys
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude-sonnet-4-5", {}
    if os.environ.get("OPENAI_API_KEY"):
        return "gpt-4o", {}
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini/gemini-3.6-flash", {}

    # 4. Nothing — guide the user
    raise RuntimeError(
        "\n\033[33mNo model configured.\033[0m Run one of:\n\n"
        "  shellm auth login gemini    → free Gemini key (aistudio.google.com/apikey)\n"
        "  shellm auth login anthropic → Anthropic API key\n"
        "  shellm auth login ollama    → use local Ollama models\n\n"
        "Install Ollama free at: https://ollama.ai"
    )


def _apply_env_key(model: str) -> str:
    """Nothing to do — LiteLLM reads env keys automatically."""
    return model
