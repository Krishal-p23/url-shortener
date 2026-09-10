# CHECKPOINT 2 - COMPLETE

## Current checkpoint

- **Stage:** 2 - PostgreSQL and Database Layer
- **Status:** Complete
- **Suggested commit:** `feat: add PostgreSQL database layer`

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
- `backend/tests/__init__.py`
- `backend/tests/test_health.py`
- `backend/tests/test_models.py`
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

## Known limitations

- No Redis integration or caching yet.
- No URL creation, redirection, analytics, or React frontend yet.
- CORS is represented in configuration but is not wired until the frontend stage.
- A live PostgreSQL integration test is still pending.

## Next stage

Stage 3 will add Base62 encoding, collision-safe short-code generation, and the first URL creation API.