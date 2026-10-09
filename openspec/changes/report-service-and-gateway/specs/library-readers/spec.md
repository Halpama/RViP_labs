# Spec Delta

## REMOVED Requirements

### Requirement: The service exposes a circulation summary
Система MUST предоставлять `GET /reports/summary` с общим числом читателей и числом читателей, у которых заполнено поле выданной книги, включая корректные нулевые значения для пустого списка.

#### Scenario: Read empty summary
- **WHEN** в системе нет читателей и клиент запрашивает сводку
- **THEN** система возвращает HTTP 200 с `total_readers` равным 0 и `outstanding_books` равным 0

#### Scenario: Read mixed summary
- **WHEN** часть читателей имеет книгу, а часть не имеет
- **THEN** система возвращает общее число читателей и точное число читателей с книгой

#### Scenario: Read all-issued summary
- **WHEN** каждый читатель имеет книгу на руках
- **THEN** система возвращает равные числовые значения `total_readers` и `outstanding_books`

#### Scenario: Read summary
- **WHEN** клиент запрашивает сводку
- **THEN** система возвращает HTTP 200 с числовыми полями общего количества читателей и количества читателей с книгой

**Reason**: Сводка переносится в отдельный read-only report-service, чтобы разделить операции управления читателями и отчётность.

**Migration**: Использовать `GET /report-service/reports/summary` через gateway.
