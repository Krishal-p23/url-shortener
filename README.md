# Hardware Distributed URL Shortener

## Overview

This repository contains a portfolio project for a URL shortening service built incrementally with Python, FastAPI, PostgreSQL, Redis, SQLAlchemy, Alembic, and React.

## Current Stage

The current implementation includes:

- FastAPI application with automatic OpenAPI documentation
- Environment-backed configuration using Pydantic Settings
- Basic startup and shutdown logging
- `GET /health` health-check endpoint
- Initial pytest setup
- Async SQLAlchemy engine and session dependency
- PostgreSQL URL and click-event schema with an Alembic migration
- Base62 encoding and PostgreSQL-sequence-backed short-code generation
- `POST /api/v1/urls` for validated URL creation
- `GET /{short_code}` for PostgreSQL-backed redirection
- Redis cache-aside lookup with PostgreSQL fallback

Click analytics and frontend functionality are intentionally scheduled for later checkpoints.

## Stage 1 Setup

From the `backend` directory, create and activate a virtual environment, then install dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

For the database-backed stages, PostgreSQL must be running and the database named `url_shortener` must exist. Apply the migration with:

```powershell
alembic upgrade head
```

Start the development server:

```powershell
uvicorn app.main:app --reload
```

Check the service at <http://127.0.0.1:8000/health> or open the interactive API documentation at <http://127.0.0.1:8000/docs>.

Run the tests:

```powershell
pytest
```

See [CHECKPOINT.md](CHECKPOINT.md) for the exact state and [TODO.md](TODO.md) for the remaining stages.

## Stage 2 Database Design

PostgreSQL is the source of truth. The `urls` table stores each short-code mapping, its lifecycle state, timestamps, and a denormalized click counter. The `click_events` table stores lightweight analytics events linked to `urls.id` with a foreign key. The unique index on `urls.short_code` makes redirect lookup and collision prevention efficient; indexes on `click_events.url_id` and `clicked_at` support per-link and time-based analytics queries.

## Stage 4 Redirection

The public redirect endpoint accepts a Base62 code at the root path, looks up an active mapping in PostgreSQL, and returns a `307 Temporary Redirect`. Missing, inactive, or malformed codes return `404`. Redis is intentionally not involved until Stage 5; this stage establishes the PostgreSQL fallback behavior that caching will wrap.

## Stage 5 Redis Caching

Redirects first check Redis using the key `url:{short_code}`. A cache hit returns the redirect without a PostgreSQL query. On a cache miss, the service queries PostgreSQL and stores the original URL in Redis for `REDIS_TTL_SECONDS` (one hour by default). Redis errors are logged and ignored, so PostgreSQL remains the source of truth and redirects continue to work when the cache is unavailable.