# Сервис учёта читателей библиотеки

Проект состоит из `reader-service` (единственный владелец схемы и Alembic) и
read-only `report-service`, доступных через nginx gateway.

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
Внешние порты приложений не публикуются. Только reader-service изменяет
единственную таблицу `readers`; report-service не содержит миграций и операций
записи.

## API

Reader API доступен под `/reader-service/`: создание, просмотр, изменение,
выдача/возврат книги, изъятие билета и удаление читателя.
Report API доступен под `/report-service/`: `GET /reports/readers` и
`GET /reports/summary`.

Postman: импортируйте `postman/library.postman_collection.json` и
`postman/local.postman_environment.json`, затем запустите папку
`Сквозной сценарий`.

## Тесты

После `docker compose up -d postgres` из соответствующих каталогов:

```bash
cd apps/reader-service
TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs
cd ../report-service
TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs
```

Критерий готовности — все тесты проходят без skipped.
