from __future__ import annotations

import ipaddress
import json
import subprocess
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class NetworkStatus:
    connected: bool
    interface: str | None
    ssid: str | None
    ipv4_addresses: list[str]
    gateway: str | None
    setup_mode: bool


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def _valid_ipv4(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False
    return ip.version == 4 and not ip.is_loopback and not ip.is_link_local


def collect_network_status() -> NetworkStatus:
    addresses: list[str] = []
    interface: str | None = None
    ssid: str | None = None
    gateway: str | None = None
    setup_mode = False

    result = _run("ip", "-j", "-4", "address", "show", "up")
    if result.returncode == 0:
        try:
            interfaces = json.loads(result.stdout)
        except json.JSONDecodeError:
            interfaces = []
        for item in interfaces:
            name = item.get("ifname")
            if name == "lo":
                continue
            for addr in item.get("addr_info", []):
                local = addr.get("local")
                if isinstance(local, str) and _valid_ipv4(local):
                    addresses.append(local)
                    interface = interface or name

    wifi = _run("nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status")
    if wifi.returncode == 0:
        for line in wifi.stdout.splitlines():
            parts = line.split(":", 3)
            if len(parts) != 4:
                continue
            device, dev_type, state, connection = parts
            if dev_type == "wifi" and state == "connected":
                interface = device
                if connection == "BarPrep Setup":
                    setup_mode = True
                else:
                    ssid = connection

    route = _run("ip", "-j", "route", "show", "default")
    if route.returncode == 0:
        try:
            routes = json.loads(route.stdout)
        except json.JSONDecodeError:
            routes = []
        if routes:
            gateway = routes[0].get("gateway")

    connected = bool(addresses) and not setup_mode
    return NetworkStatus(
        connected=connected,
        interface=interface,
        ssid=ssid,
        ipv4_addresses=sorted(set(addresses)),
        gateway=gateway,
        setup_mode=setup_mode,
    )


def network_status_dict() -> dict[str, object]:
    return asdict(collect_network_status())
