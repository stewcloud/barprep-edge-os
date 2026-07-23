#!/usr/bin/env python3
from pathlib import Path
import re
import sys

repo = Path(sys.argv[1]).resolve()
app_path = repo / "runtime/barprep_edge/web/app.py"
templates_path = repo / "runtime/barprep_edge/web/templates.py"
init_path = repo / "runtime/barprep_edge/__init__.py"

app = app_path.read_text()
app = app.replace(
"""from ..pairing import (
    PairingError,
    clear_pairing_state,
    create_pairing_request,
    load_pairing_state,
)""",
"""from ..pairing import (
    PairingError,
    check_pairing_status,
    clear_pairing_state,
    create_pairing_request,
    load_pairing_state,
)"""
)
start = app.find('  @app.post("/setup/pair")')
end = app.find('  @app.post("/actions/unpair")', start)
if start == -1 or end == -1:
    raise SystemExit("Unable to locate old pairing route")
app = app[:start] + '  @app.post("/setup/pair")\n  def pairing_submit(core_url: str = Form(...)) -> RedirectResponse:\n      identity = ensure_identity()\n      try:\n          create_pairing_request(\n              core_url=core_url,\n              device_id=str(identity["device_id"]),\n              friendly_name=str(identity.get("friendly_name") or "BarPrep Edge"),\n              version=__version__,\n              capabilities=capability_values(),\n          )\n      except PairingError as exc:\n          record_activity("Pairing registration failed", str(exc), "error")\n          raise HTTPException(400, str(exc)) from exc\n      patch_state(paired=False, station_name=None, last_error=None)\n      record_activity("Pairing requested", "Waiting for approval in BarPrep Core")\n      return RedirectResponse("/setup/pair", status_code=303)\n\n  @app.post("/setup/pair/check")\n  def pairing_check() -> RedirectResponse:\n      try:\n          pairing = check_pairing_status(version=__version__)\n      except PairingError as exc:\n          record_activity("Pairing status failed", str(exc), "error")\n          raise HTTPException(400, str(exc)) from exc\n      if pairing.paired:\n          patch_state(paired=True, station_name=pairing.station_name or None, last_error=None)\n          record_activity("Edge paired", pairing.core_url)\n          return RedirectResponse("/?paired=success", status_code=303)\n      return RedirectResponse("/setup/pair", status_code=303)\n\n' + app[end:]
app_path.write_text(app)

templates = templates_path.read_text()
start = templates.find("def render_pairing_page(")
end = templates.find("def render_wifi_page(", start)
if start == -1 or end == -1:
    raise SystemExit("Unable to locate old pairing template")
templates = templates[:start] + 'def render_pairing_page(\n    *,\n    pairing: dict[str, Any],\n    default_core_url: str,\n) -> str:\n    if pairing.get("paired"):\n        return f"""<!doctype html><html><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>Pair BarPrep Edge</title>{STYLE}</head><body><main>\n<header><div class="brand"><div class="mark">BP</div><div>\n<h1>Edge is paired</h1>\n<p class="subtitle">{escape(str(pairing.get("station_name") or "BarPrep Core"))}</p>\n</div></div></header><article class="card">\n<p>This Edge is connected to <strong>{escape(str(pairing.get("core_url")))}</strong>.</p>\n<div class="actions"><a class="button secondary" href="/">Return to dashboard</a>\n<form method="post" action="/actions/unpair"><button class="danger">Unpair Edge</button></form>\n</div></article></main></body></html>"""\n\n    if pairing.get("pending"):\n        code = escape(str(pairing.get("pairing_code_display") or "------"))\n        status = escape(str(pairing.get("approval_status") or "pending").title())\n        return f"""<!doctype html><html><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>Approve BarPrep Edge</title>{STYLE}</head><body><main>\n<header><div class="brand"><div class="mark">BP</div><div>\n<h1>Approve this Edge</h1>\n<p class="subtitle">Confirm the same code in BarPrep Core.</p>\n</div></div></header>\n<div class="notice">Open BarPrep Core → Edge Devices and approve this device.</div>\n<article class="card"><p class="help">Pairing code</p>\n<h1 style="font-size:3rem;letter-spacing:.12em">{code}</h1>\n<p>Status: <strong>{status}</strong></p>\n<div class="actions"><form method="post" action="/setup/pair/check">\n<button>Check Approval</button></form>\n<a class="button secondary" href="/">Return to dashboard</a></div>\n</article></main></body></html>"""\n\n    return f"""<!doctype html><html><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>Pair BarPrep Edge</title>{STYLE}</head><body><main>\n<header><div class="brand"><div class="mark">BP</div><div>\n<h1>Pair with BarPrep</h1>\n<p class="subtitle">Connect this appliance to BarPrep Core.</p>\n</div></div></header>\n<div class="notice">Enter your normal BarPrep URL. Edge and Core will display the same six-digit code.</div>\n<article class="card"><form method="post" action="/setup/pair">\n<label for="core_url">BarPrep Core URL</label>\n<input id="core_url" name="core_url" type="url" required\nplaceholder="https://barprep.example.com" value="{escape(default_core_url)}">\n<p class="help">Do not enter a pairing code. Edge registers itself with Core.</p>\n<div class="actions"><button>Register Edge</button>\n<a class="button secondary" href="/">Cancel</a></div>\n</form></article></main></body></html>"""\n\n\n' + templates[end:]
templates_path.write_text(templates)

if init_path.exists():
    text = init_path.read_text()
    text = re.sub(r'__version__\s*=\s*"[^"]+"', '__version__ = "0.3.1"', text)
    init_path.write_text(text)

print("Patched BarPrep Edge to 0.3.1.")
