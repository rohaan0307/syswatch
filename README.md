# syswatch

A pip-installable CLI tool that collects real-time system metrics and uses an LLM to narrate diagnostics in plain English.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and set your `ANTHROPIC_API_KEY`:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

## Usage

```bash
# Default: snapshot + LLM narration
syswatch

# Raw JSON snapshot (no LLM call)
syswatch --json

# Continuous monitoring (default 10s interval)
syswatch watch
syswatch watch --interval 3
syswatch watch -i 5

# Diagnostic mode: two snapshots 5s apart with verdict
syswatch diagnose
```

## Backends

| Backend | `SYSWATCH_BACKEND` | Cost | Setup |
|---|---|---|---|
| Anthropic | `anthropic` (default) | Paid | Set `ANTHROPIC_API_KEY` |
| Ollama | `ollama` | Free | Install Ollama, pull a model |
| Groq | `groq` | Free tier | Set `ANTHROPIC_API_KEY` to your Groq key |
| OpenRouter | `openrouter` | Varies | Set `ANTHROPIC_API_KEY` to your OpenRouter key |

### Ollama Quickstart

```bash
# Install Ollama (macOS)
brew install ollama

# Pull and run a model
ollama run llama3

# Configure syswatch
export SYSWATCH_BACKEND=ollama
export SYSWATCH_MODEL=llama3
export SYSWATCH_BASE_URL=http://localhost:11434

syswatch
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SYSWATCH_BACKEND` | `anthropic` | Backend to use |
| `SYSWATCH_MODEL` | `claude-opus-4-5` | Model string for the backend |
| `SYSWATCH_BASE_URL` | `None` | Custom base URL (for Ollama) |
| `ANTHROPIC_API_KEY` | — | API key for the active backend |
