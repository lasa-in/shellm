"""bash tool — executes shell commands on the local machine.

Platform behaviour:
  macOS / Linux  → runs via bash (shell=True)
  Windows        → runs via PowerShell (powershell -Command ...)

The LLM is told which shell is active so it generates correct syntax.
"""

import sys
import subprocess

_PLATFORM = sys.platform  # "darwin", "linux", "win32"

def _platform_label() -> str:
    if _PLATFORM == "win32":
        return "PowerShell (Windows)"
    if _PLATFORM == "darwin":
        return "bash (macOS)"
    return "bash (Linux)"


# Tool definition sent to the LLM
bash_tool = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": (
            f"Run a shell command on the user's local machine ({_platform_label()}) "
            "and return its output. "
            "On macOS/Linux use bash syntax; on Windows use PowerShell syntax. "
            "Use for listing files, running scripts, git operations, package installs, "
            "and any other terminal task. Prefer non-destructive commands; confirm with "
            "the user before deleting files or making irreversible changes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": (
                        "The shell command to execute. "
                        "Use bash syntax on macOS/Linux, PowerShell syntax on Windows."
                    ),
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


def run_bash(command: str, timeout=30) -> str:
    """Execute a shell command and return combined stdout + stderr.

    Routes to the correct shell for the current OS:
      - Windows  → powershell -Command <command>
      - Mac/Linux → shell=True (bash)
    """
    try:
        timeout = int(timeout)  # model may pass "30" as string
        if _PLATFORM == "win32":
            proc_args = ["powershell", "-NoProfile", "-NonInteractive", "-Command", command]
            result = subprocess.run(
                proc_args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        else:
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
    except FileNotFoundError:
        # PowerShell not found on this Windows install
        return "[error] PowerShell not found — is it installed and on PATH?"
    except Exception as e:
        return f"[error] {e}"
