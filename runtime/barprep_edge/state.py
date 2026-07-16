from __future__ import annotations

import json
import secrets
import threading
from pathlib import Path
from typing import Any

from .config import settings

_LOCK = threading.RLock()


def state_path() -> Path:
    return settings.data_dir / "state.json"


def default_state() -> dict[str, Any]:
    return {
        "device_id": None,
        "device_secret": None,
        "paired": False,
        "pairing_code": None,
        "station_id": None,
        "station_name": None,
        "last_job_id": None,
        "last_error": None,
    }


def save_state(state: dict[str, Any]) -> None:
    with _LOCK:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        target = state_path()
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(target)


def load_state() -> dict[str, Any]:
    with _LOCK:
        target = state_path()
        if not target.exists():
            state = default_state()
            save_state(state)
            return state

        try:
            stored = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            stored = {}

        return {**default_state(), **stored}


def patch_state(**updates: Any) -> dict[str, Any]:
    state = load_state()
    state.update(updates)
    save_state(state)
    return state


def ensure_identity() -> dict[str, Any]:
    state = load_state()

    if not state["device_id"]:
        state["device_id"] = secrets.token_hex(8)

    if not state["device_secret"]:
        state["device_secret"] = secrets.token_urlsafe(32)

    save_state(state)
    return state
