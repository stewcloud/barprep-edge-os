from barprep_edge.system_info import collect_system_info, system_info_dict


def test_collect_system_info() -> None:
    info = collect_system_info()

    assert info.hostname
    assert info.kernel
    assert info.architecture
    assert info.uptime_seconds >= 0
    assert info.disk_total_bytes > 0
    assert info.disk_free_bytes >= 0


def test_system_info_dict() -> None:
    payload = system_info_dict()

    assert "hostname" in payload
    assert "uptime_seconds" in payload
    assert "ip_addresses" in payload
