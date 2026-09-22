"""File tools — read, write, and list files on the local machine."""

import os

# Tool definitions sent to the LLM
files_tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file, creating it if it does not exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path."},
                    "content": {"type": "string", "description": "Content to write."},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and directories at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path (default: current directory).",
                        "default": ".",
                    },
                },
                "required": [],
            },
        },
    },
]


def read_file(path: str) -> str:
    try:
        with open(os.path.expanduser(path), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[error] File not found: {path}"
    except Exception as e:
        return f"[error] {e}"


def write_file(path: str, content: str) -> str:
    try:
        expanded = os.path.expanduser(path)
        os.makedirs(os.path.dirname(expanded) or ".", exist_ok=True)
        with open(expanded, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"[error] {e}"


def list_dir(path: str = ".") -> str:
    try:
        entries = os.listdir(os.path.expanduser(path))
        entries.sort()
        lines = []
        for entry in entries:
            full = os.path.join(path, entry)
            prefix = "📁" if os.path.isdir(full) else "📄"
            lines.append(f"{prefix} {entry}")
        return "\n".join(lines) if lines else "(empty directory)"
    except FileNotFoundError:
        return f"[error] Directory not found: {path}"
    except Exception as e:
        return f"[error] {e}"
