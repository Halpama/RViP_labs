# AI process

## Prompts

### Propose

- Задача 1: вставить автором
- Задача 2: вставить автором
- Задача 3: исправить замечания ревью по контракту PATCH, API-тестам,
  воспроизводимости окружения и документации сервиса читателей.

### Apply

`/openspec-apply-change fix-review-findings`

## Пересмотренные решения

- Для миграций используется Alembic вместо Liquibase.
- Сервис `migrate` переопределяет entrypoint контейнера и запускает
  `alembic upgrade head`.
- `entrypoint.sh` сохраняет CRLF-совместимое оформление для запуска в Docker.
- Поиск `.env` выполняется от корня проекта, а не через `parents[3]`.
- Конкурирующие issue/return/revoke/delete операции не входят в объём этого
  изменения; новые тесты конкурентности не добавлялись.

## Проверки

| Проверка | Фактический результат |
|---|---|
| `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs` | 26 passed, 0 skipped |
| `pip install -r requirements.txt` в venv Python 3.13.7 | Установленные pinned-зависимости уже соответствуют requirements.txt |
| `docker compose build` | Успешно собраны образы `migrate` и `api` на `python:3.13.7-slim` |
| `docker compose config` | Успешно; порядок postgres → migrate → api и `service_completed_successfully` сохранены |
| `docker compose up --build` | PostgreSQL healthy, migrate завершён с кодом 0, API запущен |
| Сценарий Swagger/API | Создание → выдача книги → summary (1/1) → возврат → изъятие билета → удаление; ответы успешны, DELETE = 204 |
| `docker compose down` | Успешно, контейнеры и сеть удалены |
| `python -m compileall -q app tests` | Успешно |
