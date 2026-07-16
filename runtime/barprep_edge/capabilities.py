from __future__ import annotations

from enum import StrEnum


class Capability(StrEnum):
    LABEL_PRINTING = "label-printing"
    USB_PRINTER = "usb-printer"
    WIFI = "wifi"
    MDNS = "mdns"
    LOCAL_STATUS = "local-status"


DEFAULT_CAPABILITIES: tuple[Capability, ...] = (
    Capability.LABEL_PRINTING,
    Capability.USB_PRINTER,
    Capability.WIFI,
    Capability.MDNS,
    Capability.LOCAL_STATUS,
)


def capability_values() -> list[str]:
    return [capability.value for capability in DEFAULT_CAPABILITIES]
