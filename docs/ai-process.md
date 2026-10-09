## Prompts

### Propose

- Задача автора (заполнить при необходимости)

### Apply

- Задача автора (заполнить при необходимости)

## Проверки

| Команда | Фактический результат |
|---|---|
| `docker compose config` | Успешно; postgres, migrate, reader-service, report-service и gateway присутствуют, опубликованы только 127.0.0.1:8080 и 127.0.0.1:55432 |
| `openspec validate report-service-and-gateway --type change --strict` | Change valid |
| `python -m compileall -q app tests` (report-service) | Успешно |
| JSON-проверка Postman collection/environment | Успешно |
| `git diff --check` | Успешно |
| `python -m pytest -rs` (reader-service, PostgreSQL на временном порту) | 25 passed, 0 skipped |
| `python -m pytest -rs` (report-service, PostgreSQL на временном порту) | 6 passed, 0 skipped |
| `python -m pytest -q tests/test_reports_unit.py` (report-service) | 3 passed |
| `docker compose up --build -d` | Сначала остановлено из-за Windows-резерва порта 55432; проверочный Compose override на доступном host-порту успешно поднял все контейнеры |
| Gateway smoke checks | `/docs`, `/openapi.json`, reader/report endpoints returned 200; OpenAPI servers used `/reader-service` and `/report-service` |
| Gateway lifecycle | Create → issue → report list/summary → return → revoke → delete; DELETE returned 204 |
| Gateway unavailable-upstream check | Остановлен report-service; gateway returned HTTP 502 with JSON `{"error":"upstream service unavailable"}` |
| `docker compose down` (с проверочным override) | Успешно |
