from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .. import __version__
from ..service import get_printer_driver
from ..state import ensure_identity, load_state
from ..system_info import system_info_dict
from .templates import render_status_page


def _printers() -> list[dict[str, object]]:
    return [device.__dict__ for device in get_printer_driver().discover()]


def create_app() -> FastAPI:
    app = FastAPI(
        title="BarPrep Edge OS",
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
    )

    @app.get("/", response_class=HTMLResponse)
    def root() -> HTMLResponse:
        state = ensure_identity()
        return HTMLResponse(
            render_status_page(
                version=__version__,
                state=state,
                system=system_info_dict(),
                printers=_printers(),
            )
        )

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/api/status")
    def status() -> dict[str, object]:
        identity = ensure_identity()
        return {
            "name": "BarPrep Edge OS",
            "version": __version__,
            "device": {
                "device_id": identity["device_id"],
                "paired": identity["paired"],
                "station_id": identity["station_id"],
                "station_name": identity["station_name"],
            },
            "system": system_info_dict(),
            "printers": _printers(),
            "activity": {
                "last_job_id": identity["last_job_id"],
                "last_error": identity["last_error"],
            },
        }

    return app


app = create_app()
