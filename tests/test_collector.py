"""Tests for the system metrics collector."""

from syswatch.collector import get_snapshot


def test_snapshot_keys():
    """Assert all top-level keys are present."""
    snapshot = get_snapshot()
    expected_keys = {
        "cpu", "memory", "disk", "processes",
        "network", "uptime_hrs", "platform", "timestamp",
    }
    assert expected_keys == set(snapshot.keys())


def test_snapshot_types():
    """Assert correct types for key metrics."""
    snapshot = get_snapshot()
    assert isinstance(snapshot["cpu"]["percent"], float)
    assert isinstance(snapshot["processes"]["total"], int)
    assert isinstance(snapshot["memory"]["total_gb"], float)
    assert isinstance(snapshot["disk"]["partitions"], list)
    assert isinstance(snapshot["cpu"]["per_core"], list)
    assert isinstance(snapshot["cpu"]["load_avg"], list)
