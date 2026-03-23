# syswatch — Product Requirements Document

## Overview
A pip-installable CLI tool (`syswatch`) that collects real-time system metrics and uses an LLM
to narrate diagnostics in plain English. The LLM backend is swappable via environment variables
so the tool works free-of-cost during development (Ollama, Groq) and uses the full Claude API
for production/demo use.

---

## Success Criteria
The project is complete when all of the following pass without errors:
```bash
pip install -e .
syswatch
syswatch --json | python3 -m json.tool
syswatch watch -i 3       # run 2 cycles, Ctrl+C
syswatch diagnose
pytest tests/ -v
```

---

## Stories

### STORY-001: Project Scaffold
**Status:** TODO
**Acceptance:**
- [ ] `pyproject.toml` exists with `syswatch = "syswatch.cli:app"` entry point
- [ ] All five module files exist: `cli.py`, `collector.py`, `analyst.py`, `renderer.py`, `config.py`
- [ ] `.env.example` exists with all backend variants documented
- [ ] `.gitignore` includes `.env`, `.venv/`, `__pycache__/`, `*.egg-info/`, `dist/`
- [ ] `pip install -e .` succeeds

---

### STORY-002: config.py — Model + Backend Config
**Status:** TODO
**Acceptance:**
- [ ] Loads `ANTHROPIC_API_KEY` from `.env` via python-dotenv
- [ ] Raises `EnvironmentError` with helpful message if key missing and backend is `anthropic`
- [ ] Exposes `BACKEND`, `MODEL`, `BASE_URL`, `MAX_TOKENS`, `THRESHOLDS` as module-level vars
- [ ] `BACKEND` defaults to `"anthropic"`, overridable via `SYSWATCH_BACKEND` env var
- [ ] `MODEL` defaults to `"claude-opus-4-5"`, overridable via `SYSWATCH_MODEL` env var
- [ ] `THRESHOLDS` dict has keys: `cpu_warn`, `cpu_crit`, `mem_warn`, `mem_crit`, `disk_warn`, `disk_crit`, `swap_warn`

---

### STORY-003: collector.py — System Metrics
**Status:** TODO
**Acceptance:**
- [ ] `get_snapshot()` returns a dict with all top-level keys: `cpu`, `memory`, `disk`, `processes`, `network`, `uptime_hrs`, `platform`, `timestamp`
- [ ] `cpu` includes: `percent`, `per_core`, `freq_mhz`, `load_avg`
- [ ] `memory` includes: `total_gb`, `used_gb`, `available_gb`, `percent`, `swap_used_gb`, `swap_percent`
- [ ] `disk.partitions` is a list of dicts with `mount`, `total_gb`, `used_gb`, `percent`
- [ ] `disk.io` has `read_mb` and `write_mb`
- [ ] `processes.top_cpu` and `processes.top_mem` are lists of 5 dicts each
- [ ] All float values are rounded to 2 decimal places
- [ ] No exceptions on macOS or Linux

---

### STORY-004: analyst.py — Multi-Backend LLM Narration
**Status:** TODO
**Acceptance:**
- [ ] `get_narration(snapshot, mode="snapshot")` returns a non-empty string
- [ ] Supports `BACKEND` values: `anthropic`, `ollama`, `openrouter`, `groq`
- [ ] `anthropic` backend uses the `anthropic` Python SDK
- [ ] `ollama`, `openrouter`, `groq` backends use `httpx` (no extra SDK dependency)
- [ ] `mode="snapshot"` uses the snapshot system prompt (SUMMARY / FLAGS / SUGGESTIONS)
- [ ] `mode="diagnose"` uses the diagnose system prompt (HEALTHY / WATCH / INVESTIGATE verdict)
- [ ] Raises `ValueError` for unknown `BACKEND` value
- [ ] Does not hardcode any API keys

---

### STORY-005: renderer.py — Rich Terminal Output
**Status:** TODO
**Acceptance:**
- [ ] `render(snapshot, narration)` prints to terminal without errors
- [ ] Shows CPU, MEM, DISK as progress bars inside a Panel
- [ ] Progress bar colors: green if below warn threshold, yellow if warn, red if crit
- [ ] Shows top 5 CPU and top 5 MEM processes in a Table
- [ ] Shows LLM narration in a separate Panel labeled "Claude's Read"
- [ ] Uses `rich.panel`, `rich.table`, `rich.progress`, `rich.console`

---

### STORY-006: cli.py — Commands
**Status:** TODO
**Acceptance:**
- [ ] `syswatch` (default) → calls `get_snapshot()` → `get_narration()` → `render()`
- [ ] `syswatch --json` → calls `get_snapshot()` only, prints `json.dumps(snapshot, indent=2)`, no LLM call
- [ ] `syswatch watch` → loops: clear console, snapshot, narrate, render, sleep N seconds
- [ ] `syswatch watch --interval N` / `-i N` → configurable interval, default 10
- [ ] `syswatch diagnose` → takes two snapshots 5s apart, passes both to `get_narration(mode="diagnose")`, renders result
- [ ] All commands handle `KeyboardInterrupt` cleanly (no stack trace on Ctrl+C)

---

### STORY-007: Tests
**Status:** TODO
**Acceptance:**
- [ ] `tests/test_collector.py` — `test_snapshot_keys()` asserts all top-level keys present
- [ ] `tests/test_collector.py` — `test_snapshot_types()` asserts `cpu.percent` is float, `processes.total` is int
- [ ] `tests/test_analyst.py` — mocks the backend call, asserts `get_narration()` returns a non-empty string
- [ ] `pytest tests/ -v` passes with 0 failures

---

### STORY-008: README.md
**Status:** TODO
**Acceptance:**
- [ ] Install section: `pip install -e .`
- [ ] Setup section: explains `.env.example` → `.env`, `ANTHROPIC_API_KEY`
- [ ] Usage section: all four commands with flags documented
- [ ] Backend section: table of all four backends with cost and setup instructions
- [ ] Ollama quickstart: `ollama run llama3` + env vars to set

---

## Non-Goals
- No web UI or HTTP server
- No persistent storage or logging to disk
- No alerting / notifications
- No Windows-specific support (psutil works but not tested)

---

## Backend Environment Variables Reference
| Variable | Default | Options |
|---|---|---|
| `SYSWATCH_BACKEND` | `anthropic` | `anthropic`, `ollama`, `groq`, `openrouter` |
| `SYSWATCH_MODEL` | `claude-opus-4-5` | any valid model string for the backend |
| `SYSWATCH_BASE_URL` | `None` | custom base URL (mainly for Ollama: `http://localhost:11434`) |
| `ANTHROPIC_API_KEY` | — | API key for whichever backend is active |

---

## Ralph Loop Phases

### Phase 1 — Core Pipeline
Stories: STORY-001 through STORY-005
Completion promise: `<promise>SESSION1_DONE</promise>`
Verification: `pip install -e . && syswatch` runs end-to-end

### Phase 2 — Watch + Diagnose + Polish
Stories: STORY-006 through STORY-008
Completion promise: `<promise>SESSION2_DONE</promise>`
Verification: all four commands work + `pytest tests/ -v` passes