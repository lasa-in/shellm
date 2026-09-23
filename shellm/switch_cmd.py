"""
`shellm switch` — quickly change the default provider/model.

Usage:
  shellm switch              → interactive picker
  shellm switch gemini       → switch to Gemini
  shellm switch anthropic    → switch to Anthropic / Claude
  shellm switch openai       → switch to OpenAI / GPT
  shellm switch ollama       → switch to local Ollama

Also available inside the REPL:
  shellm> switch
  shellm> switch gemini
"""

from .config import load_config, save_config
from .providers.ollama import detect_ollama


PROVIDER_MODELS = {
    "gemini":    "gemini/gemini-3.6-flash",
    "anthropic": "claude-sonnet-4-5",
    "openai":    "gpt-4o",
    "ollama":    "ollama/llama3",
}


def cmd_switch(args: list) -> None:
    """Entry point for `shellm switch [provider]`."""
    cfg = load_config()
    providers = cfg.get("providers", {})
    current = cfg.get("default_provider", "none")

    # Show status + picker if no arg given
    if not args:
        _show_status(providers, current)
        target = _prompt_provider(providers)
    else:
        target = args[0].lower()

    if not target:
        return

    # Ollama: check it's actually running
    if target == "ollama":
        ollama = detect_ollama()
        if not ollama or not ollama["models"]:
            print("  ❌ Ollama is not running. Start it first: ollama serve")
            return

    # Provider must be configured (have credentials)
    if target not in providers and target != "ollama":
        print(f"\n  ⚠  {target} is not configured yet.")
        print(f"  Run: \033[1mshellm auth login {target}\033[0m\n")
        return

    # Update default_provider in config
    cfg["default_provider"] = target
    save_config(cfg)

    model = providers.get(target, {}).get("model") or PROVIDER_MODELS.get(target, target)
    print(f"\n  ✅ Switched to \033[32m{target}\033[0m → {model}")
    print(f"  Restart shellm (or open a new session) to use it.\n")


def _show_status(providers: dict, current: str) -> None:
    """Print a numbered list of configured providers."""
    print("\n  \033[1mConfigured providers\033[0m\n")

    ollama = detect_ollama()
    if ollama and ollama["models"]:
        marker = " ← current" if current == "ollama" else ""
        print(f"  🦙  ollama    {', '.join(ollama['models'][:2])}{marker}")

    for p, pcfg in providers.items():
        marker = " ← current" if p == current else ""
        model = pcfg.get("model", "")
        cred = "OAuth" if pcfg.get("token") else "API key" if pcfg.get("api_key") else "local"
        print(f"  ✅  {p:<12}{model}  [{cred}]{marker}")

    print()


def _prompt_provider(providers: dict) -> str:
    """Interactive numbered picker."""
    choices = list(providers.keys())
    if detect_ollama():
        if "ollama" not in choices:
            choices.insert(0, "ollama")

    if not choices:
        print("  No providers configured. Run: shellm auth login gemini\n")
        return ""

    for i, p in enumerate(choices, 1):
        print(f"    {i}. {p}")

    raw = input("  Switch to (number or name): ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(choices):
        return choices[int(raw) - 1]
    return raw.lower()
