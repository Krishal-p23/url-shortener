# CHECKPOINT 4 - COMPLETE

## Current checkpoint

- **Stage:** 4 - Short URL Redirection
- **Status:** Complete
- **Suggested commit:** `feat: add short URL redirection`

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
- `backend/app/api/__init__.py`
- `backend/app/api/routes/__init__.py`
- `backend/tests/__init__.py`
- `backend/tests/test_health.py`
- `backend/tests/test_models.py`
- `backend/tests/test_base62.py`
- `backend/tests/test_url_api.py`
- `backend/tests/test_url_service.py`
- `backend/tests/test_redirect_api.py`
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

- No Redis integration or caching yet.
- No Redis caching, analytics, or React frontend yet.
- CORS is represented in configuration but is not wired until the frontend stage.
- A live PostgreSQL integration test is still pending.
- URL creation requires PostgreSQL because the short-code source is the database sequence.

## Next stage

Stage 5 will add Redis caching, TTLs, cache misses, and graceful PostgreSQL fallback.