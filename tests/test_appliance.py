from barprep_edge.appliance import determine_appliance_state
from barprep_edge.network import NetworkStatus


def test_setup_mode(monkeypatch, tmp_path) -> None:
    from barprep_edge import state
    monkeypatch.setattr(state.settings, "data_dir", tmp_path)
    result = determine_appliance_state(
        NetworkStatus(False, "wlan0", None, ["10.42.0.1"], None, True), False)
    assert result.code == "wifi_setup"
