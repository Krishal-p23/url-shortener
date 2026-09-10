from fastapi.testclient import TestClient

from app.main import app


def test_frontend_origin_can_make_api_preflight_request() -> None:
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/urls",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"