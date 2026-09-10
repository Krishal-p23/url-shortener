from fastapi.testclient import TestClient

from app.api.routes import redirects
from app.main import app


class FakeURL:
    original_url = "https://example.com/destination"


async def fake_lookup(session: object, short_code: str) -> FakeURL | None:
    if short_code == "9IX":
        return FakeURL()
    return None


def test_redirects_active_short_code(monkeypatch) -> None:
    monkeypatch.setattr(redirects, "get_active_url_by_code", fake_lookup)

    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/9IX")

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/destination"


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