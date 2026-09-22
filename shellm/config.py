"""shellm config — read/write ~/.shellm/config.yaml."""

import os
import yaml  # via litellm's dep tree; or add pyyaml explicitly

CONFIG_DIR  = os.path.expanduser("~/.shellm")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f) or {}


def save_config(cfg: dict) -> None:
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)
    os.chmod(CONFIG_FILE, 0o600)  # user-only read/write


def set_provider(provider: str, model: str, api_key: str | None = None,
                 api_base: str | None = None, token: dict | None = None) -> None:
    cfg = load_config()
    cfg.setdefault("providers", {})[provider] = {
        k: v for k, v in {
            "model": model,
            "api_key": api_key,
            "api_base": api_base,
            "token": token,
        }.items() if v is not None
    }
    cfg["default_provider"] = provider
    save_config(cfg)


def get_provider_token(provider: str) -> dict | None:
    cfg = load_config()
    return cfg.get("providers", {}).get(provider, {}).get("token")


def update_provider_token(provider: str, token: dict) -> None:
    cfg = load_config()
    cfg.setdefault("providers", {}).setdefault(provider, {})["token"] = token
    save_config(cfg)
