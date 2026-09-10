from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.routes import analytics
from app.main import app


class FakeURL:
    short_code = "9IX"
    click_count = 3


class FakeEvent:
    clicked_at = datetime(2026, 9, 10, tzinfo=timezone.utc)
    user_agent = "pytest-agent"
    referrer = "https://referrer.example"


async def fake_analytics(session: object, short_code: str):
    if short_code == "9IX":
        return FakeURL(), [FakeEvent()]
    return None, []


def test_analytics_returns_total_and_recent_clicks(monkeypatch) -> None:
    monkeypatch.setattr(analytics, "get_analytics", fake_analytics)

    with TestClient(app) as client:
        response = client.get("/api/v1/urls/9IX/analytics")

    assert response.status_code == 200
    assert response.json() == {
        "short_code": "9IX",
        "total_clicks": 3,
        "recent_clicks": [
            {
                "clicked_at": "2026-09-10T00:00:00Z",
                "user_agent": "pytest-agent",
                "referrer": "https://referrer.example",
            }
        ],
    }


def test_analytics_returns_not_found(monkeypatch) -> None:
    monkeypatch.setattr(analytics, "get_analytics", fake_analytics)

    with TestClient(app) as client:
        response = client.get("/api/v1/urls/missing/analytics")

    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}