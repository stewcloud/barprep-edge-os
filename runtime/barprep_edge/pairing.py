from __future__ import annotations

import json
import os
import re
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
PAIRING_CODE_PATTERN = re.compile(r"^\d{6}$")


class PairingError(RuntimeError):
    """Raised when Edge cannot complete or validate pairing."""


@dataclass(slots=True)
class PairingState:
    paired: bool = False
    pending: bool = False
    core_url: str = ""
    device_token: str = ""
    edge_id: str = ""
    device_uuid: str = ""
    pairing_code: str = ""
    claim_token: str = ""
    approval_status: str = ""
    station_id: str = ""
    station_name: str = ""
    paired_at: str = ""
    last_heartbeat_at: str = ""
    last_error: str = ""

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("device_token", None)
        data.pop("claim_token", None)
        data["has_device_token"] = bool(self.device_token)
        data["pairing_code_display"] = (
            f"{self.pairing_code[:3]}-{self.pairing_code[3:]}"
            if len(self.pairing_code) == 6
            else self.pairing_code
        )
        return data


def pairing_path() -> Path:
    return settings.data_dir / PAIRING_FILENAME


def _normalize_core_url(value: str) -> str:
    cleaned = value.strip().rstrip("/")
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise PairingError("BarPrep Core URL must begin with http:// or https://")
    return cleaned


def _request_json(
    url: str,
    payload: dict[str, Any],
    version: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"BarPrep-Edge/{version}",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = ""
        try:
            payload = json.loads(exc.read().decode("utf-8"))
            detail = str(payload.get("detail") or payload.get("error") or "")
        except Exception:
            pass
        raise PairingError(detail or f"BarPrep Core returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise PairingError(f"Unable to reach BarPrep Core: {exc.reason}") from exc
    except (TimeoutError, json.JSONDecodeError) as exc:
        raise PairingError(f"Invalid response from BarPrep Core: {exc}") from exc


def load_pairing_state() -> PairingState:
    path = pairing_path()
    if not path.exists():
        return PairingState()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PairingError(f"Unable to read pairing state: {exc}") from exc
    allowed = {field.name for field in PairingState.__dataclass_fields__.values()}
    return PairingState(**{k: v for k, v in payload.items() if k in allowed})


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
    try:
        pairing_path().unlink()
    except FileNotFoundError:
        pass


def create_pairing_request(
    *,
    core_url: str,
    device_id: str,
    friendly_name: str,
    version: str,
    capabilities: list[str],
    timeout_seconds: float = 15.0,
) -> PairingState:
    normalized_url = _normalize_core_url(core_url)
    response = _request_json(
        f"{normalized_url}/api/edge/register",
        {
            "device_uuid": device_id,
            "device_name": friendly_name,
            "software_version": version,
            "capabilities": capabilities,
        },
        version,
        timeout_seconds,
    )

    pairing_code = re.sub(r"\D", "", str(response.get("pairing_code") or ""))
    claim_token = str(response.get("claim_token") or "").strip()
    if not PAIRING_CODE_PATTERN.fullmatch(pairing_code) or not claim_token:
        raise PairingError(
            "BarPrep Core did not return a six-digit pairing code and claim token"
        )

    state = PairingState(
        paired=False,
        pending=True,
        core_url=normalized_url,
        edge_id=str(response.get("device_id") or ""),
        device_uuid=device_id,
        pairing_code=pairing_code,
        claim_token=claim_token,
        approval_status="pending",
        last_error="",
    )
    save_pairing_state(state)
    return state


def check_pairing_status(
    *,
    version: str,
    timeout_seconds: float = 15.0,
) -> PairingState:
    state = load_pairing_state()
    if state.paired:
        return state
    if not state.pending or not state.core_url or not state.claim_token:
        raise PairingError("No pending pairing request exists")

    response = _request_json(
        f"{state.core_url}/api/edge/pair-status",
        {
            "device_uuid": state.device_uuid,
            "claim_token": state.claim_token,
        },
        version,
        timeout_seconds,
    )

    status = str(response.get("approval_status") or "pending")
    state.approval_status = status

    if status == "pending":
        save_pairing_state(state)
        return state

    if status == "rejected":
        state.pending = False
        state.last_error = "Pairing request was rejected in BarPrep Core"
        save_pairing_state(state)
        return state

    api_key = str(response.get("api_key") or "").strip()
    if status == "approved" and api_key:
        state.paired = True
        state.pending = False
        state.device_token = api_key
        state.edge_id = str(response.get("device_id") or state.edge_id)
        state.pairing_code = ""
        state.claim_token = ""
        state.paired_at = datetime.now(timezone.utc).isoformat()
        state.last_error = ""
        save_pairing_state(state)
        return state

    if status == "paired":
        state.last_error = (
            "Core reports paired, but this Edge does not have its API key. "
            "Reset pairing on both sides."
        )
        save_pairing_state(state)
        return state

    raise PairingError(f"Unexpected pairing status: {status}")
