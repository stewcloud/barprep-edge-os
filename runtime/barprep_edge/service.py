from __future__ import annotations

from .drivers import BrotherQLDriver, PrinterDriver


def get_printer_driver() -> PrinterDriver:
    return BrotherQLDriver()
