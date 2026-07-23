from __future__ import annotations
import importlib.metadata
import re
from dataclasses import dataclass
from typing import Any, Callable

USB_IDENTIFIER_PATTERN = re.compile(
    r"^usb://(?P<vendor>0x[0-9a-fA-F]{4}):(?P<product>0x[0-9a-fA-F]{4})"
)

@dataclass(frozen=True)
class BrotherBackendInfo:
    package_version: str
    mode: str

def brother_package_version() -> str:
    try:
        return importlib.metadata.version("brother-ql")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"

def normalize_usb_identifier(identifier: str) -> str:
    match = USB_IDENTIFIER_PATTERN.match(identifier.strip())
    if not match:
        return identifier.strip()
    return f"usb://{match.group('vendor').lower()}:{match.group('product').lower()}"

def identifier_from_discovery_result(raw_device: Any) -> str:
    identifier: str | None = None
    if isinstance(raw_device, str) and raw_device:
        identifier = raw_device
    elif isinstance(raw_device, dict):
        candidate = raw_device.get("identifier")
        if isinstance(candidate, str) and candidate:
            identifier = candidate
    else:
        candidate = getattr(raw_device, "identifier", None)
        if isinstance(candidate, str) and candidate:
            identifier = candidate
    if identifier is None:
        raise ValueError(f"Unsupported Brother discovery result: {type(raw_device).__name__}")
    return normalize_usb_identifier(identifier)

def send_instructions(
    instructions: bytes | bytearray | list[int],
    printer_identifier: str,
    *,
    backend_identifier: str = "pyusb",
    blocking: bool = True,
) -> BrotherBackendInfo:
    normalized_identifier = normalize_usb_identifier(printer_identifier)
    try:
        from brother_ql.backends.helpers import send
        send(
            instructions=instructions,
            printer_identifier=normalized_identifier,
            backend_identifier=backend_identifier,
            blocking=blocking,
        )
        return BrotherBackendInfo(brother_package_version(), "helpers.send")
    except (ImportError, AttributeError):
        pass

    from brother_ql.backends import backend_factory
    factory_result = backend_factory(backend_identifier)
    backend_class: Callable[..., Any] | None = None
    if callable(factory_result):
        backend_class = factory_result
    elif isinstance(factory_result, dict):
        for key in ("backend_class", "class", "BrotherQLBackend", "backend"):
            candidate = factory_result.get(key)
            if callable(candidate):
                backend_class = candidate
                break
    if backend_class is None:
        keys = sorted(factory_result) if isinstance(factory_result, dict) else []
        raise RuntimeError("Unsupported brother_ql backend_factory result" + (f"; keys={keys}" if keys else ""))
    backend = backend_class(normalized_identifier)
    try:
        backend.write(instructions)
    finally:
        dispose = getattr(backend, "dispose", None)
        if callable(dispose):
            dispose()
    return BrotherBackendInfo(brother_package_version(), "backend_factory")
