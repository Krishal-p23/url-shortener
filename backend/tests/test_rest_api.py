from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api.routes import urls
from app.main import app


class FakeURL:
    id = 1
    short_code = "9IX"
    original_url = "https://example.com/docs"
    created_at = datetime(2026, 9, 10, tzinfo=timezone.utc)
    updated_at = datetime(2026, 9, 10, tzinfo=timezone.utc)
    click_count = 4
    is_active = True


async def fake_active_lookup(session: object, short_code: str):
    return FakeURL() if short_code == "9IX" else None


async def fake_deactivate(session: object, short_code: str):
    return FakeURL() if short_code == "9IX" else None


async def fake_cache_delete(short_code: str) -> None:
    return None


def test_get_url_details(monkeypatch) -> None:
    monkeypatch.setattr(urls, "get_active_url_by_code", fake_active_lookup)

    with TestClient(app) as client:
        response = client.get("/api/v1/urls/9IX")

    assert response.status_code == 200
    assert response.json()["short_url"] == "http://localhost:8000/9IX"
    assert response.json()["click_count"] == 4


def test_delete_url_soft_deactivates_and_invalidates_cache(monkeypatch) -> None:
    monkeypatch.setattr(urls, "deactivate_url", fake_deactivate)
    monkeypatch.setattr(urls, "delete_cached_url", fake_cache_delete)

    with TestClient(app) as client:
        response = client.delete("/api/v1/urls/9IX")

    assert response.status_code == 204
    assert response.content == b""


def test_management_api_rejects_malformed_code() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/urls/not-valid!")

    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}


def test_database_errors_use_safe_public_response(monkeypatch) -> None:
    async def database_failure(session: object, short_code: str):
        raise OperationalError("select", {}, Exception("secret database detail"))

    monkeypatch.setattr(urls, "get_active_url_by_code", database_failure)

    with TestClient(app) as client:
        response = client.get("/api/v1/urls/9IX")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database service unavailable"}