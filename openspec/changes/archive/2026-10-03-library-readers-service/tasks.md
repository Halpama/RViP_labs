# Tasks

## 1. Service scaffolding and configuration

- [x] 1.1 Create `apps/reader-service/` package structure with `app/main.py`, `config.py`, `db.py`, `models.py`, `schemas.py` and router modules; verify imports compile with `python -m compileall app`.
- [x] 1.2 Add `requirements.txt` with Python 3.13-compatible FastAPI, Uvicorn, SQLAlchemy async, asyncpg, Alembic, Pydantic settings and test dependencies; verify a clean dependency installation succeeds.
- [x] 1.3 Implement environment configuration and async engine/session dependency using `DATABASE_URL`; verify missing or malformed configuration fails with an explicit startup diagnostic rather than silently falling back.

## 2. Database model and migrations

- [x] 2.1 Define the single `readers` ORM model with the required columns, defaults, nullable `book_title`, and unique `card_number`; verify metadata contains no additional application tables.
- [x] 2.2 Configure Alembic's async `env.py` to read `DATABASE_URL` from the environment and connect through the async engine; verify `alembic check` can load the configuration without calling application `create_all`.
- [x] 2.3 Add the initial Alembic revision creating `readers` and its unique card constraint, plus downgrade logic; verify upgrade and downgrade run successfully against PostgreSQL.
- [x] 2.4 Add database test fixtures and migration-backed tests for defaults, uniqueness, nullable book title, and registered timestamp; verify the tests use the migrated schema and detect duplicate cards.

## 3. Reader API and validation

- [x] 3.1 Define request/response schemas for reader creation, PATCH updates, book issuance, reader responses, and summary responses; verify malformed required fields produce HTTP 422.
- [x] 3.2 Implement `POST /readers`, `GET /readers`, `GET /readers/{id}`, `PATCH /readers/{id}`, and `DELETE /readers/{id}` with 201/200/204/404/409 behavior from the spec; verify CRUD and duplicate-card API tests.
- [x] 3.3 Enforce deletion protection when `book_title` is populated and translate unique-card database conflicts into HTTP 409; verify the reader remains unchanged after both conflict paths.
- [ ] 3.4 Add API tests for unknown IDs, partial updates, response shapes, and empty-reader list behavior; verify all tests run against a migrated PostgreSQL database.

## 4. Card and circulation operations

- [x] 4.1 Implement `POST /readers/{id}/revoke-card` with row-level locking and the outstanding-book conflict rule; verify successful revocation and HTTP 409 protection tests.
- [x] 4.2 Implement `POST /readers/{id}/issue-book` with non-empty title validation, active-card checks, one-book invariant, row-level locking, and HTTP 409 conflicts; verify eligible and rejected issue scenarios.
- [x] 4.3 Implement `POST /readers/{id}/return-book` with row-level locking and the no-book HTTP 409 rule; verify successful return and unchanged-state conflict tests.
- [x] 4.4 Implement `GET /reports/summary` using aggregate counts; verify empty, mixed, and all-issued datasets return correct total and outstanding-book counts.
- [ ] 4.5 Add transaction/concurrency tests for competing issue, return, revoke, and delete operations; verify no operation can leave contradictory card/book state.

## 5. Containerization and documentation

- [x] 5.1 Add `apps/reader-service/Dockerfile` and container entrypoint for Uvicorn; verify the image builds and exposes the configured API port.
- [x] 5.2 Add root `docker-compose.yml` with PostgreSQL healthcheck, internal port 5432, host port 55432, one-shot `migrate`, and API dependency on successful migration; verify `docker compose config` validates the dependency graph.
- [x] 5.3 Add `.env.example` and update `.gitignore` without committing secrets; verify a fresh Compose run reads the documented variables and does not create schema through application startup.
- [x] 5.4 Update `README.md` with Docker and local commands, API address, PostgreSQL ports, migration command, and Swagger URL; verify every documented command and endpoint address matches the Compose configuration.

## 6. Integrated verification

- [ ] 6.1 Run the focused unit/API/migration test suite and static compile checks; verify all tests pass against the migrated PostgreSQL service.
- [x] 6.2 Run `docker compose up --build` from a clean database and exercise create, issue, return, revoke, delete, and summary endpoints through `/docs` or HTTP requests; verify migration runs before API readiness.
- [x] 6.3 Validate the completed OpenSpec change with `openspec validate --change library-readers-service --strict`; verify all required artifacts and scenarios are accepted.
