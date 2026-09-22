"""shellm — entry point for the CLI."""

import sys
import os
import argparse
from .agent import run_agent
from .providers import resolve_model

DEFAULT_MODEL = os.environ.get("SHELLM_MODEL", None)  # None = auto-detect

HELP_TEXT = """
  \033[1mshellm commands\033[0m

  Just type naturally — shellm has access to your shell and files.

  \033[33mBuilt-in commands:\033[0m
    help                    Show this help
    exit / quit             Leave shellm
    auth status             Show configured providers
    auth login [provider]   Log in (gemini, anthropic, openai, ollama)
    auth logout [provider]  Remove saved credentials

  \033[33mAvailable tools the AI can use:\033[0m
    bash          Run any shell command
    read_file     Read a file's contents
    write_file    Write or create a file
    list_dir      List files in a directory

  \033[33mExamples:\033[0m
    shellm> list all python files changed in the last 7 days
    shellm> show disk usage for this directory
    shellm> read my ~/.zshrc and suggest improvements
    shellm> write a hello world script to /tmp/hello.py

  \033[33mModel flags:\033[0m
    shellm --model ollama/llama3.1:8b "your prompt"
    shellm --model claude-sonnet-4-5 "your prompt"
"""

BANNER = """\033[36m
  ███████╗██╗  ██╗███████╗██╗     ██╗     ███╗   ███╗
  ██╔════╝██║  ██║██╔════╝██║     ██║     ████╗ ████║
  ███████╗███████║█████╗  ██║     ██║     ██╔████╔██║
  ╚════██║██╔══██║██╔══╝  ██║     ██║     ██║╚██╔╝██║
  ███████║██║  ██║███████╗███████╗███████╗██║ ╚═╝ ██║
  ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝
\033[0m  Terminal AI assistant — model-agnostic, open-source
  Type \033[33mexit\033[0m or \033[33mquit\033[0m to leave  |  \033[33mshellm auth status\033[0m to see providers
"""


def parse_args():
    parser = argparse.ArgumentParser(
        prog="shellm",
        description="Model-agnostic terminal AI assistant with shell access.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Single prompt to run non-interactively (optional).",
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help="LiteLLM model string (overrides auto-detect). "
             "Examples: gpt-4o, claude-sonnet-4-5, gemini/gemini-1.5-flash, ollama/llama3",
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Print version and exit.",
    )
    # auth subcommand: shellm auth login gemini
    parser.add_argument(
        "auth_args",
        nargs=argparse.REMAINDER,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.version:
        from . import __version__
        print(f"shellm {__version__}")
        sys.exit(0)

    # ── `shellm auth ...` subcommand ─────────────────────────────────────────
    # Handles: shellm auth login gemini / shellm auth status / shellm auth logout
    all_positional = ([args.prompt] if args.prompt else []) + list(args.auth_args or [])
    if all_positional and all_positional[0] == "auth":
        from .auth_cmd import cmd_auth
        cmd_auth(all_positional[1:])
        return

    # ── Resolve model (auto-detect Ollama → config → env vars) ──────────────
    try:
        model, extra_kwargs = resolve_model(args.model)
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    history = []

    # ── Non-interactive: single prompt passed as argument ────────────────────
    if args.prompt and args.prompt != "auth":
        try:
            response, _ = run_agent(args.prompt, model, history, extra_kwargs)
            print(response)
        except Exception as e:
            print(f"\033[31m[error]\033[0m {e}")
            sys.exit(1)
        return

    # ── Interactive REPL ─────────────────────────────────────────────────────
    print(BANNER)
    print(f"  Model: \033[32m{model}\033[0m\n")

    while True:
        try:
            user_input = input("\033[1mshellm>\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Bye!")
            break

        if user_input.lower() in ("help", "?", "--help", "-h"):
            print(HELP_TEXT)
            continue

        # Inline auth command inside REPL: `auth status`, `auth login gemini`
        if user_input.startswith("auth ") or user_input == "auth":
            from .auth_cmd import cmd_auth
            cmd_auth(user_input.split()[1:])
            continue

        try:
            response, history = run_agent(user_input, model, history, extra_kwargs)
            print(f"\n{response}\n")
        except Exception as e:
            print(f"\n\033[31m[error]\033[0m {e}\n")


if __name__ == "__main__":
    main()
