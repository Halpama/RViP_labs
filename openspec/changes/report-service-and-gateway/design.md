# Design

## Context

The existing [reader-service](../../../apps/reader-service) owns the single
`readers` table and its Alembic migrations. It already has an async SQLAlchemy
model and a summary router, while the current Compose file exposes the API
directly and runs only one application container. The proposal and delta specs
define the externally visible split; this design describes how to preserve that
database ownership while introducing a second process and a gateway.

## Goals / Non-Goals

**Goals:**

- Reuse the existing reader table mapping in a separate async report service
  without importing migration code or creating tables.
- Keep report queries read-only and cover empty, mixed, and populated datasets.
- Make gateway-prefixed URLs work for API calls, Swagger UI, and OpenAPI JSON.
- Make startup deterministic: healthy PostgreSQL, successful migration, then both
  services, then nginx.
- Provide reproducible service tests, gateway integration checks, and a complete
  Postman scenario.

**Non-Goals:**

- Changing the database schema, adding tables, or moving Alembic ownership.
- Adding write endpoints, authentication, caching, or a second persistence
  model to report-service.
- Supporting direct host access to either application service after Compose
  migration.

## Decisions

### Separate read-only application with a shared table mapping

Create `apps/report-service/app` with the same small module boundaries as the
reader service (`config.py`, `db.py`, `models.py`, `schemas.py`, `routers/`,
`main.py`). Its `Reader` mapping mirrors the existing columns and its sessions
are used only by `select` statements. It has no Alembic directory and never
calls `metadata.create_all`.

The report service gets its own pinned `requirements.txt`, Dockerfile based on
`python:3.13.7-slim`, pytest configuration, and database-backed tests. A
separate mapping is preferred over importing reader-service code because the
containers must remain independently buildable and the report service must not
accidentally acquire write or migration dependencies.

### Move, rather than duplicate, the summary endpoint

Remove the reader-service reports router and its summary tests, then implement
the same aggregate query in report-service. This avoids two contracts that
could diverge and makes the modified `library-readers` delta an explicit
removal. The report list query returns the six specified columns in a response
schema suitable for JSON serialization.

### Safe environment discovery

Use the existing settings validation pattern, but keep `.env` discovery as a
bounded upward traversal from the module location (or equivalent loop over
parents), never a fixed `parents[N]` index. Compose supplies the service
`DATABASE_URL` explicitly as the `postgres:5432` URL; `.env` is only a local
fallback and is not interpolated into service environment entries.

### FastAPI root paths plus nginx prefix stripping

Instantiate each FastAPI app with its service root path (`/reader-service` or
`/report-service`) so generated documentation links and OpenAPI `servers`
reflect the public URL. Configure nginx locations with trailing-slash prefix
handling and `proxy_pass` targets ending at the upstream root, forwarding the
usual host and forwarding headers. Add explicit gateway error pages for 502 and
504 with a short JSON response, while preserving upstream status and bodies for
healthy requests.

The alternative of leaving `root_path` empty would make proxied Swagger assets
and OpenAPI links point to unprefixed paths. Exposing service ports on the host
would simplify local debugging but violates the single-entry-point contract.

### Compose startup and image pinning

Retain PostgreSQL `16.6-alpine` with a healthcheck. Build the existing
reader-service image once for `migrate` and `reader-service`; run migration with
`entrypoint: []` and `alembic upgrade head`, `restart: "no"`, and require
`service_completed_successfully` for both applications. Add report-service with
the same migration dependency, then make gateway depend on both services.
Publish only `127.0.0.1:8080` for nginx and `127.0.0.1:55432` for PostgreSQL.
Keep shell and nginx configuration files LF via `.gitattributes`.

### Verification through both service tests and Postman

Report-service tests use `TEST_DATABASE_URL` and share the existing fixture
pattern without silently skipping when the test database is available. Compose
validation checks image tags, dependency conditions, absent application host
ports, and gateway documentation. The Postman collection uses
`base_url=http://127.0.0.1:8080`, tests status and response bodies for every
endpoint, and stores the created reader id for the folder-level end-to-end
sequence.

## Risks / Trade-offs

- **[Risk]** The two SQLAlchemy mappings can drift as the reader schema evolves.
  → Keep the report model fields aligned with the authoritative reader model and
  add a schema-shape/report query test; future schema changes remain owned by
  reader-service.
- **[Risk]** Incorrect slash handling can produce broken gateway routes or
  redirects. → Test both API and docs paths through nginx and use explicit
  prefixed URLs in Postman.
- **[Risk]** A service may start before migrations are usable. → Gate both app
  containers on successful migration completion and keep PostgreSQL healthcheck
  as the migration prerequisite.
- **[Risk]** nginx upstream failures may return an opaque HTML page. → Configure
  JSON error responses for 502/504 and validate them with a stopped-upstream
  check.

## Migration Plan

1. Build the reader and report images, start PostgreSQL, and wait for its
   healthcheck.
2. Run the one-shot reader-service migration container to the current Alembic
   head; start both application containers only after it exits successfully.
3. Start nginx and validate both prefixed health/documentation paths, then run
   the service tests and Postman scenario.
4. Roll back by deploying the previous Compose and reader-service image; no
   database rollback is needed because this change has no schema migration.

## Open Questions

None. The user request fixes the public prefixes, image tags, ports, database
ownership, and required endpoint behavior.
