"""bash tool — executes shell commands on the local machine."""

import subprocess

# Tool definition sent to the LLM
bash_tool = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": (
            "Run a shell command on the user's local machine and return its output. "
            "Use for listing files, running scripts, git operations, package installs, "
            "and any other terminal task. Prefer non-destructive commands; confirm with "
            "the user before deleting files or making irreversible changes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Max seconds to wait (default 30).",
                    "default": 30,
                },
            },
            "required": ["command"],
        },
    },
}


def run_bash(command: str, timeout: int = 30) -> str:
    """Execute a shell command and return combined stdout + stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"[error] Command timed out after {timeout}s"
    except Exception as e:
        return f"[error] {e}"
