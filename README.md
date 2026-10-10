# Сервис учёта читателей библиотеки

Проект состоит из `reader-service` (единственный владелец схемы и Alembic) и
read-only `report-service`, доступных через nginx gateway.
`report-service` не подключается к PostgreSQL: он получает данные только по
REST от `reader-service`.

## Запуск

Из корня репозитория:

```bash
docker compose up --build
```

- Gateway: http://127.0.0.1:8080
- Reader Swagger: http://127.0.0.1:8080/reader-service/docs
- Report Swagger: http://127.0.0.1:8080/report-service/docs
- PostgreSQL (только для локальных тестов): `127.0.0.1:55432`

Остановка: `docker compose down`; с удалением данных: `docker compose down -v`.
Приложения доступны только во внутренней сети Compose. Наружу опубликованы
только gateway и PostgreSQL. Только reader-service изменяет единственную
таблицу `readers`; report-service не содержит миграций, SQLAlchemy, `asyncpg`,
`DATABASE_URL` или операций записи.

## API

Reader API доступен под `/reader-service/`: создание, просмотр, изменение,
выдача/возврат книги, изъятие билета и удаление читателя.
Report API доступен под `/report-service/`: `GET /reports/readers` и
`GET /reports/summary`. Report-service запрашивает `GET /readers` у
reader-service с таймаутом 5 секунд.

Postman: импортируйте `postman/library.postman_collection.json` и
`postman/local.postman_environment.json`, затем запустите папку
`Сквозной сценарий`.

## Тесты

Из корня репозитория:

```bash
cd apps/reader-service
TEST_DATABASE_URL=******localhost:55432/library_test python -m pytest -rs
cd ../report-service
python -m pytest -rs
```

Тесты report-service используют HTTP-клиент reader-service, подменённый
`httpx.MockTransport`, и не требуют базы данных. Критерий готовности — все
тесты проходят без skipped.
