from __future__ import annotations

import json
import os
import re
import secrets
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .config import settings


PAIRING_FILENAME = "pairing.json"
PAIRING_CODE_PATTERN = re.compile(r"^[A-Z0-9]{4,12}$")


class PairingError(RuntimeError):
    """Raised when Edge cannot complete or validate pairing."""


@dataclass(slots=True)
class PairingState:
    paired: bool = False
    core_url: str = ""
    device_token: str = ""
    edge_id: str = ""
    station_id: str = ""
    station_name: str = ""
    paired_at: str = ""
    last_heartbeat_at: str = ""
    last_error: str = ""

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("device_token", None)
        data["has_device_token"] = bool(self.device_token)
        return data


def pairing_path() -> Path:
    return settings.data_dir / PAIRING_FILENAME


def _normalize_core_url(value: str) -> str:
    cleaned = value.strip().rstrip("/")
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise PairingError("BarPrep Core URL must begin with http:// or https://")
    return cleaned


def _normalize_pairing_code(value: str) -> str:
    cleaned = re.sub(r"[\s-]+", "", value.strip().upper())
    if not PAIRING_CODE_PATTERN.fullmatch(cleaned):
        raise PairingError(
            "Pairing code must contain 4–12 letters or numbers"
        )
    return cleaned


def load_pairing_state() -> PairingState:
    path = pairing_path()
    if not path.exists():
        return PairingState()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PairingError(f"Unable to read pairing state: {exc}") from exc

    allowed = {field.name for field in PairingState.__dataclass_fields__.values()}
    values = {key: value for key, value in payload.items() if key in allowed}
    return PairingState(**values)


def save_pairing_state(state: PairingState) -> None:
    path = pairing_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, temporary_name = tempfile.mkstemp(
        prefix=".pairing-",
        suffix=".json",
        dir=path.parent,
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(asdict(state), handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def clear_pairing_state() -> None:
    path = pairing_path()
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def create_pairing_request(
    *,
    core_url: str,
    pairing_code: str,
    device_id: str,
    friendly_name: str,
    version: str,
    capabilities: list[str],
    timeout_seconds: float = 15.0,
) -> PairingState:
    normalized_url = _normalize_core_url(core_url)
    normalized_code = _normalize_pairing_code(pairing_code)

    request_body = {
        "pairing_code": normalized_code,
        "device_id": device_id,
        "friendly_name": friendly_name,
        "software_version": version,
        "capabilities": capabilities,
        "pairing_nonce": secrets.token_urlsafe(18),
    }

    request = Request(
        f"{normalized_url}/api/v1/edge/pair",
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"BarPrep-Edge/{version}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = ""
        try:
            error_payload = json.loads(exc.read().decode("utf-8"))
            detail = str(error_payload.get("detail") or error_payload.get("error") or "")
        except Exception:
            detail = ""
        message = detail or f"BarPrep Core returned HTTP {exc.code}"
        raise PairingError(message) from exc
    except URLError as exc:
        raise PairingError(f"Unable to reach BarPrep Core: {exc.reason}") from exc
    except (TimeoutError, json.JSONDecodeError) as exc:
        raise PairingError(f"Invalid response from BarPrep Core: {exc}") from exc

    token = str(response_payload.get("device_token") or "").strip()
    edge_id = str(response_payload.get("edge_id") or "").strip()
    if not token or not edge_id:
        raise PairingError(
            "BarPrep Core did not return an edge ID and device token"
        )

    station = response_payload.get("station") or {}
    state = PairingState(
        paired=True,
        core_url=normalized_url,
        device_token=token,
        edge_id=edge_id,
        station_id=str(station.get("id") or ""),
        station_name=str(station.get("name") or "Unassigned"),
        paired_at=datetime.now(timezone.utc).isoformat(),
        last_error="",
    )
    save_pairing_state(state)
    return state
