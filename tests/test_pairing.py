from pathlib import Path

import pytest

from barprep_edge import pairing


def test_pairing_state_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pairing.settings, "data_dir", tmp_path)

    state = pairing.PairingState(
        paired=True,
        core_url="https://barprep.example.com",
        device_token="secret-token",
        edge_id="edge-123",
        station_id="station-1",
        station_name="Prep Area",
    )
    pairing.save_pairing_state(state)

    saved = pairing.load_pairing_state()

    assert saved == state
    assert (tmp_path / "pairing.json").stat().st_mode & 0o777 == 0o600
    assert "device_token" not in saved.public_dict()
    assert saved.public_dict()["has_device_token"] is True


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("7qpk", "7QPK"),
        ("7Q-PK", "7QPK"),
        (" 7 q p k ", "7QPK"),
    ],
)
def test_pairing_code_normalization(raw: str, expected: str) -> None:
    assert pairing._normalize_pairing_code(raw) == expected


@pytest.mark.parametrize(
    "value",
    ["", "abc", "bad code!", "TOO-LONG-CODE-12345"],
)
def test_invalid_pairing_codes(value: str) -> None:
    with pytest.raises(pairing.PairingError):
        pairing._normalize_pairing_code(value)


@pytest.mark.parametrize(
    "value",
    ["barprep.example.com", "ftp://barprep.example.com", ""],
)
def test_invalid_core_urls(value: str) -> None:
    with pytest.raises(pairing.PairingError):
        pairing._normalize_core_url(value)
