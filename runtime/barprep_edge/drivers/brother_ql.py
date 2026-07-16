from __future__ import annotations

import io

from brother_ql.backends import backend_factory
from brother_ql.backends.helpers import discover
from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster
from PIL import Image

from ..config import settings
from .base import OutputDevice, PrinterDriver


class BrotherQLDriver(PrinterDriver):
    def discover(self) -> list[OutputDevice]:
        devices: list[OutputDevice] = []

        try:
            for uri in discover("pyusb"):
                devices.append(
                    OutputDevice(
                        id=uri,
                        name=f"Brother {settings.printer_model}",
                        driver="brother_ql",
                        model=settings.printer_model,
                        connection_uri=uri,
                        ready=True,
                    )
                )
        except Exception as exc:
            devices.append(
                OutputDevice(
                    id=settings.printer_uri,
                    name=f"Brother {settings.printer_model}",
                    driver="brother_ql",
                    model=settings.printer_model,
                    connection_uri=settings.printer_uri,
                    ready=False,
                    detail=str(exc),
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
        finally:
            backend.dispose()
