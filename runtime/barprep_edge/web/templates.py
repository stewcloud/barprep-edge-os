from __future__ import annotations

from html import escape
from typing import Any

STYLE = """<style>
:root{--bg:#f3f1eb;--card:#fff;--ink:#171714;--muted:#69675f;--line:#dfddd6;--ready:#177245;--ready-bg:#e5f5ec;--warning:#9a5b00;--warning-bg:#fff1d5;--error:#8d2e2e;--error-bg:#fbe8e8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
main{width:min(920px,calc(100% - 32px));margin:32px auto 64px}header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;margin-bottom:24px}
.brand{display:flex;gap:14px;align-items:center}.mark{width:48px;height:48px;border-radius:13px;background:#171714;color:#fff;display:grid;place-items:center;font-weight:800}
h1{margin:0;font-size:clamp(1.7rem,4vw,2.4rem)}.subtitle{margin:4px 0 0;color:var(--muted)}
.pill{display:inline-flex;border-radius:999px;padding:7px 11px;font-size:.8rem;font-weight:750}.pill.ready{color:var(--ready);background:var(--ready-bg)}.pill.warning{color:var(--warning);background:var(--warning-bg)}.pill.error{color:var(--error);background:var(--error-bg)}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px}.card.wide{grid-column:1/-1}
.metric-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.metric{border:1px solid var(--line);border-radius:12px;padding:13px}.metric span{display:block;color:var(--muted);font-size:.78rem;margin-bottom:5px}.metric strong{overflow-wrap:anywhere}
.device-row{display:flex;justify-content:space-between;gap:16px;align-items:center}.empty-state{color:var(--muted);border:1px dashed var(--line);border-radius:12px;padding:18px}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}button,.button{border:0;border-radius:10px;padding:11px 15px;background:#171714;color:#fff;font-weight:700;text-decoration:none;cursor:pointer}.button.secondary{background:#ebe8df;color:#171714}
.activity{padding:12px 0;border-top:1px solid var(--line)}.activity:first-of-type{border-top:0}.activity time{color:var(--muted);font-size:.76rem}.activity strong{display:block}
select,input{width:100%;padding:11px;border:1px solid var(--line);border-radius:9px;margin:6px 0 13px}
footer{color:var(--muted);font-size:.78rem;margin-top:18px;text-align:center}@media(max-width:680px){.grid{grid-template-columns:1fr}.card.wide{grid-column:auto}}
</style>"""


def _bytes(value: int | None) -> str:
    if value is None:
        return "Unavailable"
    n = float(value)
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}"
        n /= 1024
    return str(value)


def render_status_page(*, version: str, state: dict[str, Any], system: dict[str, Any],
                       network: dict[str, Any], appliance: dict[str, Any],
                       printers: list[dict[str, Any]], activity: list[dict[str, Any]]) -> str:
    ips = network.get("ipv4_addresses") or []
    mem_total = system.get("memory_total_bytes")
    mem_available = system.get("memory_available_bytes")
    mem_used = mem_total - mem_available if isinstance(mem_total,int) and isinstance(mem_available,int) else None
    printer_html = '<div class="empty-state"><strong>No printer detected</strong><br>Supported: Brother QL-800 over USB.</div>'
    if printers:
        p = printers[0]
        printer_html = f'<div class="device-row"><div><strong>{escape(str(p.get("name")))}</strong><br><small>{escape(str(p.get("connection","")).upper())} · {escape(str(p.get("media_description") or "Media unknown"))}</small></div><span class="pill {"ready" if p.get("ready") else "error"}>{"Ready" if p.get("ready") else "Unavailable"}</span></div>'
    activity_html = "".join(f'<div class="activity"><time>{escape(str(a.get("timestamp","")))}</time><strong>{escape(str(a.get("event","")))}</strong><span>{escape(str(a.get("detail","")))}</span></div>' for a in activity) or '<div class="empty-state">No recent activity.</div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="30"><title>BarPrep Edge</title>{STYLE}</head><body><main>
<header><div class="brand"><div class="mark">BP</div><div><h1>BarPrep Edge</h1><p class="subtitle">{escape(str(state.get("friendly_name") or "barprep-edge"))}</p></div></div><span class="pill {escape(str(appliance.get("level")))}">{escape(str(appliance.get("label")))}</span></header>
<section class="grid">
<article class="card"><h2>Edge identity</h2><div class="metric-grid"><div class="metric"><span>Device ID</span><strong>{escape(str(state.get("device_id"))[-8:].upper())}</strong></div><div class="metric"><span>Edge version</span><strong>{escape(version)}</strong></div><div class="metric"><span>Pairing</span><strong>{"Paired" if state.get("paired") else "Not paired"}</strong></div><div class="metric"><span>Station</span><strong>{escape(str(state.get("station_name") or "Not assigned"))}</strong></div></div></article>
<article class="card"><h2>Network</h2><div class="metric-grid"><div class="metric"><span>Wi-Fi</span><strong>{escape(str(network.get("ssid") or ("Setup mode" if network.get("setup_mode") else "Connecting")))}</strong></div><div class="metric"><span>Address</span><strong>{escape(", ".join(ips) if ips else "Not connected")}</strong></div><div class="metric"><span>Local URL</span><strong>barprep-edge.local:8787</strong></div><div class="metric"><span>Status</span><strong>{"Online" if network.get("connected") else "Offline"}</strong></div></div><div class="actions"><a class="button secondary" href="/setup/wifi">Change Wi-Fi</a></div></article>
<article class="card wide"><h2>Printer</h2>{printer_html}<div class="actions"><form method="post" action="/actions/test-print"><button>Print test label</button></form><a class="button secondary" href="/diagnostics.zip">Download diagnostics</a></div></article>
<article class="card"><h2>System</h2><div class="metric-grid"><div class="metric"><span>Uptime</span><strong>{int(system.get("uptime_seconds") or 0)//60}m</strong></div><div class="metric"><span>CPU temperature</span><strong>{system.get("cpu_temperature_c")}°C</strong></div><div class="metric"><span>Memory used</span><strong>{_bytes(mem_used)}</strong></div><div class="metric"><span>Memory total</span><strong>{_bytes(mem_total)}</strong></div></div></article>
<article class="card"><h2>Storage and software</h2><div class="metric-grid"><div class="metric"><span>Disk free</span><strong>{_bytes(system.get("disk_free_bytes"))}</strong></div><div class="metric"><span>Architecture</span><strong>{escape(str(system.get("architecture")))}</strong></div><div class="metric"><span>Kernel</span><strong>{escape(str(system.get("kernel")))}</strong></div><div class="metric"><span>Python</span><strong>{escape(str(system.get("python_version")))}</strong></div></div></article>
<article class="card wide"><h2>Recent activity</h2>{activity_html}</article></section><footer>{escape(str(appliance.get("detail")))}</footer></main></body></html>"""


def render_wifi_page(networks: list[dict[str, object]], current_ssid: str | None) -> str:
    options = "".join(f'<option value="{escape(str(n["ssid"]))}">{escape(str(n["ssid"]))} ({n["signal"]}%)</option>' for n in networks)
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Connect BarPrep Edge</title>{STYLE}</head><body><main><header><div class="brand"><div class="mark">BP</div><div><h1>Connect BarPrep Edge</h1><p class="subtitle">Choose the Wi-Fi network for this location.</p></div></div></header><article class="card"><p>Current network: <strong>{escape(current_ssid or "None")}</strong></p><form method="post" action="/setup/wifi"><label>Wi-Fi network</label><select name="ssid" required>{options}</select><label>Password</label><input type="password" name="password"><button>Connect</button></form></article></main></body></html>'
