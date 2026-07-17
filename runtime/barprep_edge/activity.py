from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings

_LOCK = threading.RLock()
MAX_EVENTS = 100


def activity_path() -> Path:
    return settings.data_dir / "activity.json"


def read_activity(limit: int = 20) -> list[dict[str, Any]]:
    with _LOCK:
        path = activity_path()
        if not path.exists():
            return []
        try:
            events = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(events, list):
            return []
        return list(reversed(events[-max(1, limit):]))


def record_activity(event: str, detail: str = "", level: str = "info") -> None:
    with _LOCK:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        path = activity_path()
        try:
            events = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        except (OSError, json.JSONDecodeError):
            events = []
        events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "detail": detail,
            "level": level,
        })
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(events[-MAX_EVENTS:], indent=2), encoding="utf-8")
        tmp.chmod(0o600)
        tmp.replace(path)
