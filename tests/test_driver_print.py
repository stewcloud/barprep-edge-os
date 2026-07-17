from __future__ import annotations

from barprep_edge.drivers.brother_ql import BrotherQLDriver


def test_driver_uses_compatibility_sender(monkeypatch) -> None:
    calls: list[tuple[object, str]] = []

    class Result:
        mode = "helpers.send"
        package_version = "test"

    def fake_send(instructions: object, uri: str, **kwargs: object) -> Result:
        calls.append((instructions, uri))
        return Result()

    monkeypatch.setattr(
        "barprep_edge.drivers.brother_ql.send_instructions",
        fake_send,
    )

    driver = BrotherQLDriver()
    png = driver.create_test_label("TEST", ["Line one"])
    driver.print_png(png, connection_uri="usb://test")

    assert calls
    assert calls[0][1] == "usb://test"
