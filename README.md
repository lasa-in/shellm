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

```bash
pip install shellm
export OPENAI_API_KEY=sk-...   # or ANTHROPIC_API_KEY / GEMINI_API_KEY
shellm
```

### Non-interactive (pipe-friendly)

```bash
shellm "show me disk usage for the current directory"
shellm --model claude-3-5-sonnet-20241022 "find all TODO comments in this repo"
```

### Use a local model (no API key needed)

```bash
# Install Ollama from https://ollama.ai, then:
ollama pull llama3
shellm --model ollama/llama3
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

## Installation from source

```bash
git clone https://github.com/lasa-in/shellm.git
cd shellm
pip install -e .
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
