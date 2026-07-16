from __future__ import annotations

import logging
import socket

import uvicorn

from .config import settings
from .state import ensure_identity


def _configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> None:
    _configure_logging()
    identity = ensure_identity()
    logging.getLogger(__name__).info(
        "Starting BarPrep Edge device_id=%s hostname=%s",
        identity["device_id"],
        socket.gethostname(),
    )
    uvicorn.run(
        "barprep_edge.web.app:app",
        host=settings.bind,
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
