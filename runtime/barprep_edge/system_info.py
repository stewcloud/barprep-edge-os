from __future__ import annotations

import os
import platform
import shutil
import socket
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class SystemInfo:
    hostname: str
    os_name: str
    kernel: str
    architecture: str
    python_version: str
    uptime_seconds: int
    cpu_temperature_c: float | None
    memory_total_bytes: int | None
    memory_available_bytes: int | None
    disk_total_bytes: int
    disk_free_bytes: int
    ip_addresses: list[str]


def _uptime_seconds() -> int:
    try:
        return int(float(Path("/proc/uptime").read_text(encoding="utf-8").split()[0]))
    except (OSError, ValueError, IndexError):
        return int(time.monotonic())


def _cpu_temperature_c() -> float | None:
    candidates = [
        Path("/sys/class/thermal/thermal_zone0/temp"),
        Path("/sys/class/hwmon/hwmon0/temp1_input"),
    ]
    for path in candidates:
        try:
            raw = float(path.read_text(encoding="utf-8").strip())
            return round(raw / 1000.0 if raw > 200 else raw, 1)
        except (OSError, ValueError):
            continue
    return None


def _memory() -> tuple[int | None, int | None]:
    values: dict[str, int] = {}
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            key, value = line.split(":", 1)
            values[key] = int(value.strip().split()[0]) * 1024
    except (OSError, ValueError, IndexError):
        return None, None
    return values.get("MemTotal"), values.get("MemAvailable")


def _ip_addresses() -> list[str]:
    addresses: set[str] = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            address = info[4][0]
            if ":" not in address and not address.startswith("127."):
                addresses.add(address)
    except socket.gaierror:
        pass
    return sorted(addresses)


def collect_system_info() -> SystemInfo:
    memory_total, memory_available = _memory()
    disk = shutil.disk_usage("/")
    return SystemInfo(
        hostname=socket.gethostname(),
        os_name=platform.platform(),
        kernel=platform.release(),
        architecture=platform.machine(),
        python_version=platform.python_version(),
        uptime_seconds=_uptime_seconds(),
        cpu_temperature_c=_cpu_temperature_c(),
        memory_total_bytes=memory_total,
        memory_available_bytes=memory_available,
        disk_total_bytes=disk.total,
        disk_free_bytes=disk.free,
        ip_addresses=_ip_addresses(),
    )


def system_info_dict() -> dict[str, object]:
    return asdict(collect_system_info())
