from __future__ import annotations

import importlib.metadata
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class BrotherBackendInfo:
    package_version: str
    mode: str


def brother_package_version() -> str:
    try:
        return importlib.metadata.version("brother-ql")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def identifier_from_discovery_result(raw_device: Any) -> str:
    """
    Normalize discovery values from legacy and current brother_ql releases.

    Current PyUSB discovery may return:
        {"identifier": "usb://...", "instance": <live USB handle>}

    The handle contains ctypes pointers and must remain private to brother_ql.
    """
    if isinstance(raw_device, str) and raw_device:
        return raw_device

    if isinstance(raw_device, dict):
        identifier = raw_device.get("identifier")
        if isinstance(identifier, str) and identifier:
            return identifier

    identifier = getattr(raw_device, "identifier", None)
    if isinstance(identifier, str) and identifier:
        return identifier

    raise ValueError(
        f"Unsupported Brother discovery result: {type(raw_device).__name__}"
    )


def send_instructions(
    instructions: bytes | bytearray | list[int],
    printer_identifier: str,
    *,
    backend_identifier: str = "pyusb",
    blocking: bool = True,
) -> BrotherBackendInfo:
    """
    Send raster instructions using the most stable API available.

    Preferred API:
        brother_ql.backends.helpers.send(...)

    Fallbacks support older releases where backend_factory returned either a
    class or a mapping containing a backend class.
    """
    try:
        from brother_ql.backends.helpers import send

        send(
            instructions=instructions,
            printer_identifier=printer_identifier,
            backend_identifier=backend_identifier,
            blocking=blocking,
        )
        return BrotherBackendInfo(
            package_version=brother_package_version(),
            mode="helpers.send",
        )
    except (ImportError, AttributeError):
        pass

    from brother_ql.backends import backend_factory

    factory_result = backend_factory(backend_identifier)
    backend_class: Callable[..., Any] | None = None

    if callable(factory_result):
        backend_class = factory_result
    elif isinstance(factory_result, dict):
        for key in (
            "backend_class",
            "class",
            "BrotherQLBackend",
            "backend",
        ):
            candidate = factory_result.get(key)
            if callable(candidate):
                backend_class = candidate
                break

    if backend_class is None:
        keys = sorted(factory_result) if isinstance(factory_result, dict) else []
        raise RuntimeError(
            "Unsupported brother_ql backend_factory result"
            + (f"; keys={keys}" if keys else "")
        )

    backend = backend_class(printer_identifier)
    try:
        backend.write(instructions)
    finally:
        dispose = getattr(backend, "dispose", None)
        if callable(dispose):
            dispose()

    return BrotherBackendInfo(
        package_version=brother_package_version(),
        mode="backend_factory",
    )
