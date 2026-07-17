from fastapi.testclient import TestClient

from barprep_edge.drivers.base import OutputDevice
from barprep_edge.web import app as web_app_module


class FakeDriver:
    def discover(self) -> list[OutputDevice]:
        return [
            OutputDevice(
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
        ]


def test_dashboard_survives_connected_printer(monkeypatch, tmp_path) -> None:
    from barprep_edge import state

    monkeypatch.setattr(state.settings, "data_dir", tmp_path)
    monkeypatch.setattr(web_app_module, "get_printer_driver", lambda: FakeDriver())

    client = TestClient(web_app_module.create_app())
    response = client.get("/")

    assert response.status_code == 200
    assert "Brother QL-800" in response.text


def test_status_api_serializes_connected_printer(monkeypatch, tmp_path) -> None:
    from barprep_edge import state

    monkeypatch.setattr(state.settings, "data_dir", tmp_path)
    monkeypatch.setattr(web_app_module, "get_printer_driver", lambda: FakeDriver())

    client = TestClient(web_app_module.create_app())
    response = client.get("/api/status")

    assert response.status_code == 200
    printer = response.json()["printers"][0]
    assert printer["connection_uri"] == "usb://0x04f9:0x209b_TEST"
