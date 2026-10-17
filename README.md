# Сервис учёта читателей библиотеки

Проект состоит из `reader-service` (единственный владелец схемы и Alembic),
read-only `report-service` и `file-storage-service`, доступных через nginx
gateway.
`report-service` не подключается к PostgreSQL: он получает данные только по
REST от `reader-service`, формирует CSV и передаёт его в файловое хранилище
через REST.

## Запуск

Из корня репозитория:

```bash
docker compose up --build
```

Для запуска двух экземпляров `reader-service` с автоматическим обнаружением
реплик nginx используйте:

```bash
docker compose up --build --scale reader-service=2
```

Nginx разрешает имя `reader-service` через встроенный DNS Docker и обновляет
список адресов каждые 5 секунд. Поэтому новые реплики добавляются без ручного
изменения `gateway/nginx.conf`.

- Gateway: http://127.0.0.1:8080
- Reader Swagger: http://127.0.0.1:8080/reader-service/docs
- Report Swagger: http://127.0.0.1:8080/report-service/docs
- File storage Swagger: http://127.0.0.1:8080/file-storage/docs
- PostgreSQL (только для локальных тестов): `127.0.0.1:55432`

Остановка: `docker compose down`; с удалением данных: `docker compose down -v`.
Приложения доступны только во внутренней сети Compose. Наружу опубликованы
только gateway и PostgreSQL. Только reader-service изменяет единственную
таблицу `readers`; report-service не содержит миграций, SQLAlchemy, `asyncpg`,
`DATABASE_URL` или операций записи. CSV-файлы сохраняются в named volume
`file_storage`, которым владеет file-storage-service.

## API

Reader API доступен под `/reader-service/`: создание, просмотр, изменение,
выдача/возврат книги, изъятие билета и удаление читателя.
Report API доступен под `/report-service/`: `GET /reports/readers`,
`GET /reports/summary` и `POST /reports/export`. Последний запрашивает
`GET /readers` у reader-service, формирует CSV и передаёт его в
file-storage-service с таймаутом 5 секунд. Сохранённый файл можно скачать
через `/file-storage/files/{filename}`.

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
