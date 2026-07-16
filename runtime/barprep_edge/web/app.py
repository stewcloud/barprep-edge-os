from __future__ import annotations

from fastapi import FastAPI

from .. import __version__
from ..service import get_printer_driver
from ..state import ensure_identity, load_state


def create_app() -> FastAPI:
    app = FastAPI(title="BarPrep Edge OS", version=__version__)

    @app.get("/")
    def root() -> dict[str, object]:
        state = load_state()
        printers = [device.__dict__ for device in get_printer_driver().discover()]

        return {
            "name": "BarPrep Edge OS",
            "version": __version__,
            "paired": state["paired"],
            "station": state["station_name"],
            "printers": printers,
        }

    @app.get("/api/status")
    def status() -> dict[str, object]:
        identity = ensure_identity()
        printers = [device.__dict__ for device in get_printer_driver().discover()]

        return {
            "version": __version__,
            "device_id": identity["device_id"],
            "paired": identity["paired"],
            "station_id": identity["station_id"],
            "station_name": identity["station_name"],
            "last_job_id": identity["last_job_id"],
            "last_error": identity["last_error"],
            "printers": printers,
        }

    return app


app = create_app()
