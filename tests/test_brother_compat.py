from barprep_edge.drivers import brother_compat

def test_current_discovery_dictionary_is_normalized() -> None:
    raw = {"identifier": "usb://0x04f9:0x209b_TEST", "instance": object()}
    assert brother_compat.identifier_from_discovery_result(raw) == "usb://0x04f9:0x209b"

def test_malformed_ql800_serial_suffix_is_removed() -> None:
    raw = {"identifier": "usb://0x04f9:0x209b_Љ", "instance": object()}
    assert brother_compat.identifier_from_discovery_result(raw) == "usb://0x04f9:0x209b"

def test_send_normalizes_identifier_before_helpers_send(monkeypatch) -> None:
    calls = []
    def fake_send(**kwargs):
        calls.append(kwargs)
    import brother_ql.backends.helpers as helpers
    monkeypatch.setattr(helpers, "send", fake_send)
    result = brother_compat.send_instructions(b"abc", "usb://0x04f9:0x209b_Љ")
    assert result.mode == "helpers.send"
    assert calls[0]["printer_identifier"] == "usb://0x04f9:0x209b"
