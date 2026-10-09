# AGENTS.md

## Проект
Python 3.13, FastAPI, SQLAlchemy async, PostgreSQL 16, Alembic.
`apps/reader-service` владеет единственной таблицей `readers` и миграциями.
`apps/report-service` только читает эту таблицу. Внешний вход — nginx gateway.

## Структура и запуск
- `apps/reader-service/` — CRUD и Alembic
- `apps/report-service/` — read-only `/reports/readers` и `/reports/summary`
- `gateway/nginx.conf` — префиксы `/reader-service/`, `/report-service/`
- запускать `docker compose ...` только из корня
- gateway: `http://127.0.0.1:8080`; PostgreSQL: `127.0.0.1:55432`

```bash
docker compose up --build
docker compose down
```

Swagger: `/reader-service/docs` и `/report-service/docs`. Postman-коллекция и
окружение находятся в `postman/`.

## Проверка
Из `apps/reader-service` и `apps/report-service` запускайте pytest с
`TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test`.
Ожидается 0 skipped. Не использовать `create_all`; схему изменяет только
reader-service через Alembic. Секреты не коммитить.
