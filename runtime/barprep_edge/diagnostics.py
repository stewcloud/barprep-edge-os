from __future__ import annotations

import io
import json
import subprocess
import zipfile
from datetime import datetime, timezone

from .activity import read_activity
from .drivers.brother_compat import brother_package_version
from .network import network_status_dict
from .state import load_state
from .system_info import system_info_dict


def _command(*args: str) -> str:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    return (result.stdout + "\n" + result.stderr).strip()


def create_diagnostics_zip(printers: list[dict[str, object]]) -> bytes:
    buffer = io.BytesIO()
    safe_state = load_state().copy()
    if safe_state.get("device_secret"):
        safe_state["device_secret"] = "[REDACTED]"

    software = {
        "brother_ql_version": brother_package_version(),
        "python_packages": _command(
            "/opt/barprep-edge/.venv/bin/python",
            "-m",
            "pip",
            "freeze",
        ),
    }

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "type": "barprep-edge-diagnostics",
                },
                indent=2,
            ),
        )
        archive.writestr("state.json", json.dumps(safe_state, indent=2))
        archive.writestr("system.json", json.dumps(system_info_dict(), indent=2))
        archive.writestr("network.json", json.dumps(network_status_dict(), indent=2))
        archive.writestr("printers.json", json.dumps(printers, indent=2))
        archive.writestr("software.json", json.dumps(software, indent=2))
        archive.writestr("activity.json", json.dumps(read_activity(100), indent=2))
        archive.writestr("usb.txt", _command("lsusb"))
        archive.writestr(
            "service-log.txt",
            _command(
                "journalctl",
                "-u",
                "barprep-edge",
                "-n",
                "250",
                "--no-pager",
            ),
        )
        archive.writestr(
            "wifi-watchdog-log.txt",
            _command(
                "journalctl",
                "-u",
                "barprep-edge-wifi",
                "-n",
                "250",
                "--no-pager",
            ),
        )

    return buffer.getvalue()
