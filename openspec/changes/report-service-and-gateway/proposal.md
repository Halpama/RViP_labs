# Proposal

## Why

Лабораторной работе нужен отдельный read-only сервис отчётов, который использует
ту же таблицу `readers`, не становясь владельцем схемы или операций изменения
данных. Единый nginx-шлюз должен скрыть внутренние порты, предоставить стабильные
пути для обоих сервисов и сделать Swagger доступным из единой точки входа.

## What Changes

- Добавить `apps/report-service` с асинхронным FastAPI API только для чтения:
  список читателей и сводка по выданным книгам.
- Перенести `GET /reports/summary` из reader-service в report-service и удалить
  маршрут и его тесты из reader-service. **BREAKING**: summary больше не
  предоставляется напрямую reader-service.
- Добавить nginx-шлюз на закреплённом образе `nginx:1.27-alpine` с маршрутами
  `/reader-service/` и `/report-service/`, включая корректные `root_path` и
  Swagger/OpenAPI URL обоих сервисов.
- Обновить Docker Compose: PostgreSQL с healthcheck, одноразовые миграции
  reader-service, два приложения за внутренней сетью и единственная внешняя
  точка входа gateway на `127.0.0.1:8080`.
- Добавить Postman-коллекцию и локальное окружение со сквозным сценарием от
  создания читателя до удаления.
- Обновить README, AGENTS.md, Copilot-инструкции, `.gitattributes` и журнал
  реально выполненных проверок.

## Capabilities

### New Capabilities

- `reader-reporting`: read-only отчёты по читателям и сводка по выданным книгам
  через отдельный report-service.
- `service-gateway`: маршрутизация двух внутренних сервисов через nginx-шлюз,
  включая доступность их документации и понятные ошибки upstream.

### Modified Capabilities

- `library-readers`: удалить требование и сценарии прямого
  `GET /reports/summary` из reader-service; сводка становится контрактом
  capability `reader-reporting`.

## Impact

- Затрагиваются `apps/reader-service/app`, его API-тесты и спецификация
  `openspec/specs/library-readers/spec.md`.
- Появятся новый Python-сервис, его pinned-зависимости, Dockerfile и тесты,
  nginx-конфигурация, обновлённый `docker-compose.yml` и Postman-артефакты.
- Внешний API изменится с прямого доступа к сервисам на gateway-prefixed URLs;
  внутренние сервисные порты останутся доступны только внутри Compose-сети.
- Миграции и владение схемой останутся исключительно у reader-service; report-
  service не будет содержать Alembic, `create_all` или операции записи.
