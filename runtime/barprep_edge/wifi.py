from __future__ import annotations

import subprocess
import time
from dataclasses import asdict, dataclass

from .activity import record_activity
from .config import settings


@dataclass(frozen=True)
class WifiNetwork:
    ssid: str
    signal: int
    security: str


def _run(*args: str, check: bool = True) -> str:
    result = subprocess.run(args, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or "NetworkManager command failed")
    return result.stdout.strip()


def scan_networks() -> list[WifiNetwork]:
    _run("nmcli", "device", "wifi", "rescan", "ifname", settings.wifi_interface, check=False)
    time.sleep(1)
    output = _run("nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY",
                  "device", "wifi", "list", "ifname", settings.wifi_interface)
    found: dict[str, WifiNetwork] = {}
    for line in output.splitlines():
        parts = line.rsplit(":", 2)
        if len(parts) != 3:
            continue
        ssid, signal, security = parts
        ssid = ssid.replace(r"\:", ":").strip()
        if not ssid:
            continue
        try:
            signal_value = int(signal)
        except ValueError:
            signal_value = 0
        item = WifiNetwork(ssid=ssid, signal=signal_value, security=security)
        if ssid not in found or item.signal > found[ssid].signal:
            found[ssid] = item
    return sorted(found.values(), key=lambda item: item.signal, reverse=True)


def connect_wifi(ssid: str, password: str = "") -> None:
    stop_setup_ap()
    args = ["nmcli", "device", "wifi", "connect", ssid, "ifname", settings.wifi_interface]
    if password:
        args.extend(["password", password])
    try:
        _run(*args)
        record_activity("Wi-Fi connected", ssid)
    except Exception:
        start_setup_ap()
        record_activity("Wi-Fi connection failed", ssid, "error")
        raise


def setup_ssid(device_id: str) -> str:
    return f"{settings.setup_ssid_prefix}-{device_id[-4:].upper()}"


def start_setup_ap(ssid: str | None = None) -> str:
    if ssid is None:
        from .state import ensure_identity
        ssid = setup_ssid(ensure_identity()["device_id"])
    _run("nmcli", "connection", "down", "BarPrep Setup", check=False)
    _run("nmcli", "connection", "delete", "BarPrep Setup", check=False)
    _run("nmcli", "connection", "add", "type", "wifi", "ifname", settings.wifi_interface,
         "con-name", "BarPrep Setup", "autoconnect", "no", "ssid", ssid)
    _run("nmcli", "connection", "modify", "BarPrep Setup",
         "802-11-wireless.mode", "ap", "ipv4.method", "shared", "ipv6.method", "disabled")
    if settings.setup_password:
        _run("nmcli", "connection", "modify", "BarPrep Setup",
             "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", settings.setup_password)
    _run("nmcli", "connection", "up", "BarPrep Setup")
    record_activity("Wi-Fi setup started", ssid)
    return ssid


def stop_setup_ap() -> None:
    _run("nmcli", "connection", "down", "BarPrep Setup", check=False)


def wifi_network_dicts() -> list[dict[str, object]]:
    return [asdict(item) for item in scan_networks()]
