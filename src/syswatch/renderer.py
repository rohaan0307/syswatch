"""Rich terminal output for syswatch."""

from rich.console import Console
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from . import config

console = Console()


def _bar_color(value: float, warn: int, crit: int) -> str:
    if value >= crit:
        return "red"
    if value >= warn:
        return "yellow"
    return "green"


def _metric_bar(label: str, value: float, warn: int, crit: int) -> Text:
    color = _bar_color(value, warn, crit)
    filled = int(value / 100 * 30)
    bar = "█" * filled + "░" * (30 - filled)
    return Text.from_markup(f"{label:>6s} [{color}]{bar}[/] {value:5.1f}%")


def _process_table(title: str, procs: list[dict]) -> Table:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("PID", justify="right", width=8)
    table.add_column("Name", width=24)
    table.add_column("CPU%", justify="right", width=8)
    table.add_column("MEM%", justify="right", width=8)
    for p in procs:
        table.add_row(
            str(p["pid"]),
            p["name"][:24],
            f"{p['cpu_percent']:.1f}",
            f"{p['memory_percent']:.1f}",
        )
    return table


def render(snapshot: dict, narration: str) -> None:
    """Print formatted system metrics and LLM narration to the terminal."""
    th = config.THRESHOLDS
    cpu_pct = snapshot["cpu"]["percent"]
    mem_pct = snapshot["memory"]["percent"]

    lines = [
        _metric_bar("CPU", cpu_pct, th["cpu_warn"], th["cpu_crit"]),
        _metric_bar("MEM", mem_pct, th["mem_warn"], th["mem_crit"]),
    ]

    for part in snapshot["disk"]["partitions"]:
        label = f"DISK({part['mount']})"
        if len(label) > 14:
            label = f"DISK(..{part['mount'][-6:]})"
        lines.append(
            _metric_bar(label, part["percent"], th["disk_warn"], th["disk_crit"])
        )

    bar_text = Text("\n").join(lines)
    console.print(Panel(bar_text, title="System Metrics", border_style="blue"))

    # Process tables
    cpu_table = _process_table("Top 5 by CPU", snapshot["processes"]["top_cpu"])
    mem_table = _process_table("Top 5 by MEM", snapshot["processes"]["top_mem"])
    console.print(cpu_table)
    console.print(mem_table)

    # LLM narration
    console.print(Panel(narration, title="Claude's Read", border_style="magenta"))
