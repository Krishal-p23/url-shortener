from fastapi.testclient import TestClient

from app.api.routes import redirects
from app.cache.redis import CachedURL
from app.main import app


class FakeURL:
    id = 1
    original_url = "https://example.com/destination"


async def fake_lookup(session: object, short_code: str) -> FakeURL | None:
    if short_code == "9IX":
        return FakeURL()
    return None


async def cache_miss(short_code: str) -> None:
    return None


async def cache_write(short_code: str, url_id: int, original_url: str) -> None:
    return None


async def record_click(*args) -> None:
    return None


def test_redirects_active_short_code(monkeypatch) -> None:
    monkeypatch.setattr(redirects, "get_active_url_by_code", fake_lookup)
    monkeypatch.setattr(redirects, "get_cached_url", cache_miss)
    monkeypatch.setattr(redirects, "cache_url", cache_write)
    monkeypatch.setattr(redirects, "record_click", record_click)

    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/9IX")

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/destination"


async def cache_hit(short_code: str) -> CachedURL:
    return CachedURL(1, "https://cached.example.com/destination")


def test_redirect_uses_cached_url_without_database_lookup(monkeypatch) -> None:
    async def database_must_not_run(session: object, short_code: str):
        raise AssertionError("database lookup should not run on a cache hit")

    monkeypatch.setattr(redirects, "get_cached_url", cache_hit)
    monkeypatch.setattr(redirects, "get_active_url_by_code", database_must_not_run)
    monkeypatch.setattr(redirects, "record_click", record_click)

    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/9IX")

    assert response.status_code == 307
    assert response.headers["location"] == "https://cached.example.com/destination"


def test_redirect_returns_not_found_for_missing_or_inactive_code(monkeypatch) -> None:
    monkeypatch.setattr(redirects, "get_active_url_by_code", fake_lookup)

    with TestClient(app) as client:
        response = client.get("/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}


def test_redirect_rejects_malformed_short_code() -> None:
    with TestClient(app) as client:
        response = client.get("/not-valid!")

    assert response.status_code == 404