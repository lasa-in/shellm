"""Agent loop — sends messages to the LLM and handles tool calls."""

import json
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
You can run shell commands, read and write files, and help with coding, DevOps, and everyday terminal tasks.
Always show the command you're about to run before executing it.
Ask for confirmation before deleting files or making irreversible changes."""


def run_agent(prompt: str, model: str, history: list) -> tuple[str, list]:
    """
    Run one turn of the agent loop.
    Returns the final text response and updated history.
    """
    history.append({"role": "user", "content": prompt})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    while True:
        response = litellm.completion(
            model=model,
            messages=messages,
            tools=ALL_TOOLS,
            tool_choice="auto",
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

            handler = TOOL_HANDLERS.get(name)
            if handler:
                result = handler(args)
            else:
                result = f"[error] Unknown tool: {name}"

            print(f"   → {result[:200]}{'...' if len(result) > 200 else ''}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
