from __future__ import annotations

import io
from typing import Any

from brother_ql.backends import backend_factory
from brother_ql.backends.helpers import discover
from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster
from PIL import Image, ImageDraw, ImageFont

from ..activity import record_activity
from ..config import settings
from .base import OutputDevice, PrinterDriver


def _identifier_from_discovery_result(raw_device: Any) -> str:
    """
    Normalize brother_ql discovery results into a stable string identifier.

    Newer brother_ql/PyUSB combinations can return a dictionary containing
    both an identifier and a live USB device instance. The live instance wraps
    ctypes pointers and must never enter our public device model.
    """
    if isinstance(raw_device, dict):
        identifier = raw_device.get("identifier")
        if isinstance(identifier, str) and identifier:
            return identifier

    identifier = getattr(raw_device, "identifier", None)
    if isinstance(identifier, str) and identifier:
        return identifier

    if isinstance(raw_device, str):
        return raw_device

    raise ValueError(f"Unsupported Brother discovery result: {type(raw_device).__name__}")


class BrotherQLDriver(PrinterDriver):
    def discover(self) -> list[OutputDevice]:
        try:
            raw_devices = discover("pyusb")
        except Exception as exc:
            return [
                OutputDevice(
                    id=settings.printer_uri,
                    name=f"Brother {settings.printer_model}",
                    driver="brother_ql",
                    manufacturer="Brother",
                    model=settings.printer_model,
                    connection="usb",
                    connection_uri=settings.printer_uri,
                    ready=False,
                    media_label=settings.printer_label,
                    media_description=settings.printer_label_description,
                    detail=str(exc),
                )
            ]

        devices: list[OutputDevice] = []
        for raw_device in raw_devices:
            try:
                identifier = _identifier_from_discovery_result(raw_device)
            except ValueError as exc:
                record_activity("Printer discovery warning", str(exc), "warning")
                continue

            devices.append(
                OutputDevice(
                    id=identifier,
                    name=f"Brother {settings.printer_model}",
                    driver="brother_ql",
                    manufacturer="Brother",
                    model=settings.printer_model,
                    connection="usb",
                    connection_uri=identifier,
                    ready=True,
                    media_label=settings.printer_label,
                    media_description=settings.printer_label_description,
                )
            )

        return devices

    def print_png(
        self,
        png_data: bytes,
        *,
        copies: int = 1,
        cut: bool = True,
        connection_uri: str | None = None,
    ) -> None:
        if copies < 1:
            raise ValueError("copies must be at least 1")

        uri = connection_uri or settings.printer_uri
        image = Image.open(io.BytesIO(png_data)).convert("RGB")
        raster = BrotherQLRaster(settings.printer_model)
        raster.exception_on_warning = True

        instructions = convert(
            qlr=raster,
            images=[image] * copies,
            label=settings.printer_label,
            rotate="auto",
            threshold=70.0,
            dither=False,
            compress=True,
            red=False,
            dpi_600=False,
            hq=True,
            cut=cut,
        )

        backend_class = backend_factory("pyusb")
        backend = backend_class(uri)

        try:
            backend.write(instructions)
            record_activity("Print completed", f"{copies} test label(s)")
        except Exception as exc:
            record_activity("Print failed", str(exc), "error")
            raise
        finally:
            backend.dispose()

    def create_test_label(self, title: str, lines: list[str]) -> bytes:
        image = Image.new("RGB", (696, 360), "white")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        draw.rectangle((8, 8, 688, 352), outline="black", width=4)
        draw.text((30, 28), title, fill="black", font=font)

        y = 90
        for line in lines:
            draw.text((30, y), line, fill="black", font=font)
            y += 44

        output = io.BytesIO()
        image.save(output, "PNG")
        return output.getvalue()
