from barprep_edge.drivers.base import OutputDevice
from barprep_edge.drivers.brother_ql import _identifier_from_discovery_result


class FakeUsbDevice:
    """Represents a non-serializable live PyUSB handle."""


def test_extract_identifier_from_brother_dictionary() -> None:
    raw = {
        "identifier": "usb://0x04f9:0x209b_TEST",
        "instance": FakeUsbDevice(),
    }

    assert _identifier_from_discovery_result(raw) == "usb://0x04f9:0x209b_TEST"


def test_output_device_to_dict_contains_only_public_values() -> None:
    output = OutputDevice(
        id="usb://0x04f9:0x209b_TEST",
        name="Brother QL-800",
        driver="brother_ql",
        manufacturer="Brother",
        model="QL-800",
        connection="usb",
        connection_uri="usb://0x04f9:0x209b_TEST",
        ready=True,
        media_label="62",
        media_description="62 mm continuous",
    )

    payload = output.to_dict()

    assert payload["connection_uri"] == "usb://0x04f9:0x209b_TEST"
    assert payload["ready"] is True
    assert set(payload) == {
        "id",
        "name",
        "driver",
        "manufacturer",
        "model",
        "connection",
        "connection_uri",
        "ready",
        "media_label",
        "media_description",
        "detail",
    }


def test_identifier_rejects_unknown_object() -> None:
    try:
        _identifier_from_discovery_result(object())
    except ValueError as exc:
        assert "Unsupported Brother discovery result" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
