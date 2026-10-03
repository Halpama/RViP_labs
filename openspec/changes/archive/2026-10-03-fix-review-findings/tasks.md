# Tasks

## 1. Исправление PATCH-контракта

- [x] 1.1 Обновить `ReaderUpdate`: оставить только `full_name` и `card_number`, запретить `null` и пустые/пробельные строки, отклонять пустой объект `{}`, включить `extra="forbid"`; проверить схемными тестами HTTP 422 для null, пустых значений, `{}`, `card_active`, `book_title` и неизвестного поля.
- [x] 1.2 Проверить, что `PATCH /readers/{id}` сохраняет допустимые частичные изменения, отдаёт 409 при дубликате `card_number`, 404 для неизвестного ID и не меняет запись при ошибках; подтвердить API-тестами.

## 2. Расширение API-тестов

- [x] 2.1 Добавить тесты 404 для GET/PATCH/DELETE/revoke-card/issue-book/return-book с неизвестным ID и тест пустого списка читателей; проверить командой `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs` и убедиться, что `0 skipped`.
- [x] 2.2 Добавить тесты 409 для дубликата `card_number` при создании и PATCH, удаления и изъятия билета при книге на руках, второй книги, выдачи при неактивном билете и возврата без книги; проверить неизменность состояния после каждого конфликта и выполнить `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs` с `0 skipped`.
- [x] 2.3 Добавить тесты `GET /reports/summary` для пустого, смешанного набора и набора, где у всех читателей есть книги; проверить точные `total_readers` и `outstanding_books`.
- [x] 2.4 Не добавлять тесты конкурентности; отметить в тестовой документации/tasks, что конкурирующие issue/return/revoke/delete находятся вне объёма этого изменения. Конкурирующие операции явно остаются вне объёма текущего изменения.

## 3. Исправление database-теста

- [x] 3.1 Изменить `tests/test_database.py`, чтобы после rollback тест использовал сохранённый идентификатор или повторно загруженную сущность, а не ORM-объект, истёкший после rollback; проверить командой `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs` на migrated PostgreSQL и получить `0 skipped`.

## 4. Воспроизводимость окружения и документация

- [x] 4.1 Заменить диапазоны в `requirements.txt` точными версиями (`==`) совместимого набора, выбирая только существующие версии; проверить `pip install -r requirements.txt` в чистом venv и затем `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs` с результатом `0 skipped`.
- [x] 4.2 Закрепить Docker-образы только на существующих конкретных patch-тегах `postgres:16.x-alpine` и `python:3.13.x-slim`, не меняя порядок postgres → migrate → api; проверить `docker compose build` и `docker compose config`.
- [x] 4.3 Обновить README отдельными инструкциями для Windows, macOS и Linux, включая venv, `.env`, PostgreSQL, миграции, тесты, API и Swagger; проверить команды по фактической конфигурации Compose.
- [x] 4.4 Создать `docs/ai-process.md` с промптами propose/apply, оставив для propose первой и второй задач заглушку `вставить автором`, пересмотренными решениями (Alembic вместо Liquibase, override entrypoint migrate, CRLF в entrypoint.sh, поиск `.env` вместо `parents[3]`) и таблицей только реально выполненных проверок с фактическими результатами: `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs`, `pip install -r requirements.txt` в чистом venv, `docker compose build`, `docker compose config` и сценарий Swagger; не записывать невыполненные команды или выдуманные итоги.

## 5. Интеграционная проверка

- [x] 5.1 Запустить полный набор тестов командой `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test python -m pytest -rs` без пропусков и статическую проверку импортов/компиляции; зафиксировать только фактически полученные команды и результаты в `docs/ai-process.md`.
- [x] 5.2 Выполнить `docker compose up --build`, проверить healthcheck, успешный migrate и доступность API, затем пройти сценарий в Swagger; после проверки выполнить `docker compose down` и записать результат.
- [x] 5.3 Выполнить `openspec validate --change fix-review-findings --strict` и убедиться, что все артефакты изменения валидны.

## 6. Синхронизация проектных инструкций и архивных задач

- [x] 6.1 Обновить `AGENTS.md` и `.github/copilot-instructions.md`: PATCH меняет только `full_name` и `card_number`, тесты запускаются с явным `TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library_test`, критерий — `0 skipped`; проверить, что оба файла содержат одинаковые правила.
- [x] 6.2 В `openspec/changes/archive/2026-10-03-library-readers-service/tasks.md` дописать к задачам 3.4, 4.5 и 6.1 пометку `закрыто/вынесено в fix-review-findings`; проверить наличие отметки у всех трёх задач.
