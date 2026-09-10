# Hardware Distributed URL Shortener

## 1. Abstract

This project is a URL shortening service built as a small, understandable distributed application. A user submits a long HTTP or HTTPS URL, the service creates a compact Base62 code, stores the mapping in PostgreSQL, and redirects visitors through a Redis-assisted lookup path. Redirects record lightweight click analytics, while a minimal React frontend provides URL creation and analytics inspection.

The design intentionally uses a few strong boundaries rather than many services: PostgreSQL is the source of truth, Redis is only a cache, FastAPI owns the HTTP contract, and React is a thin client.

## 2. Problem and Objectives

Long URLs are difficult to share and obscure the useful identity of a link. The service solves this by mapping a short public code to an original URL. The objectives were to demonstrate:

- REST API design and request validation.
- Relational schema design and migrations.
- Compact identifier generation with collision safety.
- Cache-aside reads and graceful dependency failure.
- Click analytics without collecting unnecessary personal data.
- Async Python, connection pooling, testing, and local container orchestration.

## 3. System Architecture

```text
Browser
  |
  v
React/Vite frontend ---- POST/GET analytics ----> FastAPI
                                                   |
                         redirect lookup ---------+--------> Redis cache
                                                   |
                                                   +--------> PostgreSQL
                                                               |
                                                               +--> urls
                                                               +--> click_events
```

The frontend calls the backend at `VITE_API_BASE_URL`. The backend validates input with Pydantic, executes database work through async SQLAlchemy, and uses Redis only for hot redirect data. PostgreSQL stores durable URL mappings and analytics. Docker Compose provides the four runtime services locally: PostgreSQL, Redis, backend, and frontend.

## 4. Request Flows

### Create

1. The client sends `POST /api/v1/urls` with a URL.
2. `AnyHttpUrl` validation accepts HTTP/HTTPS URL input and rejects malformed data.
3. PostgreSQL allocates the next `urls.id` sequence value.
4. That integer is encoded with Base62 and stored as `short_code`.
5. The unique database constraint protects the mapping.
6. The API returns the short code, public URL, original URL, and timestamp.

### Redirect

1. A visitor requests `GET /{short_code}`.
2. The route rejects malformed codes with `404`.
3. Redis checks `url:{short_code}`.
4. A cache hit supplies the destination and URL ID immediately.
5. A miss queries active PostgreSQL data and populates Redis with a one-hour TTL.
6. The service records a click event and returns a `307 Temporary Redirect`.
7. Redis failures are logged and ignored, so PostgreSQL remains the fallback.

### Analytics

`GET /api/v1/urls/{short_code}/analytics` reads the denormalized total from `urls.click_count` and fetches up to 20 recent events ordered by timestamp. Redirect analytics writes are transactional but best-effort for availability: an analytics write failure is rolled back and does not block a valid redirect.

## 5. URL Shortening Algorithm

Base62 uses 62 symbols: `0-9`, `A-Z`, and `a-z`. An integer is repeatedly divided by 62; each remainder selects one character, and the remainders are read in reverse. This gives shorter text than decimal for the same positive integer.

The project uses the PostgreSQL primary-key sequence as the integer source. This is preferable to random strings here because the database already allocates sequence values atomically under concurrency. The numeric ID is encoded after allocation, and `short_code` also has a unique constraint. The service retains a bounded retry loop for an unexpected integrity conflict.

The Base62 utility is in `backend/app/utils/base62.py`; allocation is in `backend/app/services/url_service.py`.

## 6. Database Design

### `urls`

- `id`: integer primary key and sequence source.
- `original_url`: durable destination.
- `short_code`: unique indexed public identifier.
- `created_at`, `updated_at`: timezone-aware lifecycle timestamps.
- `click_count`: denormalized fast aggregate.
- `is_active`: soft-delete state.

### `click_events`

- `id`: event primary key.
- `url_id`: foreign key to `urls.id` with cascade deletion.
- `clicked_at`: timezone-aware event timestamp.
- `user_agent`: bounded 512-character metadata.
- `referrer`: optional referrer metadata.

The migrations are `0001_create_url_tables` and `0002_add_analytics_lookup_index`. The composite `(url_id, clicked_at)` index supports the analytics query that filters by URL and returns recent events.

Textual relationship:

```text
urls 1 -------- * click_events
```

Alembic owns schema changes; the application does not create tables at runtime. The Docker backend runs `alembic upgrade head` before starting Uvicorn.

## 7. Redis Caching

Redis is intentionally not a primary store. Each cache value contains the URL row ID and original destination as JSON under `url:{short_code}`. The ID is cached so a cache-hit redirect can record analytics without another lookup.

The cache uses a one-hour default TTL. Deleting a URL removes its cache entry. Redis has a 0.5-second socket timeout and catches Redis errors around reads, writes, and deletes. This makes cache loss a latency/degradation event rather than a correctness failure.

## 8. API Design

- `GET /health`: process health response.
- `POST /api/v1/urls`: create a validated short URL; returns `201`.
- `GET /api/v1/urls/{short_code}`: retrieve active URL details.
- `GET /api/v1/urls/{short_code}/analytics`: retrieve total and recent clicks.
- `DELETE /api/v1/urls/{short_code}`: soft-delete; returns `204`.
- `GET /{short_code}`: public redirect; returns `307`.

Malformed or missing short codes return `404`. Unexpected SQLAlchemy failures return a stable `503` message without exposing database internals. FastAPI exposes OpenAPI documentation at `/docs`.

## 9. Frontend

The React client is deliberately small. It provides a URL input, creation action, generated short URL, copy action, analytics action, loading states, and visible errors. `frontend/src/api.js` contains the Fetch API boundary. CORS permits the configured Vite origin, normally `http://localhost:5173`.

## 10. Testing Strategy

Backend pytest coverage includes Base62 round trips, Pydantic validation, creation behavior, collision retry, redirect cache hit/miss behavior, Redis failures, click recording, analytics responses, soft deletion, safe database errors, and CORS preflight. Frontend Vitest coverage checks API request contracts, API error display, and the shorten-to-analytics user flow.

Validated results for this checkpoint:

- Backend: 29 tests passed.
- Frontend: 4 tests passed.
- Frontend production build passed.
- Alembic offline SQL generation passed.
- Compose configuration parsing passed.
- Base62 micro-benchmark: 100,000 encodes in 0.0721 seconds on the development machine.

Live PostgreSQL/Redis integration and Docker image execution were not validated in this environment. Docker image building was blocked because Docker Desktop's Linux engine was unavailable.

## 11. Performance and Scalability

The async SQLAlchemy engine uses a bounded pool: 10 persistent connections, up to 20 overflow connections, and a 30-second acquisition timeout. These are configuration defaults, not universal production values; they should be tuned against database capacity and measured traffic.

At approximately 100 requests per minute, one backend instance with PostgreSQL and Redis is sufficient. At 10,000 requests per minute, multiple stateless FastAPI instances can sit behind a load balancer, with Redis absorbing repeated redirect reads and PostgreSQL handling durable writes. At much higher redirect volume, cache hit rate, Redis memory/eviction policy, PostgreSQL connection limits, and analytics write pressure become the primary concerns.

Analytics currently writes synchronously to PostgreSQL to keep the project understandable and transactional. At larger scale, a queue or append-only event pipeline could decouple redirect latency from reporting workloads, followed by aggregation into a reporting store.

## 12. Security and Privacy

- URL input is validated through Pydantic and ORM parameters prevent SQL injection.
- Secrets and service URLs are environment-configured rather than hardcoded in application logic.
- Short-code input is restricted to Base62 characters and bounded length.
- CORS is explicitly configured instead of allowing every origin.
- Internal database errors are logged server-side and sanitized in responses.
- Analytics stores user-agent and referrer only; IP addresses are not collected.
- Production deployments still need authentication for management endpoints, rate limiting, abuse detection, HTTPS, secret management, and stricter origin configuration.

## 13. Key Decisions and Limitations

FastAPI was selected for typed async HTTP APIs and generated documentation. PostgreSQL provides transactions, constraints, indexes, and durable source-of-truth storage. Redis improves repeated redirect latency but remains disposable. SQLAlchemy provides ORM mapping and async connection management; Alembic makes schema evolution reproducible. React is limited to the workflow needed to demonstrate API integration.

The project does not include authentication, rate limiting, asynchronous analytics ingestion, multi-region replication, or a production load benchmark. The Base62 result measures only encoding utility speed; it is not a claim about requests per second.

## 14. Future Improvements

- Add authentication and ownership for management endpoints.
- Add rate limiting and abuse-safe URL policy.
- Add live PostgreSQL/Redis integration tests in CI.
- Add a real HTTP load test with controlled infrastructure.
- Move analytics ingestion off the redirect request path at higher volume.
- Add structured logs, metrics, tracing, and alerting.
- Deploy behind HTTPS with managed PostgreSQL and Redis.

## 15. Study Checklist

An interview explanation should be able to trace one request through React, FastAPI, Redis, PostgreSQL, and the redirect response; explain why PostgreSQL is authoritative; explain how sequence IDs become Base62 codes; describe cache hit/miss and failure behavior; identify the database indexes; and state which performance claims were actually measured.