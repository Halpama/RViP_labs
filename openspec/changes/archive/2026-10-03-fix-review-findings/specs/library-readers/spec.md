# Spec Delta

## MODIFIED Requirements

### Requirement: Clients can update reader profile and card state
Система MUST поддерживать частичное изменение только профиля читателя через `PATCH /readers/{id}` и MUST сохранять уникальность номера билета. Поля `full_name` и `card_number` MUST быть непустыми строками и MUST отклонять `null`; поля состояния `card_active` и `book_title` MUST быть недоступны через PATCH, а любые дополнительные поля MUST отклоняться.

#### Scenario: Update reader fields
- **WHEN** клиент отправляет допустимое частичное обновление `full_name` или `card_number` существующего читателя
- **THEN** система сохраняет переданные поля и возвращает HTTP 200 с обновлённой записью

#### Scenario: Reject null or blank profile fields
- **WHEN** клиент отправляет в PATCH `full_name` или `card_number` со значением `null` или пустой строкой
- **THEN** система возвращает HTTP 422 и не изменяет читателя

#### Scenario: Reject empty PATCH body
- **WHEN** клиент отправляет PATCH с пустым JSON-объектом `{}` без обновляемых полей
- **THEN** система возвращает HTTP 422 и не изменяет читателя

#### Scenario: Reject state and extra PATCH fields
- **WHEN** клиент отправляет в PATCH `card_active`, `book_title` или любое поле, отсутствующее в схеме обновления
- **THEN** система возвращает HTTP 422 и не изменяет читателя

#### Scenario: Reject conflicting card update
- **WHEN** обновление меняет номер билета на уже занятый
- **THEN** система не изменяет читателя и возвращает HTTP 409

### Requirement: Clients can delete readers
Система MUST удалять читателя по `DELETE /readers/{id}` только если у него нет книги на руках и MUST возвращать HTTP 404 для неизвестного идентификатора.

#### Scenario: Delete an existing reader
- **WHEN** клиент удаляет существующего читателя без книги
- **THEN** система удаляет запись и возвращает HTTP 204 без тела ответа

#### Scenario: Delete an unknown reader
- **WHEN** клиент удаляет отсутствующий идентификатор
- **THEN** система возвращает HTTP 404

#### Scenario: Reject deletion with an outstanding book
- **WHEN** клиент удаляет читателя, у которого есть книга на руках
- **THEN** система не удаляет запись и возвращает HTTP 409

### Requirement: Card revocation is protected by outstanding books
Система MUST изымать билет через `POST /readers/{id}/revoke-card`, MUST запрещать изъятие, пока у читателя числится книга, и MUST возвращать HTTP 404 для неизвестного идентификатора.

#### Scenario: Revoke an active card without a book
- **WHEN** у существующего читателя нет книги на руках и клиент изымает билет
- **THEN** система устанавливает `card_active` в `false` и возвращает HTTP 200 с обновлённой записью

#### Scenario: Reject revocation with an outstanding book
- **WHEN** у читателя есть книга на руках
- **THEN** система не меняет билет и возвращает HTTP 409

#### Scenario: Revoke an unknown reader
- **WHEN** клиент изымает билет у отсутствующего идентификатора
- **THEN** система возвращает HTTP 404

### Requirement: Books can be issued only to eligible readers
Система MUST выдавать одну книгу через `POST /readers/{id}/issue-book`, принимая непустое название книги, только читателю с активным билетом и без другой книги, и MUST возвращать HTTP 404 для неизвестного идентификатора.

#### Scenario: Issue a book
- **WHEN** читатель существует, его билет активен, книги нет, а название книги непустое
- **THEN** система сохраняет название книги и возвращает HTTP 200 с обновлённой записью

#### Scenario: Reject issue for inactive card
- **WHEN** клиент пытается выдать книгу читателю с неактивным билетом
- **THEN** система не меняет запись и возвращает HTTP 409

#### Scenario: Reject second book
- **WHEN** клиент пытается выдать вторую книгу читателю, у которого уже есть книга
- **THEN** система не меняет запись и возвращает HTTP 409

#### Scenario: Issue to an unknown reader
- **WHEN** клиент выдаёт книгу отсутствующему идентификатору
- **THEN** система возвращает HTTP 404

### Requirement: Issued books can be returned
Система MUST возвращать книгу через `POST /readers/{id}/return-book`, очищая сведения о книге, и MUST возвращать HTTP 404 для неизвестного идентификатора.

#### Scenario: Return an issued book
- **WHEN** у существующего читателя есть книга на руках
- **THEN** система очищает `book_title` и возвращает HTTP 200 с обновлённой записью

#### Scenario: Return when no book is issued
- **WHEN** у читателя нет книги на руках
- **THEN** система не меняет запись и возвращает HTTP 409

#### Scenario: Return for an unknown reader
- **WHEN** клиент возвращает книгу отсутствующему идентификатору
- **THEN** система возвращает HTTP 404

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

### Requirement: Invalid requests have explicit validation responses
Система MUST отклонять отсутствующие, пустые или имеющие неверный тип обязательные поля с HTTP 422 и MUST возвращать HTTP 404 для неизвестного читателя на любой операции, адресованной по идентификатору.

#### Scenario: Validate a malformed request
- **WHEN** клиент отправляет запрос с отсутствующим или некорректным обязательным полем
- **THEN** система возвращает HTTP 422 и структурированное описание ошибки без изменения данных

#### Scenario: Unknown reader action
- **WHEN** клиент вызывает GET, PATCH, DELETE, revoke-card, issue-book или return-book для отсутствующего идентификатора
- **THEN** система возвращает HTTP 404 без изменения данных
