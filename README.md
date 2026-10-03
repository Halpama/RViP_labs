# Сервис учёта читателей библиотеки

Асинхронный REST-сервис на FastAPI + SQLAlchemy 2.x (asyncpg) + PostgreSQL.
Схема БД (одна таблица `readers`) создаётся миграциями Alembic.

## Возможности

- `POST /readers` — добавить читателя
- `GET /readers`, `GET /readers/{id}` — список и просмотр
- `PATCH /readers/{id}` — редактировать
- `DELETE /readers/{id}` — удалить
- `POST /readers/{id}/revoke-card` — изъять читательский билет
- `POST /readers/{id}/issue-book` — выдать книгу
- `POST /readers/{id}/return-book` — вернуть книгу
- `GET /reports/summary` — всего читателей и сколько из них с книгой на руках

## Запуск в Docker

Запускает PostgreSQL, одноразовую миграцию и API в одной docker-сети:

```bash
docker compose up --build
```

- API: `http://localhost:3001`
- Swagger UI: `http://localhost:3001/docs`
- PostgreSQL с хоста: порт `55432` (внутри сети Compose — `postgres:5432`)

Контейнер API стартует только после того, как PostgreSQL прошёл healthcheck, а
сервис `migrate` успешно выполнил `alembic upgrade head`.

Остановка: `docker compose down` (с удалением данных БД: `docker compose down -v`).

## Локальный запуск

БД запускается в Docker, приложение — на хосте.

1. Скопируйте `.env.example` в `.env` в корне проекта. 
2. Запустите только PostgreSQL:

```bash
docker compose up -d postgres
```

3. Установите зависимости, примените миграции и запустите сервис:

```bash
cd apps/reader-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 3001
```

API и Swagger доступны по тем же адресам, что и в Docker:
`http://localhost:3001` и `http://localhost:3001/docs`.