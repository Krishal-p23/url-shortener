# Hardware Distributed URL Shortener

## Overview

This repository contains a portfolio project for a URL shortening service built incrementally with Python, FastAPI, PostgreSQL, Redis, SQLAlchemy, Alembic, and React.

## Current Stage

The current implementation includes:

- FastAPI application with automatic OpenAPI documentation
- Environment-backed configuration using Pydantic Settings

## Database Design

- Compact Base62 short-code generation.
- PostgreSQL-backed URL mappings and click events.
- Redis cache-aside redirect lookup with graceful fallback.
## Redirection
- Soft deletion with cache invalidation.
- Minimal React client with copy and analytics actions.
- Async database access, migrations, validation, tests, and Docker Compose.

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic Settings, SQLAlchemy 2 async, asyncpg, Alembic.
- **Data services:** PostgreSQL 17 and Redis 7.
- **Frontend:** React, Vite, Fetch API.
- **Testing:** pytest, pytest-asyncio, Vitest, React Testing Library.
- **Operations:** Docker and Docker Compose.

## Project Structure

```text
backend/app/       FastAPI routes, services, models, schemas, cache, and database setup
backend/alembic/   PostgreSQL migrations
backend/tests/     Backend behavior tests
frontend/src/      React application and API client
docs/              Technical project report
docker-compose.yml Local PostgreSQL, Redis, backend, and frontend stack
```
## Redis Caching Strategy
## Prerequisites

- Python 3.13+
- Node.js 24+ and npm
## Analytics
- Docker Desktop for Compose execution

## Installation

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

## Running PostgreSQL and Redis

## Example API Requests and Responses

Start the development server:

```powershell
uvicorn app.main:app --reload
```

Check the service at <http://127.0.0.1:8000/health> or open the interactive API documentation at <http://127.0.0.1:8000/docs>.

## Testing

Run backend tests:

```powershell
pytest
```

Run frontend tests and build:

```powershell
cd ..\frontend
npm test
npm run build
```

The test suite covers Base62, URL validation and creation, redirect cache behavior, Redis degradation, analytics, soft deletion, safe API errors, CORS preflight, and the frontend shortening/analytics flow.

## Performance Considerations

- SQLAlchemy uses a bounded async pool: 10 persistent connections, up to 20 overflow connections, and a 30-second acquisition timeout by default.
- Redis connections fail fast with a 0.5-second socket timeout, preserving PostgreSQL fallback behavior during cache outages.
- `urls.short_code` is unique and indexed for redirect/detail lookups.
- `click_events` has a composite `(url_id, clicked_at)` index for recent per-link analytics.
- The local Base62 benchmark can be run with `python -m scripts.benchmark_base62` from `backend`. On the development machine used for this checkpoint it completed 100,000 encodes in 0.0721 seconds, approximately 1,387,783 operations/second. This is a utility micro-benchmark, not an end-to-end service performance claim.

At higher traffic, stateless FastAPI instances can scale horizontally behind a load balancer. Redis absorbs hot redirect reads, PostgreSQL remains the source of truth, and analytics can later move to asynchronous ingestion or a separate reporting store if click volume becomes the dominant workload.

See [CHECKPOINT.md](CHECKPOINT.md) for the exact state and [TODO.md](TODO.md) for the remaining stages.

## Stage 2 Database Design

PostgreSQL is the source of truth. The `urls` table stores each short-code mapping, its lifecycle state, timestamps, and a denormalized click counter. The `click_events` table stores lightweight analytics events linked to `urls.id` with a foreign key. The unique index on `urls.short_code` makes redirect lookup and collision prevention efficient; indexes on `click_events.url_id` and `clicked_at` support per-link and time-based analytics queries.

## Environment Variables

Backend variables are documented in [backend/.env.example](backend/.env.example). Important values are `DATABASE_URL`, `REDIS_URL`, `PUBLIC_BASE_URL`, `ALLOWED_ORIGINS`, `REDIS_TTL_SECONDS`, and the database pool settings. Frontend configuration is documented in [frontend/.env.example](frontend/.env.example); `VITE_API_BASE_URL` selects the FastAPI origin.

## API Examples

Create a short URL:

```http
POST /api/v1/urls
Content-Type: application/json

{"url":"https://example.com/docs"}
```

```json
{
	"short_code": "1",
	"short_url": "http://localhost:8000/1",
	"original_url": "https://example.com/docs",
	"created_at": "2026-09-10T12:00:00Z"
}
```

Redirect with `GET /1`, inspect with `GET /api/v1/urls/1`, inspect analytics with `GET /api/v1/urls/1/analytics`, and soft-delete with `DELETE /api/v1/urls/1`.

## Stage 4 Redirection

The public redirect endpoint accepts a Base62 code at the root path, looks up an active mapping in PostgreSQL, and returns a `307 Temporary Redirect`. Missing, inactive, or malformed codes return `404`. Redis is intentionally not involved until Stage 5; this stage establishes the PostgreSQL fallback behavior that caching will wrap.

## Stage 5 Redis Caching

Redirects first check Redis using the key `url:{short_code}`. A cache hit returns the redirect without a PostgreSQL query. On a cache miss, the service queries PostgreSQL and stores the original URL in Redis for `REDIS_TTL_SECONDS` (one hour by default). Redis errors are logged and ignored, so PostgreSQL remains the source of truth and redirects continue to work when the cache is unavailable.

## Stage 6 Click Analytics

Each redirect records a `click_events` row with the URL ID, timestamp, user-agent, and referrer. The `urls.click_count` counter is incremented in the same transaction. Analytics are best-effort for the redirect path: an analytics write failure is rolled back and logged without blocking the redirect. `GET /api/v1/urls/{short_code}/analytics` returns the total counter and the 20 most recent events.

## REST API

- `POST /api/v1/urls`: validate and create a short URL.
- `GET /api/v1/urls/{short_code}`: return active URL details and click count.
- `GET /api/v1/urls/{short_code}/analytics`: return aggregate and recent click data.
- `DELETE /api/v1/urls/{short_code}`: soft-delete the mapping and invalidate its Redis entry.
- `GET /{short_code}`: redirect to the active original URL.

Deletion is intentionally a soft delete: it sets `is_active` to false, prevents future redirects, removes the cache entry, and preserves the URL row and click history for analytics. Unexpected database failures return a stable `503` response without exposing internal database details.

## Frontend

From the `frontend` directory:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

The Vite client runs at <http://localhost:5173> and calls the FastAPI backend at `VITE_API_BASE_URL` (default `http://localhost:8000`). It supports URL creation, copying the generated link, loading analytics, and visible loading/error states. FastAPI allows the Vite origin through `ALLOWED_ORIGINS`.

## Running with Docker

Install and start Docker Desktop, then from the repository root run:

```powershell
docker compose up --build
```

Compose starts PostgreSQL and Redis first, waits for their health checks, runs the Alembic migration in the backend container, and then starts FastAPI and the React preview server. The API is available at <http://localhost:8000> and the frontend at <http://localhost:5173>.

Stop the stack with:

```powershell
docker compose down
```

Add `-v` to remove the persisted PostgreSQL and Redis volumes when a clean local database is required.

## Documentation

See [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md) for the complete architecture, algorithms, database design, testing strategy, scalability discussion, security considerations, and limitations.

The final repository quality review is recorded in [docs/QUALITY_REVIEW.md](docs/QUALITY_REVIEW.md).

## Future Improvements

Authentication, rate limiting, abuse prevention, asynchronous analytics ingestion, observability, live integration tests, and production HTTPS deployment are described in the project report.

## Author / Project Information

This is a portfolio and interview-study project demonstrating practical backend engineering with FastAPI, PostgreSQL, Redis, REST APIs, caching, analytics, React, migrations, tests, and containerized local development.