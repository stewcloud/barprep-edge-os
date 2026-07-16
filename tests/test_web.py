from fastapi.testclient import TestClient

from barprep_edge.web.app import create_app


def test_status_endpoint(monkeypatch, tmp_path) -> None:
    from barprep_edge import state

    monkeypatch.setattr(state.settings, "data_dir", tmp_path)

    app = create_app()
    client = TestClient(app)

    response = client.get("/api/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["version"]
    assert payload["device"]["device_id"]
    assert "system" in payload
    assert "printers" in payload


def test_status_page(monkeypatch, tmp_path) -> None:
    from barprep_edge import state

    monkeypatch.setattr(state.settings, "data_dir", tmp_path)

    client = TestClient(create_app())
    response = client.get("/")

    assert response.status_code == 200
    assert "BarPrep Edge" in response.text
    assert "Device ID" in response.text


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
