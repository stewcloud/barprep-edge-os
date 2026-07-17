from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OutputDevice:
    id: str
    name: str
    driver: str
    manufacturer: str
    model: str
    connection: str
    connection_uri: str
    ready: bool
    media_label: str | None = None
    media_description: str | None = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return the stable, JSON-safe public representation of an output."""
        return {
            "id": self.id,
            "name": self.name,
            "driver": self.driver,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "connection": self.connection,
            "connection_uri": self.connection_uri,
            "ready": self.ready,
            "media_label": self.media_label,
            "media_description": self.media_description,
            "detail": self.detail,
        }


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

    @abstractmethod
    def create_test_label(self, title: str, lines: list[str]) -> bytes:
        raise NotImplementedError
