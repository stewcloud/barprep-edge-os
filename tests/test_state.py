from pathlib import Path

from barprep_edge import state


def test_identity_is_persistent(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(state.settings, "data_dir", tmp_path)

    first = state.ensure_identity()
    second = state.ensure_identity()

    assert first["device_id"]
    assert first["device_secret"]
    assert first["device_id"] == second["device_id"]
    assert first["device_secret"] == second["device_secret"]
