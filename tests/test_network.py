from barprep_edge.network import _valid_ipv4


def test_valid_ipv4() -> None:
    assert _valid_ipv4("192.168.1.20")
    assert not _valid_ipv4("127.0.0.1")
    assert not _valid_ipv4("169.254.1.2")
