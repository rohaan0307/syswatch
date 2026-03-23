"""LLM narration with swappable backends."""

import json

import httpx

from . import config

SNAPSHOT_SYSTEM = (
    "You are syswatch, a concise system-health narrator. "
    "Given JSON system metrics, reply with exactly three sections:\n"
    "SUMMARY — one paragraph overview\n"
    "FLAGS — bullet list of any metrics above warning thresholds\n"
    "SUGGESTIONS — bullet list of actionable tips (or 'None' if healthy)"
)

DIAGNOSE_SYSTEM = (
    "You are syswatch, a system diagnostician. "
    "You receive two snapshots taken seconds apart. "
    "Reply with:\n"
    "VERDICT — one of HEALTHY / WATCH / INVESTIGATE\n"
    "DETAILS — paragraph explaining the verdict\n"
    "ACTIONS — bullet list of recommended actions"
)


def _prompt(snapshot, mode: str) -> tuple[str, str]:
    system = SNAPSHOT_SYSTEM if mode == "snapshot" else DIAGNOSE_SYSTEM
    user = json.dumps(snapshot, indent=2)
    return system, user


def _call_anthropic(system: str, user: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=config.get_api_key())
    resp = client.messages.create(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


def _call_openai_compat(system: str, user: str) -> str:
    """Generic OpenAI-compatible endpoint (ollama, groq, openrouter)."""
    base_urls = {
        "ollama": config.BASE_URL or "http://localhost:11434",
        "groq": "https://api.groq.com/openai",
        "openrouter": "https://openrouter.ai/api",
    }
    base = base_urls.get(config.BACKEND, config.BASE_URL or "")
    url = f"{base}/v1/chat/completions"

    headers = {"Content-Type": "application/json"}
    api_key = config.get_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body = {
        "model": config.MODEL,
        "max_tokens": config.MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    resp = httpx.post(url, json=body, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def get_narration(snapshot, mode: str = "snapshot") -> str:
    """Return LLM narration for the given snapshot(s)."""
    system, user = _prompt(snapshot, mode)

    if config.BACKEND == "anthropic":
        return _call_anthropic(system, user)
    elif config.BACKEND in ("ollama", "groq", "openrouter"):
        return _call_openai_compat(system, user)
    else:
        raise ValueError(f"Unknown backend: {config.BACKEND!r}")
