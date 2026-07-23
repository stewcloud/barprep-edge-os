import json

import pytest

from barprep_edge import pairing


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return json.dumps(
            {
                "device_token": "token-123",
                "edge_id": "edge-123",
                "station": {"id": "station-1", "name": "Prep Area"},
            }
        ).encode("utf-8")


def test_create_pairing_request(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pairing.settings, "data_dir", tmp_path)
    monkeypatch.setattr(pairing, "urlopen", lambda request, timeout: FakeResponse())

    state = pairing.create_pairing_request(
        core_url="https://barprep.example.com/",
        pairing_code="7q-pk",
        device_id="device-1",
        friendly_name="Prep Printer",
        version="0.3.0-dev",
        capabilities=["print_png"],
    )

    assert state.paired is True
    assert state.core_url == "https://barprep.example.com"
    assert state.station_name == "Prep Area"
    assert pairing.load_pairing_state().device_token == "token-123"
