"""Tests for the LLM analyst module."""

import sys
from unittest.mock import patch, MagicMock

from syswatch.analyst import get_narration


def test_get_narration_anthropic():
    """Mock the anthropic backend and assert narration returns a non-empty string."""
    fake_snapshot = {"cpu": {"percent": 50.0}, "memory": {"percent": 60.0}}

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="SUMMARY\nSystem is healthy.\nFLAGS\nNone\nSUGGESTIONS\nNone")]

    mock_anthropic_module = MagicMock()
    mock_client = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client
    mock_client.messages.create.return_value = mock_response

    with patch("syswatch.analyst.config") as mock_config:
        mock_config.BACKEND = "anthropic"
        mock_config.MODEL = "claude-opus-4-5"
        mock_config.MAX_TOKENS = 1024
        mock_config.get_api_key.return_value = "sk-test-key"

        with patch.dict(sys.modules, {"anthropic": mock_anthropic_module}):
            result = get_narration(fake_snapshot, mode="snapshot")

    assert isinstance(result, str)
    assert len(result) > 0


def test_get_narration_unknown_backend():
    """Assert ValueError for unknown backend."""
    import pytest

    with patch("syswatch.analyst.config") as mock_config:
        mock_config.BACKEND = "unknown_backend"

        with pytest.raises(ValueError, match="Unknown backend"):
            get_narration({"cpu": {"percent": 50.0}})
