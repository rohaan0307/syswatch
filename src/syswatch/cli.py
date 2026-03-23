"""CLI entry point using Typer."""

import json
import sys
import time

import typer
from rich.console import Console

from .analyst import get_narration
from .collector import get_snapshot
from .renderer import render

app = typer.Typer(add_completion=False, invoke_without_command=True)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON snapshot"),
):
    """syswatch — real-time system metrics with LLM narration."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        snapshot = get_snapshot()
        if json_output:
            print(json.dumps(snapshot, indent=2))
            return
        narration = get_narration(snapshot, mode="snapshot")
        render(snapshot, narration)
    except KeyboardInterrupt:
        sys.exit(0)


@app.command()
def watch(
    interval: int = typer.Option(10, "--interval", "-i", help="Seconds between refreshes"),
):
    """Continuously monitor system metrics."""
    try:
        while True:
            console.clear()
            snapshot = get_snapshot()
            narration = get_narration(snapshot, mode="snapshot")
            render(snapshot, narration)
            time.sleep(interval)
    except KeyboardInterrupt:
        sys.exit(0)


@app.command()
def diagnose():
    """Take two snapshots and provide a diagnostic verdict."""
    try:
        console.print("[bold]Taking first snapshot...[/]")
        snap1 = get_snapshot()
        console.print("[bold]Waiting 5 seconds...[/]")
        time.sleep(5)
        console.print("[bold]Taking second snapshot...[/]")
        snap2 = get_snapshot()
        combined = {"snapshot_1": snap1, "snapshot_2": snap2}
        narration = get_narration(combined, mode="diagnose")
        render(snap2, narration)
    except KeyboardInterrupt:
        sys.exit(0)
