from __future__ import annotations

import io
from pathlib import Path

from brother_ql.backends.helpers import discover
from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster
from PIL import Image, ImageDraw, ImageFont

from ..activity import record_activity
from ..config import settings
from .base import OutputDevice, PrinterDriver
from .brother_compat import identifier_from_discovery_result, send_instructions


FONT_CANDIDATES = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
]


def _load_font(size: int) -> ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def _fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    max_width: int,
    preferred_size: int,
    minimum_size: int,
) -> ImageFont.ImageFont:
    for size in range(preferred_size, minimum_size - 1, -2):
        font = _load_font(size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        if right - left <= max_width:
            return font
    return _load_font(minimum_size)


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
                identifier = identifier_from_discovery_result(raw_device)
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

        try:
            backend = send_instructions(
                instructions,
                uri,
                backend_identifier="pyusb",
                blocking=True,
            )
            record_activity(
                "Print completed",
                f"{copies} label(s) via {backend.mode} "
                f"(brother-ql {backend.package_version})",
            )
        except Exception as exc:
            record_activity("Print failed", str(exc), "error")
            raise

    def create_test_label(self, title: str, lines: list[str]) -> bytes:
        width = 696
        height = 420
        margin = 24
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle(
            (8, 8, width - 8, height - 8),
            radius=18,
            outline="black",
            width=5,
        )

        title_font = _fit_text(
            draw,
            title,
            max_width=width - (margin * 2),
            preferred_size=64,
            minimum_size=42,
        )
        title_box = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_box[2] - title_box[0]
        draw.text(
            ((width - title_width) // 2, 24),
            title,
            fill="black",
            font=title_font,
        )

        divider_y = 112
        draw.line((margin, divider_y, width - margin, divider_y), fill="black", width=4)

        body_lines = lines[:4]
        y = 136
        available_width = width - (margin * 2)

        for index, line in enumerate(body_lines):
            preferred = 46 if index == 0 else 38
            minimum = 30
            font = _fit_text(
                draw,
                line,
                max_width=available_width,
                preferred_size=preferred,
                minimum_size=minimum,
            )
            draw.text((margin, y), line, fill="black", font=font)
            box = draw.textbbox((margin, y), line, font=font)
            line_height = box[3] - box[1]
            y += max(line_height + 18, 64)

        output = io.BytesIO()
        image.save(output, "PNG")
        return output.getvalue()
