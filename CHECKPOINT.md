# CHECKPOINT 9 - COMPLETE

## Current checkpoint

- **Stage:** 9 - Testing
- **Status:** Complete
- **Suggested commit:** `test: expand backend and frontend coverage`

## Working features

- FastAPI application starts with Uvicorn.
- `GET /health` returns the application status and environment.
- Settings load from environment variables and an optional backend `.env` file.
- Startup and shutdown events emit basic logs.
- FastAPI Swagger UI is available at `/docs`.
- The initial health endpoint test runs with pytest.
- Async SQLAlchemy engine and session factory are configured from `DATABASE_URL`.
- `urls` and `click_events` ORM models define the Stage 2 schema.
- Alembic is configured for asynchronous PostgreSQL migrations.
- The initial migration creates both tables, constraints, and lookup indexes.
- Model metadata tests verify the database contract without requiring PostgreSQL.
- Base62 encoding and decoding support the full `0-9A-Za-z` alphabet.
- URL creation validates HTTP and HTTPS URLs with Pydantic.
- `POST /api/v1/urls` returns a `201` response containing the short code, short URL, original URL, and creation timestamp.
- PostgreSQL sequence IDs are encoded as short codes, avoiding random collision coordination.
- Unique-constraint retry behavior is covered at the service layer.
- `GET /{short_code}` looks up active mappings in PostgreSQL and returns a `307` redirect.
- Missing, inactive, and malformed short codes return `404`.
- The lookup is isolated in a service so Redis caching can be inserted in Stage 5.
- Redis cache helpers use the `url:{short_code}` key pattern.
- Redirects check Redis before PostgreSQL and populate the cache after a database hit.
- Cached URLs use a configurable one-hour default TTL.
- Redis read and write failures degrade gracefully to PostgreSQL behavior.
- Redis connection pools close during application shutdown.
- Redirects record click events with timestamp, user-agent, and referrer metadata.
- The URL click counter increments in the same database transaction as the event.
- `GET /api/v1/urls/{short_code}/analytics` returns total clicks and the 20 most recent events.
- Analytics failures are rolled back and logged without blocking redirects.
- Redis cache values include the URL ID so cache hits can record analytics without a database lookup.
- `GET /api/v1/urls/{short_code}` returns active URL details and click count.
- `DELETE /api/v1/urls/{short_code}` performs a soft delete and invalidates Redis.
- API short-code validation consistently returns `404` for malformed or missing resources.
- Unexpected SQLAlchemy failures return a safe `503` response without internal database details.
- React frontend supports URL shortening, copy-to-clipboard, analytics loading, errors, and loading states.
- Vite frontend configuration uses `VITE_API_BASE_URL` with a localhost backend default.
- FastAPI CORS allows configured comma-separated origins, including the Vite development origin.
- Vitest and React Testing Library cover the frontend API client and shorten/analytics flow.
- Backend regression tests cover Redis failures and CORS preflight behavior.

## Files created

- `backend/app/__init__.py`
- `backend/app/config.py`
- `backend/app/main.py`
- `backend/app/db/base.py`
- `backend/app/db/session.py`
- `backend/app/models/url.py`
- `backend/app/models/click_event.py`
- `backend/app/models/__init__.py`
- `backend/app/db/__init__.py`
- `backend/app/utils/base62.py`
- `backend/app/schemas/url.py`
- `backend/app/services/url_service.py`
- `backend/app/api/router.py`
- `backend/app/api/routes/urls.py`
- `backend/app/api/routes/redirects.py`
- `backend/app/cache/__init__.py`
- `backend/app/cache/redis.py`
- `backend/app/api/routes/analytics.py`
- `backend/tests/test_rest_api.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/index.html`
- `frontend/vite.config.js`
- `frontend/.env.example`
- `frontend/src/main.jsx`
- `frontend/src/api.js`
- `frontend/src/App.jsx`
- `frontend/src/styles.css`
- `frontend/src/test-setup.js`
- `frontend/src/api.test.js`
- `frontend/src/App.test.jsx`
- `backend/app/api/__init__.py`
- `backend/app/api/routes/__init__.py`
- `backend/tests/__init__.py`
- `backend/tests/test_health.py`
- `backend/tests/test_models.py`
- `backend/tests/test_base62.py`
- `backend/tests/test_url_api.py`
- `backend/tests/test_url_service.py`
- `backend/tests/test_redirect_api.py`
- `backend/tests/test_redis_cache.py`
- `backend/tests/test_analytics_api.py`
- `backend/tests/test_analytics_service.py`
- `backend/tests/test_cors.py`
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/0001_create_url_tables.py`
- `.gitignore`
- `README.md`
- `CHECKPOINT.md`
- `TODO.md`

## How to run

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## How to test

From `backend` with the virtual environment active:

```powershell
pytest
```

Manual check: open <http://127.0.0.1:8000/health> and expect a JSON response with `status` set to `healthy`. A live PostgreSQL instance is required for `alembic upgrade head`, but not for the model tests or health endpoint.

Create a URL with:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/urls `
	-H "Content-Type: application/json" `
	-d '{"url":"https://example.com/docs"}'
```

## Known limitations

- No Docker deployment yet.
- A live PostgreSQL integration test is still pending.
- URL creation requires PostgreSQL because the short-code source is the database sequence.
- Live PostgreSQL and Redis integration checks are still pending.

## Next stage

Stage 10 will add Docker and Docker Compose setup for the backend, PostgreSQL, Redis, and frontend.