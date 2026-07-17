from __future__ import annotations

from dataclasses import dataclass

from .network import NetworkStatus
from .state import load_state


@dataclass(frozen=True)
class ApplianceState:
    code: str
    label: str
    level: str
    detail: str


def determine_appliance_state(network: NetworkStatus, printer_ready: bool) -> ApplianceState:
    state = load_state()
    if network.setup_mode:
        return ApplianceState("wifi_setup", "Wi-Fi setup", "warning",
                              "Connect to the BarPrep setup network.")
    if not network.connected:
        return ApplianceState("connecting", "Connecting", "warning",
                              "Trying saved Wi-Fi networks.")
    if not state.get("paired"):
        return ApplianceState("pairing_required", "Pairing required", "warning",
                              "Connected to Wi-Fi and waiting for BarPrep pairing.")
    if not printer_ready:
        return ApplianceState("printer_required", "Printer required", "error",
                              "Connect the Brother QL-800 by USB.")
    return ApplianceState("ready", "Ready", "ready", "BarPrep Edge is ready to print.")
