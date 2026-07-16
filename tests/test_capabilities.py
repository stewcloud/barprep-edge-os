from barprep_edge.capabilities import Capability, capability_values


def test_default_capabilities() -> None:
    values = capability_values()

    assert Capability.LABEL_PRINTING.value in values
    assert Capability.USB_PRINTER.value in values
    assert Capability.WIFI.value in values
    assert Capability.MDNS.value in values
    assert len(values) == len(set(values))
