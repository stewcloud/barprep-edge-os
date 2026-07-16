from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OutputDevice:
    id: str
    name: str
    driver: str
    model: str
    connection_uri: str
    ready: bool
    detail: str = ""


class PrinterDriver(ABC):
    @abstractmethod
    def discover(self) -> list[OutputDevice]:
        raise NotImplementedError

    @abstractmethod
    def print_png(
        self,
        png_data: bytes,
        *,
        copies: int = 1,
        cut: bool = True,
        connection_uri: str | None = None,
    ) -> None:
        raise NotImplementedError
