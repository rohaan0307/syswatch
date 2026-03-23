"""System metrics collector using psutil."""

import platform
import time
from datetime import datetime, timezone

import psutil


def _round(val: float) -> float:
    return round(val, 2)


def _bytes_to_gb(b: int) -> float:
    return _round(b / (1024 ** 3))


def _bytes_to_mb(b: int) -> float:
    return _round(b / (1024 ** 2))


def _top_procs(key: str, n: int = 5) -> list[dict]:
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            procs.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": _round(info["cpu_percent"] or 0.0),
                "memory_percent": _round(info["memory_percent"] or 0.0),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda p: p[key], reverse=True)
    return procs[:n]


def get_snapshot() -> dict:
    """Collect a full system metrics snapshot."""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.5)
    per_core = psutil.cpu_percent(interval=0, percpu=True)
    freq = psutil.cpu_freq()
    load_avg = list(psutil.getloadavg()) if hasattr(psutil, "getloadavg") else [0.0, 0.0, 0.0]

    # Memory
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disk
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "mount": part.mountpoint,
                "total_gb": _bytes_to_gb(usage.total),
                "used_gb": _bytes_to_gb(usage.used),
                "percent": _round(usage.percent),
            })
        except (PermissionError, OSError):
            continue

    disk_io = psutil.disk_io_counters()
    disk_io_dict = {
        "read_mb": _bytes_to_mb(disk_io.read_bytes) if disk_io else 0.0,
        "write_mb": _bytes_to_mb(disk_io.write_bytes) if disk_io else 0.0,
    }

    # Network
    net = psutil.net_io_counters()

    # Processes
    top_cpu = _top_procs("cpu_percent")
    top_mem = _top_procs("memory_percent")

    return {
        "cpu": {
            "percent": _round(cpu_percent),
            "per_core": [_round(c) for c in per_core],
            "freq_mhz": _round(freq.current) if freq else 0.0,
            "load_avg": [_round(la) for la in load_avg],
        },
        "memory": {
            "total_gb": _bytes_to_gb(mem.total),
            "used_gb": _bytes_to_gb(mem.used),
            "available_gb": _bytes_to_gb(mem.available),
            "percent": _round(mem.percent),
            "swap_used_gb": _bytes_to_gb(swap.used),
            "swap_percent": _round(swap.percent),
        },
        "disk": {
            "partitions": partitions,
            "io": disk_io_dict,
        },
        "processes": {
            "total": len(psutil.pids()),
            "top_cpu": top_cpu,
            "top_mem": top_mem,
        },
        "network": {
            "sent_mb": _bytes_to_mb(net.bytes_sent),
            "recv_mb": _bytes_to_mb(net.bytes_recv),
        },
        "uptime_hrs": _round((time.time() - psutil.boot_time()) / 3600),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
