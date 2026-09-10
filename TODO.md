# TODO

## Remaining stages

- [x] Stage 2: Integrate PostgreSQL, SQLAlchemy, and Alembic.
- [x] Stage 3: Add Base62 encoding and URL creation.
- [x] Stage 4: Add short-code redirection.
- [x] Stage 5: Add Redis caching and PostgreSQL fallback.
- [x] Stage 6: Add click analytics.
- [x] Stage 7: Complete and harden the REST API.
- [ ] Stage 8: Add the minimal React frontend and CORS wiring.
- [ ] Stage 9: Expand behavior-focused tests.
- [ ] Stage 10: Add Docker and Docker Compose setup.
- [ ] Stage 11: Review performance, security, and scalability.
- [ ] Stage 12: Complete README and `docs/PROJECT_REPORT.md`.

## Stage 1 notes

- The application currently exposes only `GET /health`.
- Run the server from `backend` so `app.main:app` resolves correctly.

## Stage 2 notes

- Set `DATABASE_URL` to a reachable PostgreSQL database before running migrations.
- Run `alembic upgrade head` from `backend` to create the `urls` and `click_events` tables.
- PostgreSQL is the source of truth; Redis will be introduced as a cache in Stage 5.

## Stage 3 notes

- `POST /api/v1/urls` validates HTTP and HTTPS URLs with Pydantic.
- Short codes encode PostgreSQL sequence IDs with Base62 characters `0-9A-Za-z`.
- The live URL creation flow requires PostgreSQL and the Stage 2 migration.

## Stage 4 notes

- `GET /{short_code}` returns a `307` redirect for active mappings.
- Redirect lookup currently queries PostgreSQL directly.
- Missing, inactive, and malformed codes return `404`.

## Stage 5 notes

- Redis keys use the `url:{short_code}` pattern.
- Cached original URLs use a configurable one-hour default TTL.
- Redis failures are logged and do not prevent PostgreSQL fallback redirects.
- The live Redis service is not required for unit tests; a live integration check remains pending.

## Stage 6 notes

- Redirects record user-agent and referrer metadata without collecting IP addresses.
- Analytics writes are transactional and best-effort for redirect availability.
- `GET /api/v1/urls/{short_code}/analytics` returns totals and recent events.

## Stage 7 notes

- `GET /api/v1/urls/{short_code}` returns active URL details.
- `DELETE /api/v1/urls/{short_code}` soft-deletes mappings and invalidates Redis.
- Unexpected database errors use a safe `503` response.