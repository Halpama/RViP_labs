# Сервис учёта читателей библиотеки

Асинхронный REST-сервис на FastAPI + SQLAlchemy 2.x (asyncpg) + PostgreSQL.
Схема БД (одна таблица `readers`) создаётся миграциями Alembic.

## Возможности

- `POST /readers` — добавить читателя
- `GET /readers`, `GET /readers/{id}` — список и просмотр
- `PATCH /readers/{id}` — изменить только `full_name` и `card_number`
- `DELETE /readers/{id}` — удалить читателя без выданной книги
- `POST /readers/{id}/revoke-card` — изъять читательский билет
- `POST /readers/{id}/issue-book` — выдать книгу
- `POST /readers/{id}/return-book` — вернуть книгу
- `GET /reports/summary` — всего читателей и сколько из них с книгой на руках

## Запуск в Docker (Windows, macOS и Linux)

Из корня репозитория скопируйте `.env.example` в `.env`, при необходимости
измените параметры PostgreSQL, затем выполните:

```bash
docker compose up --build
```

Compose запускает PostgreSQL, ждёт его healthcheck, выполняет `alembic upgrade
head` в одноразовом сервисе `migrate`, а затем запускает API.

- API: <http://localhost:3001>
- Swagger UI: <http://localhost:3001/docs>
- PostgreSQL с хоста: порт `55432` (внутри Compose: `postgres:5432`)

Остановка: `docker compose down`. Для удаления данных используйте
`docker compose down -v`.

## Локальный запуск: Windows PowerShell

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
Set-Location apps/reader-service
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "postgresql+asyncpg://library:library@localhost:55432/library"
alembic upgrade head
uvicorn app.main:app --reload --port 3001
```

## Локальный запуск: macOS

```bash
cp .env.example .env
docker compose up -d postgres
cd apps/reader-service
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library
alembic upgrade head
uvicorn app.main:app --reload --port 3001
```

## Локальный запуск: Linux

```bash
cp .env.example .env
docker compose up -d postgres
cd apps/reader-service
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library
alembic upgrade head
uvicorn app.main:app --reload --port 3001
```

Для миграций и тестов используется отдельная база `library_test`:

```bash
TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs
```

На PowerShell эквивалент:

```powershell
$env:TEST_DATABASE_URL = "postgresql+asyncpg://library:library@localhost:55432/library_test"
python -m pytest -rs
```

Критерий проверки — все тесты проходят без skipped. После локальной проверки
остановите PostgreSQL командой `docker compose down`.
