from __future__ import annotations

from html import escape
from typing import Any


def _format_duration(seconds: int) -> str:
    days, remainder = divmod(max(0, seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "Unavailable"
    units = ["B", "KB", "MB", "GB", "TB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def render_status_page(
    *,
    version: str,
    state: dict[str, Any],
    system: dict[str, Any],
    printers: list[dict[str, Any]],
) -> str:
    paired = bool(state.get("paired"))
    printer_ready = any(bool(item.get("ready")) for item in printers)
    network_ready = bool(system.get("ip_addresses"))

    status_text = "Ready" if network_ready else "Needs setup"
    status_class = "ready" if network_ready else "warning"

    printer_rows = ""
    if printers:
        for printer in printers:
            ready = bool(printer.get("ready"))
            printer_rows += f"""
            <div class="device-row">
              <div>
                <strong>{escape(str(printer.get("name", "Printer")))}</strong>
                <span>{escape(str(printer.get("model", "")))}</span>
              </div>
              <span class="pill {'ready' if ready else 'offline'}">
                {'Ready' if ready else 'Not detected'}
              </span>
            </div>
            """
    else:
        printer_rows = """
        <div class="empty-state">
          Connect a Brother QL-800 to the Pi's USB data port.
        </div>
        """

    memory_total = system.get("memory_total_bytes")
    memory_available = system.get("memory_available_bytes")
    memory_used = None
    if isinstance(memory_total, int) and isinstance(memory_available, int):
        memory_used = memory_total - memory_available

    ips = system.get("ip_addresses") or []
    ip_text = ", ".join(escape(str(ip)) for ip in ips) if ips else "Not connected"
    temp = system.get("cpu_temperature_c")
    temp_text = f"{temp}°C" if temp is not None else "Unavailable"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="refresh" content="30">
  <title>BarPrep Edge</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f3f1eb;
      --card: #ffffff;
      --ink: #171714;
      --muted: #69675f;
      --line: #dfddd6;
      --accent: #171714;
      --ready: #177245;
      --ready-bg: #e5f5ec;
      --warning: #9a5b00;
      --warning-bg: #fff1d5;
      --offline: #8d2e2e;
      --offline-bg: #fbe8e8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
                   "Segoe UI", sans-serif;
    }}
    main {{
      width: min(880px, calc(100% - 32px));
      margin: 32px auto 64px;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 24px;
      margin-bottom: 24px;
    }}
    .brand {{ display: flex; gap: 14px; align-items: center; }}
    .mark {{
      width: 48px;
      height: 48px;
      border-radius: 13px;
      background: var(--accent);
      color: white;
      display: grid;
      place-items: center;
      font-weight: 800;
      letter-spacing: -.04em;
    }}
    h1 {{ margin: 0; font-size: clamp(1.7rem, 4vw, 2.4rem); }}
    .subtitle {{ margin: 4px 0 0; color: var(--muted); }}
    .pill {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 7px 11px;
      font-size: .8rem;
      font-weight: 750;
      white-space: nowrap;
    }}
    .pill.ready {{ color: var(--ready); background: var(--ready-bg); }}
    .pill.warning {{ color: var(--warning); background: var(--warning-bg); }}
    .pill.offline {{ color: var(--offline); background: var(--offline-bg); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 8px 24px rgba(0,0,0,.035);
    }}
    .card.wide {{ grid-column: 1 / -1; }}
    .card h2 {{
      margin: 0 0 17px;
      font-size: 1rem;
      letter-spacing: .01em;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0,1fr));
      gap: 12px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 13px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: .78rem;
      margin-bottom: 5px;
    }}
    .metric strong {{ font-size: .98rem; overflow-wrap: anywhere; }}
    .device-row {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      padding: 14px 0;
      border-top: 1px solid var(--line);
    }}
    .device-row:first-of-type {{ border-top: 0; padding-top: 0; }}
    .device-row:last-of-type {{ padding-bottom: 0; }}
    .device-row strong, .device-row span {{ display: block; }}
    .device-row div span {{
      color: var(--muted);
      font-size: .82rem;
      margin-top: 3px;
    }}
    .empty-state {{
      color: var(--muted);
      border: 1px dashed var(--line);
      border-radius: 12px;
      padding: 18px;
    }}
    footer {{
      color: var(--muted);
      font-size: .78rem;
      margin-top: 18px;
      text-align: center;
    }}
    @media (max-width: 680px) {{
      main {{ margin-top: 20px; }}
      header {{ align-items: center; }}
      .grid {{ grid-template-columns: 1fr; }}
      .card.wide {{ grid-column: auto; }}
      .metric-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
    @media (max-width: 420px) {{
      .metric-grid {{ grid-template-columns: 1fr; }}
      .device-row {{ align-items: flex-start; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <div class="brand">
      <div class="mark">BP</div>
      <div>
        <h1>BarPrep Edge</h1>
        <p class="subtitle">{escape(str(system.get("hostname", "barprep-edge")))}</p>
      </div>
    </div>
    <span class="pill {status_class}">{status_text}</span>
  </header>

  <section class="grid">
    <article class="card">
      <h2>Edge identity</h2>
      <div class="metric-grid">
        <div class="metric"><span>Device ID</span><strong>{escape(str(state.get("device_id") or "Generating…"))}</strong></div>
        <div class="metric"><span>Runtime</span><strong>{escape(version)}</strong></div>
        <div class="metric"><span>Pairing</span><strong>{'Paired' if paired else 'Not paired'}</strong></div>
        <div class="metric"><span>Station</span><strong>{escape(str(state.get("station_name") or "Not assigned"))}</strong></div>
      </div>
    </article>

    <article class="card">
      <h2>Network</h2>
      <div class="metric-grid">
        <div class="metric"><span>Hostname</span><strong>{escape(str(system.get("hostname")))}</strong></div>
        <div class="metric"><span>Address</span><strong>{ip_text}</strong></div>
        <div class="metric"><span>Local URL</span><strong>barprep-edge.local:8787</strong></div>
        <div class="metric"><span>Status</span><strong>{'Connected' if network_ready else 'Offline'}</strong></div>
      </div>
    </article>

    <article class="card wide">
      <h2>Printer</h2>
      {printer_rows}
    </article>

    <article class="card">
      <h2>System</h2>
      <div class="metric-grid">
        <div class="metric"><span>Uptime</span><strong>{_format_duration(int(system.get("uptime_seconds") or 0))}</strong></div>
        <div class="metric"><span>CPU temperature</span><strong>{temp_text}</strong></div>
        <div class="metric"><span>Memory used</span><strong>{_format_bytes(memory_used)}</strong></div>
        <div class="metric"><span>Memory total</span><strong>{_format_bytes(memory_total)}</strong></div>
      </div>
    </article>

    <article class="card">
      <h2>Storage and software</h2>
      <div class="metric-grid">
        <div class="metric"><span>Disk free</span><strong>{_format_bytes(system.get("disk_free_bytes"))}</strong></div>
        <div class="metric"><span>Architecture</span><strong>{escape(str(system.get("architecture")))}</strong></div>
        <div class="metric"><span>Kernel</span><strong>{escape(str(system.get("kernel")))}</strong></div>
        <div class="metric"><span>Python</span><strong>{escape(str(system.get("python_version")))}</strong></div>
      </div>
    </article>

    <article class="card wide">
      <h2>Recent activity</h2>
      <div class="metric-grid">
        <div class="metric"><span>Last print job</span><strong>{escape(str(state.get("last_job_id") or "None"))}</strong></div>
        <div class="metric"><span>Last error</span><strong>{escape(str(state.get("last_error") or "None"))}</strong></div>
      </div>
    </article>
  </section>
  <footer>BarPrep Edge OS refreshes this page every 30 seconds.</footer>
</main>
</body>
</html>"""
