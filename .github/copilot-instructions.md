# Инструкции проекта

- Работайте из корня репозитория; Docker Compose запускается только из корня.
- Схему и миграции изменяет только `apps/reader-service`; в базе ровно
  `readers` и `alembic_version`.
- `apps/report-service` остаётся read-only, не имеет доступа к БД, не содержит
  Alembic, `create_all`, SQLAlchemy, asyncpg или `DATABASE_URL`; данные получает
  по REST от reader-service через `READER_SERVICE_URL`.
- В report-service используется один `httpx.AsyncClient` на lifespan приложения,
  таймаут REST-вызова — 5 секунд; ошибки reader-service преобразуются в 502,
  таймауты — в 504.
- Проверяйте gateway по адресу `http://127.0.0.1:8080`, документацию через
  `/reader-service/docs` и `/report-service/docs`.
- Не публикуйте внутренние порты приложений и не коммитьте `.env` или секреты.
