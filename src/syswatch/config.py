"""Configuration — loads env vars and exposes module-level settings."""

import os
from dotenv import load_dotenv

load_dotenv()

BACKEND: str = os.getenv("SYSWATCH_BACKEND", "anthropic")
MODEL: str = os.getenv("SYSWATCH_MODEL", "claude-opus-4-5")
BASE_URL: str | None = os.getenv("SYSWATCH_BASE_URL")
MAX_TOKENS: int = int(os.getenv("SYSWATCH_MAX_TOKENS", "1024"))

THRESHOLDS: dict = {
    "cpu_warn": 60,
    "cpu_crit": 85,
    "mem_warn": 70,
    "mem_crit": 90,
    "disk_warn": 75,
    "disk_crit": 90,
    "swap_warn": 50,
}


def get_api_key() -> str:
    """Return the API key, raising if the anthropic backend is active and key is missing."""
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if BACKEND == "anthropic" and not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. "
            "Either set it in your .env file or switch to a free backend:\n"
            "  export SYSWATCH_BACKEND=ollama\n"
            "  export SYSWATCH_MODEL=llama3\n"
            "  export SYSWATCH_BASE_URL=http://localhost:11434"
        )
    return key
