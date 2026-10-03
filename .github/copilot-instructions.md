# AGENTS.md

## О проекте
Сервис учёта читателей библиотеки (лабораторная работа 1, вариант «читатели»).
Python 3.13, FastAPI (async), SQLAlchemy 2.x + asyncpg, PostgreSQL 16, Alembic.
Спецификации: `openspec/` (источник правды о требованиях).

## Структура
- `apps/reader-service/app/` — код (main, config, db, models, schemas, routers)
- `apps/reader-service/alembic/` — миграции
- `apps/reader-service/tests/` — тесты
- `docker-compose.yml` — postgres, migrate (одноразовый), api
- запускать `docker compose` нужно из корня репозитория

## Как запустить
Docker: `docker compose up --build` → API http://localhost:3001, Swagger /docs.
Локально: `docker compose up -d postgres`, `.env` из `.env.example`,
затем из `apps/reader-service`: `alembic upgrade head`,
`uvicorn app.main:app --reload --port 3001`.

## Как проверить
- Тесты: из `apps/reader-service` выполнить
  `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs`.
  Критерий готовности — `0 skipped`.
- Сервис жив: `GET http://127.0.0.1:3001/docs` отдаёт 200
  (использовать `127.0.0.1`, а не `localhost`: из-за `HTTP_PROXY` в окружении
  запросы к `localhost` могут возвращать 503).
- Основной сценарий через Swagger: создать читателя → выдать книгу →
  `/reports/summary` → вернуть книгу → изъять билет → удалить
- Ожидаемые коды: создание читателя — 201; выдача книги, возврат,
  изъятие билета, `/reports/summary` — 200; удаление читателя — 204;
  дубль `card_number` — 409.
- После проверки остановить окружение: `docker compose down`
  (из корня репозитория).

## Жёсткие правила
- В БД ровно одна таблица `readers` (плюс служебная `alembic_version`).
- Схема создаётся только Alembic; `create_all` не использовать.
- Не менять существующие эндпоинты и коды ответов без изменения спецификации.
- PATCH принимает только непустые `full_name` и `card_number`; `null`, пустые,
  state-поля и дополнительные поля должны возвращать HTTP 422.
- Секреты не коммитить: `.env` в `.gitignore`, в репозитории только `.env.example`.
- В Docker `DATABASE_URL` задан в compose (хост `postgres`, порт 5432),
  локально в `.env` (хост `localhost`, порт 55432).
- Новые изменения оформлять через OpenSpec (`openspec/changes/`).

## Критерий готовности
Тесты проходят, `docker compose up --build` поднимает postgres → migrate
(код 0) → api, сценарий в Swagger выполняется без ошибок.