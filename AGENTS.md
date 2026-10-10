# AGENTS.md

## Проект
Python 3.13, FastAPI, SQLAlchemy async, PostgreSQL 16, Alembic.
`apps/reader-service` владеет единственной таблицей `readers` и миграциями.
`apps/report-service` не имеет доступа к базе данных и получает данные только
по REST от `reader-service`. Внешний вход — nginx gateway.

## Структура и запуск
- `apps/reader-service/` — CRUD и Alembic
- `apps/report-service/` — read-only `/reports/readers` и `/reports/summary`,
  HTTP-клиент `reader-service` через `READER_SERVICE_URL`
- `gateway/nginx.conf` — префиксы `/reader-service/`, `/report-service/`
- запускать `docker compose ...` только из корня
- gateway: `http://127.0.0.1:8080`; PostgreSQL: `127.0.0.1:55432`
- приложения не публикуют порты наружу; report-service не получает
  `DATABASE_URL` и не подключается к PostgreSQL

```bash
docker compose up --build
docker compose down
```

Swagger: `/reader-service/docs` и `/report-service/docs`. Postman-коллекция и
окружение находятся в `postman/`.

## Проверка
Из корня запускайте pytest в каждом сервисе. Для reader-service нужен
`TEST_DATABASE_URL=******localhost:55432/library_test`; report-service
тестируется без базы через `httpx.MockTransport`. Ожидается 0 skipped.
Не использовать `create_all`; схему изменяет только reader-service через
Alembic. Секреты не коммитить.
