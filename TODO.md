# TODO

## Remaining stages

- [x] Stage 2: Integrate PostgreSQL, SQLAlchemy, and Alembic.
- [ ] Stage 3: Add Base62 encoding and URL creation.
- [ ] Stage 4: Add short-code redirection.
- [ ] Stage 5: Add Redis caching and PostgreSQL fallback.
- [ ] Stage 6: Add click analytics.
- [ ] Stage 7: Complete and harden the REST API.
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