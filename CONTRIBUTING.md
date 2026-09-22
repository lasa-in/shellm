# Contributing to shellm

Thanks for your interest! shellm is community-built — all contributions welcome.

---

## Quickest way to contribute: add a new tool

A tool is a function the AI can call. Each tool has two parts:
1. A **definition** (tells the LLM what the tool does and what arguments it takes)
2. A **handler** (Python function that actually runs it)

### Example — add a `search_web` tool

**1. Create `shellm/tools/search.py`:**

```python
import requests

search_tool = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web and return top results.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
    },
}

def search_web(query: str) -> str:
    # implement with your preferred search API
    return f"Results for: {query}"
```

**2. Register it in `shellm/tools/__init__.py`:**

```python
from .search import search_tool, search_web

ALL_TOOLS = [bash_tool, search_tool] + files_tools

TOOL_HANDLERS = {
    ...
    "search_web": lambda args: search_web(**args),
}
```

That's it — the agent picks it up automatically on the next run.

---

## Development setup

```bash
git clone https://github.com/lasa-in/shellm.git
cd shellm
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

---

## PR checklist

- [ ] New tool has a definition dict + a handler function in its own file
- [ ] Tool is registered in `shellm/tools/__init__.py` and `shellm/agent.py`
- [ ] `README.md` Built-in Tools table updated if adding a new tool
- [ ] No secrets or API keys committed
- [ ] Branch name: `feat/tool-name` or `fix/what-you-fixed`

---

## Reporting bugs / ideas

Open an issue at https://github.com/lasa-in/shellm/issues — describe what you expected vs what happened.
