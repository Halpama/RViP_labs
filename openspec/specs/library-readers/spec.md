# Library Readers Specification

## Purpose

Эта capability предоставляет библиотеке REST-контракт для регистрации читателей, управления активностью их билетов и учёта одной выданной книги на читателя. Она также отдаёт минимальную сводку для контроля текущей нагрузки библиотеки.

## Requirements

### Requirement: Reader records are persisted with unique library cards
Система MUST хранить каждого читателя с идентификатором, полным именем, уникальным номером билета, признаком активности билета, необязательным названием книги и датой регистрации.

#### Scenario: Create a reader
- **WHEN** клиент отправляет `POST /readers` с именем и ещё не занятым номером билета
- **THEN** система создаёт читателя с активным билетом, пустой книгой и датой регистрации и возвращает созданную запись с HTTP 201

#### Scenario: Reject duplicate card number
- **WHEN** клиент отправляет `POST /readers` с номером билета, уже принадлежащим другому читателю
- **THEN** система не создаёт запись и возвращает HTTP 409 с описанием конфликта

### Requirement: Clients can list and retrieve readers
Система MUST предоставлять чтение списка читателей и отдельной записи по идентификатору.

#### Scenario: List readers
- **WHEN** клиент отправляет `GET /readers`
- **THEN** система возвращает HTTP 200 и список читателей с полями состояния билета, книги и даты регистрации

#### Scenario: Retrieve an existing reader
- **WHEN** клиент отправляет `GET /readers/{id}` для существующего читателя
- **THEN** система возвращает HTTP 200 и соответствующую запись

#### Scenario: Retrieve an unknown reader
- **WHEN** клиент запрашивает отсутствующий идентификатор
- **THEN** система возвращает HTTP 404

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
- **WHEN** клиент удаляет существующего читателя
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


### Requirement: Invalid requests have explicit validation responses
Система MUST отклонять отсутствующие, пустые или имеющие неверный тип обязательные поля с HTTP 422 и MUST возвращать HTTP 404 для неизвестного читателя на любой операции, адресованной по идентификатору.

#### Scenario: Validate a malformed request
- **WHEN** клиент отправляет запрос с отсутствующим или некорректным обязательным полем
- **THEN** система возвращает HTTP 422 и структурированное описание ошибки без изменения данных

#### Scenario: Unknown reader action
- **WHEN** клиент вызывает GET, PATCH, DELETE, revoke-card, issue-book или return-book для отсутствующего идентификатора
- **THEN** система возвращает HTTP 404 без изменения данных
