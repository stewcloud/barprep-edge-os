from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from .. import __version__
from ..activity import read_activity, record_activity
from ..appliance import determine_appliance_state
from ..capabilities import capability_values
from ..diagnostics import create_diagnostics_zip
from ..network import collect_network_status
from ..service import get_printer_driver
from ..state import ensure_identity, patch_state
from ..system_info import system_info_dict
from ..wifi import connect_wifi, scan_networks
from .templates import render_status_page, render_wifi_page


def _printers() -> list[dict[str, object]]:
    return [asdict(device) for device in get_printer_driver().discover()]


def create_app() -> FastAPI:
    app = FastAPI(title="BarPrep Edge", version=__version__, docs_url="/api/docs", redoc_url=None)

    @app.on_event("startup")
    def startup() -> None:
        ensure_identity()
        record_activity("Runtime started", f"Version {__version__}")

    @app.get("/", response_class=HTMLResponse)
    def root() -> HTMLResponse:
        state = ensure_identity()
        network = collect_network_status()
        printers = _printers()
        appliance = determine_appliance_state(network, any(bool(p.get("ready")) for p in printers))
        return HTMLResponse(render_status_page(version=__version__, state=state,
            system=system_info_dict(), network=asdict(network), appliance=asdict(appliance),
            printers=printers, activity=read_activity(20)))

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/api/status")
    def status() -> dict[str, object]:
        state = ensure_identity()
        network = collect_network_status()
        printers = _printers()
        appliance = determine_appliance_state(network, any(bool(p.get("ready")) for p in printers))
        return {"name": "BarPrep Edge", "version": __version__, "device": state,
                "capabilities": capability_values(), "network": asdict(network),
                "appliance": asdict(appliance), "system": system_info_dict(),
                "printers": printers, "activity": read_activity(20)}

    @app.get("/setup/wifi", response_class=HTMLResponse)
    def wifi_page() -> HTMLResponse:
        try:
            networks = [asdict(item) for item in scan_networks()]
        except Exception as exc:
            raise HTTPException(500, str(exc))
        return HTMLResponse(render_wifi_page(networks, collect_network_status().ssid))

    @app.post("/setup/wifi")
    def wifi_submit(ssid: str = Form(...), password: str = Form("")) -> RedirectResponse:
        try:
            connect_wifi(ssid, password)
            patch_state(last_error=None)
        except Exception as exc:
            patch_state(last_error=str(exc))
            raise HTTPException(400, str(exc))
        return RedirectResponse("/", status_code=303)

    @app.post("/actions/test-print")
    def test_print() -> RedirectResponse:
        state = ensure_identity()
        ready = next((p for p in _printers() if p.get("ready")), None)
        if not ready:
            raise HTTPException(409, "Brother QL-800 is not connected")
        driver = get_printer_driver()
        png = driver.create_test_label("BARPREP EDGE", [
            "Printer Test", f"Device: {str(state['device_id'])[-8:].upper()}",
            f"Station: {state.get('station_name') or 'Not assigned'}", "Printer ready"])
        driver.print_png(png, connection_uri=str(ready["connection_uri"]))
        return RedirectResponse("/", status_code=303)

    @app.get("/diagnostics.zip")
    def diagnostics() -> Response:
        return Response(create_diagnostics_zip(_printers()), media_type="application/zip",
                        headers={"Content-Disposition": "attachment; filename=barprep-edge-diagnostics.zip"})

    return app


app = create_app()
