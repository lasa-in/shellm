# shellm

> Open-source terminal AI assistant with real shell access. Works with OpenAI, Anthropic, Gemini, and local models via Ollama. Extensible, model-agnostic, community-built.

```
shellm> list all python files changed in the last 7 days
⚙  Running tool: bash({"command":"find . -name '*.py' -mtime -7"})
   → ./shellm/agent.py
     ./shellm/main.py

Here are the Python files modified in the last 7 days:
- shellm/agent.py
- shellm/main.py
```

---

## Features

- 🔧 **Real shell access** — runs commands on your machine, reads and writes files
- 🤖 **Model-agnostic** — OpenAI, Anthropic, Gemini, or local Ollama models
- 🔁 **Agentic tool loop** — multi-step reasoning: think → tool → observe → answer
- 💬 **Interactive REPL** or single-shot prompt mode
- 🧩 **Extensible** — add new tools in one file (see [Contributing](#contributing))

---

## Quickstart

### Option 1 — pipx (recommended, handles PATH automatically)

```bash
pipx install git+https://github.com/lasa-in/shellm.git
shellm
```

> Don't have pipx? `brew install pipx && pipx ensurepath` (Mac) or `pip install pipx` (Linux/Windows).

### Option 2 — venv

```bash
python3 -m venv ~/shellm-env
~/shellm-env/bin/pip install git+https://github.com/lasa-in/shellm.git

# Make `shellm` available everywhere (Mac/Linux):
ln -sf ~/shellm-env/bin/shellm /usr/local/bin/shellm
```

### Zero-config with Ollama (free, no API key)

```bash
# 1. Install Ollama: https://ollama.ai
ollama pull llama3.1:8b   # 8B model handles tool-calling well
# 2. Start Ollama (it runs as a background service)
# 3. Just run shellm — it auto-detects Ollama:
shellm
#   🦙 Ollama detected — using ollama/llama3.1:8b (free, local)
```

### With a cloud API key

```bash
export OPENAI_API_KEY=sk-...        # or ANTHROPIC_API_KEY / GEMINI_API_KEY
shellm
```

### Non-interactive (pipe-friendly)

```bash
shellm "show me disk usage for the current directory"
shellm --model claude-sonnet-4-5 "find all TODO comments in this repo"
```

---

## Supported Models

shellm uses [LiteLLM](https://github.com/BerriAI/litellm) — any model it supports works here.

| Provider | Example `--model` value |
|---|---|
| OpenAI | `gpt-4o` (default), `gpt-4o-mini` |
| Anthropic | `claude-3-5-sonnet-20241022` |
| Google | `gemini/gemini-1.5-pro` |
| Ollama (local) | `ollama/llama3`, `ollama/mistral` |
| AWS Bedrock | `bedrock/anthropic.claude-3-sonnet` |

Set your default model via environment variable:

```bash
export SHELLM_MODEL=claude-3-5-sonnet-20241022
```

---

## Install from source (for contributors)

```bash
git clone https://github.com/lasa-in/shellm.git
cd shellm
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Built-in Tools

| Tool | Description |
|---|---|
| `bash` | Run any shell command |
| `read_file` | Read a file's contents |
| `write_file` | Write or create a file |
| `list_dir` | List files in a directory |

---

## Contributing

Contributions are very welcome — especially new tools!

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a tool, run tests, and open a PR.

---

## License

MIT — see [LICENSE](LICENSE).
