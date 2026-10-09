# Tasks

## 1. Report service foundation

- [x] 1.1 Create `apps/report-service` structure, pinned requirements, Dockerfile based on `python:3.13.7-slim`, pytest configuration, and LF-compatible entrypoint; verify all expected files exist and dependency installation succeeds.
- [x] 1.2 Implement report-service settings, safe parent traversal for `.env`, async engine/session dependency, and read-only `Reader` mapping without Alembic or `create_all`; verify `python -m compileall app tests` succeeds and no migration/schema-creation code is present.
- [x] 1.3 Implement response schemas and `GET /reports/readers` plus `GET /reports/summary`; verify the routes return the specified fields, numeric zero values for an empty database, and correct mixed reader/book counts.
- [x] 1.4 Add report-service database/API tests using `TEST_DATABASE_URL`, including empty and populated reports and a check that report requests do not mutate rows; verify the targeted pytest run passes with 0 skipped.

## 2. Reader-service contract split

- [x] 2.1 Remove the reader-service summary router registration and summary tests while preserving all reader-management routes and response codes; verify reader-service tests pass and `/reports/summary` is absent from its OpenAPI routes.
- [x] 2.2 Update the main `library-readers` specification in the change implementation phase according to the REMOVED delta and add focused contract coverage for the new report-service endpoint; verify OpenSpec validation accepts the delta and no reader-service summary test remains.

## 3. Gateway and container orchestration

- [x] 3.1 Add `gateway/nginx.conf` using `nginx:1.27-alpine` routing `/reader-service/` and `/report-service/`, forwarding headers, stripping prefixes, and returning readable JSON for 502/504; verify nginx configuration parses in the built image.
- [x] 3.2 Set FastAPI `root_path` values for both services and ensure `/docs` and `/openapi.json` generate gateway-prefixed links; verify both documentation paths return HTTP 200 through nginx and reference usable prefixed URLs.
- [x] 3.3 Rewrite `docker-compose.yml` with pinned PostgreSQL, healthcheck, one-shot reader migration, internal-only application services, report-service, and gateway dependency conditions; update `.gitattributes` for LF on `*.sh` and `*.conf`; verify `docker compose config` shows the required dependency graph, fixed database URLs, and only ports `127.0.0.1:8080` and `127.0.0.1:55432`.
- [x] 3.4 Add gateway/container integration checks for API forwarding and an unavailable-upstream 502/504 response; verify `docker compose up --build` reaches healthy PostgreSQL, successful migration, both services, and a responsive gateway.

## 4. Client scenario and documentation

- [x] 4.1 Add `postman/library.postman_collection.json` and `postman/local.postman_environment.json` with `base_url=http://127.0.0.1:8080`, status/body assertions for every endpoint, and the folder `Сквозной сценарий` that stores and reuses the created reader id; verify the collection imports and its scenario completes through the gateway.
- [x] 4.2 Update README, AGENTS.md, and `.github/copilot-instructions.md` with service structure, ports, Docker/Swagger/Postman commands, and the rule that only reader-service changes the schema; verify every documented command uses the root Compose invocation and current gateway URLs.
- [x] 4.3 Update `docs/ai-process.md` with only commands actually run and their results, leaving prompt entries as author placeholders; verify the document contains no unexecuted claims or committed secrets.

## 5. End-to-end validation

- [x] 5.1 Run reader-service and report-service tests, compile checks, `docker compose config`, and the full Docker scenario including create → issue → report list/summary → return → revoke → delete; verify all tests have 0 skipped and expected HTTP statuses are preserved.
- [x] 5.2 Stop the environment with `docker compose down` and inspect the final change status and diff; verify `openspec status --change report-service-and-gateway` reports all required artifacts complete and no unintended files are changed.
