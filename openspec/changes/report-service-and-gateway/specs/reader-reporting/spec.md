# Spec Delta

## Purpose

Предоставляет отдельный read-only HTTP-контракт для просмотра читателей и
оперативной сводки по книгам, используя общую библиотечную базу без изменения
данных или схемы.

## ADDED Requirements

### Requirement: Report service lists readers
Report service MUST provide `GET /reports/readers` with the current reader records and the fields `id`, `full_name`, `card_number`, `card_active`, `book_title`, and `registered_at`.

#### Scenario: List readers from an empty database
- **WHEN** the report client requests `GET /reports/readers` and no reader records exist
- **THEN** the service returns HTTP 200 with an empty JSON array

#### Scenario: List current reader state
- **WHEN** the report client requests `GET /reports/readers`
- **THEN** the service returns HTTP 200 and each item contains the six specified reader fields, including the current book and card state

### Requirement: Report service exposes circulation summary
Report service MUST provide `GET /reports/summary` with numeric `total_readers` and `outstanding_books` values.

#### Scenario: Read an empty summary
- **WHEN** no reader records exist and the report client requests `GET /reports/summary`
- **THEN** the service returns HTTP 200 with `total_readers` equal to 0 and `outstanding_books` equal to 0

#### Scenario: Read a mixed summary
- **WHEN** some readers have a non-empty book and others do not
- **THEN** the service returns the total reader count and the exact count of readers with an outstanding book

### Requirement: Report service is read-only
Report service MUST not expose operations that insert, update, delete, or otherwise mutate reader records or database schema.

#### Scenario: Report requests do not mutate data
- **WHEN** a client uses either report endpoint
- **THEN** the reader records and database schema remain unchanged
