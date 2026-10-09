# Инструкции проекта

- Работайте из корня репозитория; Docker Compose запускается только из корня.
- Схему и миграции изменяет только `apps/reader-service`; в базе ровно
  `readers` и `alembic_version`.
- `apps/report-service` остаётся read-only и не содержит Alembic или `create_all`.
- Проверяйте gateway по адресу `http://127.0.0.1:8080`, документацию через
  `/reader-service/docs` и `/report-service/docs`.
- Не публикуйте внутренние порты приложений и не коммитьте `.env` или секреты.
- Новые изменения оформляйте в `openspec/changes/`.
