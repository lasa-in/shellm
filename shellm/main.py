"""shellm — entry point for the CLI."""

import sys
import os
import argparse
from .agent import run_agent

DEFAULT_MODEL = os.environ.get("SHELLM_MODEL", "gpt-4o")

BANNER = """\033[36m
  ███████╗██╗  ██╗███████╗██╗     ██╗     ███╗   ███╗
  ██╔════╝██║  ██║██╔════╝██║     ██║     ████╗ ████║
  ███████╗███████║█████╗  ██║     ██║     ██╔████╔██║
  ╚════██║██╔══██║██╔══╝  ██║     ██║     ██║╚██╔╝██║
  ███████║██║  ██║███████╗███████╗███████╗██║ ╚═╝ ██║
  ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝
\033[0m  Terminal AI assistant — model-agnostic, open-source
  Type \033[33mexit\033[0m or \033[33mquit\033[0m to leave | \033[33mCtrl+C\033[0m to interrupt
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
        help=f"LiteLLM model string (default: {DEFAULT_MODEL}). "
             "Examples: gpt-4o, claude-3-5-sonnet-20241022, gemini/gemini-1.5-pro, ollama/llama3",
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Print version and exit.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.version:
        from . import __version__
        print(f"shellm {__version__}")
        sys.exit(0)

    model = args.model
    history = []

    # Non-interactive: single prompt passed as argument
    if args.prompt:
        response, _ = run_agent(args.prompt, model, history)
        print(response)
        return

    # Interactive REPL
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

        try:
            response, history = run_agent(user_input, model, history)
            print(f"\n{response}\n")
        except Exception as e:
            print(f"\n\033[31m[error]\033[0m {e}\n")


if __name__ == "__main__":
    main()
