from fastapi.testclient import TestClient

from app.api.routes import health as health_routes
from app.main import app
from app.services.health import DatabaseUnavailableError

client = TestClient(app)


def test_liveness_returns_service_metadata() -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "AI运营工作台"
    assert payload["version"] == "0.1.0"


def test_readiness_checks_database(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(health_routes, "check_database", lambda _: "connected")
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_readiness_returns_503_when_database_is_unavailable(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def unavailable(_):  # type: ignore[no-untyped-def]
        raise DatabaseUnavailableError("database unavailable")

    monkeypatch.setattr(health_routes, "check_database", unavailable)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "HTTP_503"
