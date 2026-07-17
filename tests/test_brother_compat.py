from __future__ import annotations

from barprep_edge.drivers import brother_compat


class FakeBackend:
    writes: list[object] = []
    disposed = False

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def write(self, instructions: object) -> None:
        self.writes.append(instructions)

    def dispose(self) -> None:
        self.disposed = True


def test_current_discovery_dictionary_is_normalized() -> None:
    raw = {
        "identifier": "usb://0x04f9:0x209b_TEST",
        "instance": object(),
    }
    assert (
        brother_compat.identifier_from_discovery_result(raw)
        == "usb://0x04f9:0x209b_TEST"
    )


def test_legacy_discovery_string_is_preserved() -> None:
    assert (
        brother_compat.identifier_from_discovery_result("usb://legacy")
        == "usb://legacy"
    )


def test_send_prefers_helpers_send(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_send(**kwargs: object) -> None:
        calls.append(kwargs)

    import brother_ql.backends.helpers as helpers

    monkeypatch.setattr(helpers, "send", fake_send)

    result = brother_compat.send_instructions(
        b"abc",
        "usb://printer",
    )

    assert result.mode == "helpers.send"
    assert calls[0]["printer_identifier"] == "usb://printer"
    assert calls[0]["backend_identifier"] == "pyusb"
    assert calls[0]["blocking"] is True
