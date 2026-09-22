"""
`shellm auth` subcommands — login, logout, status.

Usage:
  shellm auth login gemini      → Google Device OAuth (browser)
  shellm auth login anthropic   → API key prompt (OAuth coming when Anthropic opens it)
  shellm auth login openai      → API key prompt
  shellm auth status            → show current auth state
  shellm auth logout            → clear saved credentials
"""

from .config import load_config, save_config, set_provider, get_provider_token
from .providers.gemini_oauth import login as gemini_login, revoke as gemini_revoke, GeminiOAuthError


PROVIDER_MODELS = {
    "gemini":    "gemini/gemini-1.5-flash",
    "anthropic": "claude-sonnet-4-5",
    "openai":    "gpt-4o",
    "ollama":    "ollama/llama3",
}


def cmd_auth(args: list[str]) -> None:
    """Entry point for `shellm auth <subcommand> [provider]`."""
    if not args:
        _print_usage()
        return

    sub = args[0].lower()

    if sub == "login":
        provider = args[1].lower() if len(args) > 1 else _prompt_provider()
        _login(provider)

    elif sub == "logout":
        provider = args[1].lower() if len(args) > 1 else _current_provider()
        _logout(provider)

    elif sub == "status":
        _status()

    else:
        print(f"Unknown auth subcommand: {sub}")
        _print_usage()


def _login(provider: str) -> None:
    if provider == "gemini":
        try:
            token = gemini_login()
            set_provider("gemini", PROVIDER_MODELS["gemini"], token=token)
            print("  ✅ Gemini saved to ~/.shellm/config.yaml")
            print("  Run \033[1mshellm\033[0m to start chatting.\n")
        except GeminiOAuthError:
            # OAuth app not registered — fall back to API key
            print("\n  Gemini browser login isn't configured yet.")
            print("  Get a free API key (no credit card) at: \033[4mhttps://aistudio.google.com/apikey\033[0m")
            key = input("  Paste your Gemini API key: ").strip()
            if key:
                set_provider("gemini", PROVIDER_MODELS["gemini"], api_key=key)
                print("  ✅ Gemini API key saved to ~/.shellm/config.yaml\n")
                print("  Run \033[1mshellm\033[0m to start chatting.\n")
            else:
                print("  No key entered — skipping.\n")

    elif provider in ("anthropic", "openai"):
        # API key login — OAuth coming when providers open it
        key_name = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        print(f"\n  {provider.capitalize()} doesn't support browser OAuth for third-party apps yet.")
        print(f"  Get a key at: {'console.anthropic.com' if provider == 'anthropic' else 'platform.openai.com/api-keys'}")
        key = input(f"  Paste your {key_name}: ").strip()
        if key:
            set_provider(provider, PROVIDER_MODELS[provider], api_key=key)
            print(f"  ✅ {provider.capitalize()} key saved to ~/.shellm/config.yaml\n")
        else:
            print("  No key entered — skipping.\n")

    elif provider == "ollama":
        from .providers.ollama import detect_ollama, pick_ollama_model
        ollama = detect_ollama()
        if ollama and ollama["models"]:
            model = pick_ollama_model(ollama["models"])
            set_provider("ollama", model, api_base=ollama["base_url"])
            print(f"  ✅ Ollama configured → {model}")
            print(f"  Available models: {', '.join(ollama['models'])}\n")
        else:
            print("  ❌ Ollama is not running.")
            print("  Install at https://ollama.ai, then run: ollama pull llama3.2\n")

    else:
        print(f"  Unknown provider: {provider}")
        print(f"  Supported: {', '.join(PROVIDER_MODELS)}\n")


def _logout(provider: str) -> None:
    cfg = load_config()
    providers = cfg.get("providers", {})

    if provider not in providers:
        print(f"  Not logged in to {provider}.\n")
        return

    # Revoke Gemini token if possible
    if provider == "gemini":
        token = get_provider_token("gemini")
        if token:
            try:
                gemini_revoke(token)
                print("  Token revoked from Google.")
            except Exception:
                pass

    del providers[provider]
    if cfg.get("default_provider") == provider:
        cfg["default_provider"] = next(iter(providers), None)
    cfg["providers"] = providers
    save_config(cfg)
    print(f"  ✅ Logged out from {provider}.\n")


def _status() -> None:
    from .providers.ollama import detect_ollama
    cfg = load_config()
    providers = cfg.get("providers", {})
    default = cfg.get("default_provider", "none")

    print("\n  \033[1mshellm auth status\033[0m\n")

    # Ollama
    ollama = detect_ollama()
    if ollama and ollama["models"]:
        print(f"  🦙 Ollama         \033[32mrunning\033[0m — {', '.join(ollama['models'])}")
    else:
        print("  🦙 Ollama         \033[90mnot running\033[0m")

    # Configured providers
    for p, pcfg in providers.items():
        marker = " ← default" if p == default else ""
        if pcfg.get("token"):
            print(f"  ✅ {p:<14}\033[32mOAuth\033[0m{marker}")
        elif pcfg.get("api_key"):
            key_preview = pcfg["api_key"][:8] + "..."
            print(f"  🔑 {p:<14}\033[32mAPI key\033[0m ({key_preview}){marker}")
        else:
            print(f"  ⚠  {p:<14}configured but no credentials{marker}")

    if not providers:
        print("  (no providers configured — run \033[1mshellm auth login gemini\033[0m)")

    print()


def _current_provider() -> str:
    cfg = load_config()
    return cfg.get("default_provider") or "gemini"


def _prompt_provider() -> str:
    print("\n  Choose a provider:")
    for i, p in enumerate(PROVIDER_MODELS, 1):
        print(f"    {i}. {p}")
    choice = input("  > ").strip()
    providers = list(PROVIDER_MODELS.keys())
    if choice.isdigit() and 1 <= int(choice) <= len(providers):
        return providers[int(choice) - 1]
    return choice.lower()


def _print_usage() -> None:
    print("""
  Usage:
    shellm auth login [provider]   Log in (gemini, anthropic, openai, ollama)
    shellm auth logout [provider]  Remove saved credentials
    shellm auth status             Show current auth state
""")
