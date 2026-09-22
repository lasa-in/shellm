"""Agent loop — sends messages to the LLM and handles tool calls."""

import json
from typing import Optional
import litellm
from .tools import ALL_TOOLS, run_bash, read_file, write_file, list_dir

# Map tool names → handler functions
TOOL_HANDLERS = {
    "bash": lambda args: run_bash(**args),
    "read_file": lambda args: read_file(**args),
    "write_file": lambda args: write_file(**args),
    "list_dir": lambda args: list_dir(**args),
}

SYSTEM_PROMPT = """You are shellm, a terminal AI assistant with access to the user's local machine.

You have exactly four tools available — use ONLY these, nothing else:
  - bash(command, timeout)     Run a shell command
  - read_file(path)            Read a file's contents
  - write_file(path, content)  Write or overwrite a file
  - list_dir(path)             List files in a directory

Rules:
- For questions that don't need file access or shell commands, answer directly in text — do NOT call a tool.
- Never invent tool names that aren't in the list above (e.g. no 'help', 'answer', 'search').
- Always show intent before running a destructive command; ask before deleting files."""

MAX_TOOL_ITERATIONS = 15  # guard against runaway tool loops with smaller models
MAX_CONSECUTIVE_UNKNOWN = 3  # stop if model keeps calling nonexistent tools


def run_agent(prompt: str, model: str, history: list, extra_kwargs: Optional[dict] = None) -> tuple:
    """
    Run one turn of the agent loop.
    Returns the final text response and updated history.
    """
    history.append({"role": "user", "content": prompt})
    extra_kwargs = extra_kwargs or {}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    iterations = 0
    consecutive_unknown = 0
    last_tool_sig = None   # detect same tool+args repeated back-to-back
    repeated_count = 0

    while True:
        if iterations >= MAX_TOOL_ITERATIONS:
            text = "[shellm] Reached max tool iterations — stopping to prevent infinite loop."
            history.append({"role": "assistant", "content": text})
            return text, history
        iterations += 1

        response = litellm.completion(
            model=model,
            messages=messages,
            tools=ALL_TOOLS,
            tool_choice="auto",
            **extra_kwargs,
        )

        message = response.choices[0].message

        # No tool calls — we have a final answer
        if not message.tool_calls:
            text = message.content or ""
            history.append({"role": "assistant", "content": text})
            return text, history

        # Append assistant message with tool calls
        messages.append(message)

        # Execute each tool call and append results
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"\n⚙  Running tool: \033[33m{name}\033[0m({json.dumps(args, separators=(',', ':'))})")

            # Detect repeated identical tool calls (model stuck in a loop)
            sig = f"{name}:{json.dumps(args, sort_keys=True)}"
            if sig == last_tool_sig:
                repeated_count += 1
            else:
                repeated_count = 0
            last_tool_sig = sig
            if repeated_count >= 2:
                text = "I seem to be going in circles. Please try rephrasing, or use a larger model (`ollama pull llama3.1:8b`)."
                history.append({"role": "assistant", "content": text})
                return text, history

            handler = TOOL_HANDLERS.get(name)
            if handler:
                consecutive_unknown = 0
                result = handler(args)
            else:
                consecutive_unknown += 1
                result = (
                    f"[error] Unknown tool '{name}'. "
                    f"Available tools: bash, read_file, write_file, list_dir. "
                    f"Answer in plain text if no tool is needed."
                )
                if consecutive_unknown >= MAX_CONSECUTIVE_UNKNOWN:
                    text = f"I'm unable to answer using the available tools. Please try rephrasing, or run `ollama pull llama3.1:8b` for a smarter local model."
                    history.append({"role": "assistant", "content": text})
                    return text, history

            print(f"   → {result[:200]}{'...' if len(result) > 200 else ''}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
