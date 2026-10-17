# Сервис учёта читателей библиотеки

Проект состоит из `reader-service` (единственный владелец схемы и Alembic) и
read-only `report-service`, доступных через nginx gateway.
`report-service` не подключается к PostgreSQL: он получает данные только по
REST от `reader-service`.

## Запуск

Из корня репозитория:

```bash
docker compose up --build -d
```

Для запуска двух экземпляров `reader-service` с автоматическим обнаружением
реплик nginx используйте:

```bash
docker compose up --build --scale reader-service=2
```

Вместе с приложениями запускаются Loki, Promtail и Grafana. Promtail читает
stdout/stderr всех контейнеров проекта через Docker API и отправляет записи в
Loki. Loki и Promtail доступны только во внутренней сети Compose; наружу
опубликован только Grafana:

- Grafana: http://127.0.0.1:3000 (логин `admin`, пароль `admin`)
- Loki: только внутри Compose, `http://loki:3100`
- Promtail: только внутри Compose

В Grafana автоматически создаются datasource Loki и dashboard **Library
services observability**. На панели **Reader requests by container** выберите
последние 5–15 минут: счётчик группируется по метке `container`, поэтому при
масштабировании видны разные контейнеры `reader-service`. В логах
reader-service и report-service присутствуют JSON-поля `hostname` (уникальный
hostname контейнера), `instance_name`, `method`, `path` и `status_code`.
Дополнительно access log gateway содержит `upstream`, например
`reader-service:3001`, — это адрес upstream, обработавшего запрос.

Для быстрой проверки балансировки выполните несколько запросов:

```bash
docker compose up --build -d --scale reader-service=2
for ($i = 1; $i -le 10; $i++) {
  curl.exe -s http://127.0.0.1:8080/reader-service/readers > $null
}
```

Откройте dashboard в Grafana или выполните запрос в Explore:
`{service="reader-service"} | json`. Для gateway используйте
`{service="gateway"}` и поле `upstream`. Имена контейнеров и hostname
реплик различаются даже когда `INSTANCE_NAME` оставлен со значением по
умолчанию, поэтому распределение запросов можно сопоставить с конкретным
экземпляром.

Nginx разрешает имя `reader-service` через встроенный DNS Docker и обновляет
список адресов каждые 5 секунд. Поэтому новые реплики добавляются без ручного
изменения `gateway/nginx.conf`.

- Gateway: http://127.0.0.1:8080
- Reader Swagger: http://127.0.0.1:8080/reader-service/docs
- Report Swagger: http://127.0.0.1:8080/report-service/docs
- PostgreSQL (только для локальных тестов): `127.0.0.1:55432`

Остановка: `docker compose down`; с удалением данных наблюдаемости:
`docker compose down -v`.
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
