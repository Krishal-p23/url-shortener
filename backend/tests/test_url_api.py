from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.routes import urls as url_routes
from app.main import app


class FakeURL:
    short_code = "9IX"
    original_url = "https://example.com/docs"
    created_at = datetime(2026, 9, 10, tzinfo=timezone.utc)


async def fake_create_url(session: object, original_url: str) -> FakeURL:
    assert original_url == "https://example.com/docs"
    return FakeURL()


def test_create_url_rejects_non_http_urls() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/urls",
            json={"url": "ftp://example.com/file"},
        )

    assert response.status_code == 422


def test_create_url_returns_short_url(monkeypatch) -> None:
    monkeypatch.setattr(url_routes, "create_url", fake_create_url)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/urls",
            json={"url": "https://example.com/docs"},
        )

    assert response.status_code == 201
    assert response.json() == {
        "short_code": "9IX",
        "short_url": "http://localhost:8000/9IX",
        "original_url": "https://example.com/docs",
        "created_at": "2026-09-10T00:00:00Z",
    }