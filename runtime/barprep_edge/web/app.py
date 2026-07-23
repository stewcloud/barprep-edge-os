from __future__ import annotations

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from .. import __version__
from ..activity import read_activity, record_activity
from ..appliance import determine_appliance_state
from ..capabilities import capability_values
from ..diagnostics import create_diagnostics_zip
from ..drivers.brother_compat import brother_package_version
from ..network import collect_network_status
from ..pairing import (
    PairingError,
    check_pairing_status,
    clear_pairing_state,
    create_pairing_request,
    load_pairing_state,
)
from ..service import get_printer_driver
from ..state import ensure_identity, patch_state
from ..system_info import system_info_dict
from ..wifi import connect_wifi, scan_networks
from .templates import (
    render_pairing_page,
    render_status_page,
    render_wifi_page,
)


def _printers() -> list[dict[str, object]]:
    return [device.to_dict() for device in get_printer_driver().discover()]


def create_app() -> FastAPI:
    app = FastAPI(
        title="BarPrep Edge",
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
    )

    @app.on_event("startup")
    def startup() -> None:
        ensure_identity()
        try:
            pairing = load_pairing_state()
            patch_state(
                paired=pairing.paired,
                station_name=pairing.station_name or None,
            )
        except PairingError as exc:
            patch_state(last_error=str(exc))
            record_activity("Pairing state error", str(exc), "error")

        record_activity(
            "Runtime started",
            f"Version {__version__}; brother-ql {brother_package_version()}",
        )

    @app.get("/", response_class=HTMLResponse)
    def root() -> HTMLResponse:
        state = ensure_identity()
        pairing = load_pairing_state()
        network = collect_network_status()
        printers = _printers()
        appliance = determine_appliance_state(
            network,
            any(bool(printer.get("ready")) for printer in printers),
        )
        return HTMLResponse(
            render_status_page(
                version=__version__,
                state=state,
                pairing=pairing.public_dict(),
                system=system_info_dict(),
                network=network.__dict__,
                appliance=appliance.__dict__,
                printers=printers,
                activity=read_activity(20),
            )
        )

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "version": __version__,
            "brother_ql_version": brother_package_version(),
        }

    @app.get("/api/status")
    def status() -> dict[str, object]:
        state = ensure_identity()
        pairing = load_pairing_state()
        network = collect_network_status()
        printers = _printers()
        appliance = determine_appliance_state(
            network,
            any(bool(printer.get("ready")) for printer in printers),
        )
        return {
            "name": "BarPrep Edge",
            "version": __version__,
            "brother_ql_version": brother_package_version(),
            "device": state,
            "pairing": pairing.public_dict(),
            "capabilities": capability_values(),
            "network": network.__dict__,
            "appliance": appliance.__dict__,
            "system": system_info_dict(),
            "printers": printers,
            "activity": read_activity(20),
        }

    @app.get("/setup/pair", response_class=HTMLResponse)
    def pairing_page() -> HTMLResponse:
        return HTMLResponse(
            render_pairing_page(
                pairing=load_pairing_state().public_dict(),
                default_core_url="",
            )
        )

    @app.post("/setup/pair")
    def pairing_submit(core_url: str = Form(...)) -> RedirectResponse:
        identity = ensure_identity()
        try:
            create_pairing_request(
                core_url=core_url,
                device_id=str(identity["device_id"]),
                friendly_name=str(
                    identity.get("friendly_name") or "BarPrep Edge"
                ),
                version=__version__,
                capabilities=capability_values(),
            )
        except PairingError as exc:
            record_activity(
                "Pairing registration failed",
                str(exc),
                "error",
            )
            raise HTTPException(400, str(exc)) from exc

        patch_state(
            paired=False,
            station_name=None,
            last_error=None,
        )
        record_activity(
            "Pairing requested",
            "Waiting for approval in BarPrep Core",
        )
        return RedirectResponse("/setup/pair", status_code=303)

    @app.post("/setup/pair/check")
    def pairing_check() -> RedirectResponse:
        try:
            pairing = check_pairing_status(version=__version__)
        except PairingError as exc:
            record_activity(
                "Pairing status failed",
                str(exc),
                "error",
            )
            raise HTTPException(400, str(exc)) from exc

        if pairing.paired:
            patch_state(
                paired=True,
                station_name=pairing.station_name or None,
                last_error=None,
            )
            record_activity("Edge paired", pairing.core_url)
            return RedirectResponse("/?paired=success", status_code=303)

        return RedirectResponse("/setup/pair", status_code=303)

    @app.post("/actions/unpair")
    def unpair() -> RedirectResponse:
        prior = load_pairing_state()
        clear_pairing_state()
        patch_state(
            paired=False,
            station_name=None,
        )
        record_activity(
            "Edge unpaired",
            prior.core_url or "Local pairing data removed",
            "warning",
        )
        return RedirectResponse("/?unpaired=success", status_code=303)

    @app.get("/setup/wifi", response_class=HTMLResponse)
    def wifi_page() -> HTMLResponse:
        try:
            networks = [network.__dict__ for network in scan_networks()]
        except Exception as exc:
            raise HTTPException(500, str(exc)) from exc
        return HTMLResponse(render_wifi_page(networks, collect_network_status().ssid))

    @app.post("/setup/wifi")
    def wifi_submit(
        ssid: str = Form(...),
        password: str = Form(""),
    ) -> RedirectResponse:
        try:
            connect_wifi(ssid, password)
            patch_state(last_error=None)
        except Exception as exc:
            patch_state(last_error=str(exc))
            raise HTTPException(400, str(exc)) from exc
        return RedirectResponse("/", status_code=303)

    @app.post("/actions/test-print")
    def test_print() -> RedirectResponse:
        state = ensure_identity()
        ready = next(
            (printer for printer in _printers() if printer.get("ready")),
            None,
        )

        if not ready:
            raise HTTPException(409, "Brother QL-800 is not connected")

        driver = get_printer_driver()
        png = driver.create_test_label(
            "BARPREP EDGE",
            [
                "Printer Test",
                f"Device: {str(state['device_id'])[-8:].upper()}",
                f"Station: {state.get('station_name') or 'Not assigned'}",
                f"Edge: {__version__}",
            ],
        )

        try:
            driver.print_png(
                png,
                connection_uri=str(ready["connection_uri"]),
            )
        except Exception as exc:
            raise HTTPException(
                500,
                f"Printer test failed: {exc}",
            ) from exc

        return RedirectResponse("/?test_print=success", status_code=303)

    @app.get("/diagnostics.zip")
    def diagnostics() -> Response:
        return Response(
            create_diagnostics_zip(_printers()),
            media_type="application/zip",
            headers={
                "Content-Disposition":
                    "attachment; filename=barprep-edge-diagnostics.zip"
            },
        )

    return app


app = create_app()
