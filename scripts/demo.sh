#!/usr/bin/env bash
# Демонстрация работы API через HTTP-запросы (аналог "Try it out" в Swagger UI).
# Требуется запущенный сервис: локально (uvicorn) или в docker compose.
#
# Использование: ./scripts/demo.sh [BASE_URL]
set -euo pipefail

BASE="${1:-http://localhost:8000}/api/v1"
J='Content-Type: application/json'

pp() { python3 -m json.tool --no-ensure-ascii 2>/dev/null || cat; }

echo "=== 1. Добавить читателя ==="
R1=$(curl -sf -X POST "$BASE/readers" -H "$J" \
  -d '{"full_name":"Иванов Иван Иванович","email":"ivanov@example.com","phone":"+7 900 111-22-33"}')
echo "$R1" | pp
ID1=$(echo "$R1" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

echo "=== 2. Добавить второго читателя ==="
R2=$(curl -sf -X POST "$BASE/readers" -H "$J" -d '{"full_name":"Петрова Анна Сергеевна"}')
echo "$R2" | pp
ID2=$(echo "$R2" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

echo "=== 3. Выдать книгу читателю #$ID1 ==="
curl -sf -X POST "$BASE/readers/$ID1/books" -H "$J" \
  -d '{"book_title":"Мастер и Маргарита","author":"Михаил Булгаков","isbn":"978-5-389-06927-1"}' | pp

echo "=== 4. Отредактировать читателя #$ID1 (PATCH) ==="
curl -sf -X PATCH "$BASE/readers/$ID1" -H "$J" \
  -d '{"address":"г. Москва, ул. Ленина, д. 1","birth_date":"1990-05-15"}' | pp

echo "=== 5. Изъять читательский билет у #$ID2 ==="
curl -sf -X POST "$BASE/readers/$ID2/ticket/confiscate" -H "$J" \
  -d '{"reason":"Просрочка возврата книг более 60 дней","suspend":true}' | pp

echo "=== 6. Попытка выдать книгу при изъятом билете -> ожидаем 409 ==="
curl -s -o /dev/null -w 'HTTP %{http_code}\n' -X POST "$BASE/readers/$ID2/books" -H "$J" \
  -d '{"book_title":"Война и мир"}'

echo "=== 7. Отчёт: всего читателей и сколько с книгами на руках ==="
curl -sf "$BASE/reports/readers" | pp

echo "=== 8. Список читателей с фильтром has_books=true ==="
curl -sf "$BASE/readers?has_books=true&limit=10" | pp

echo "Готово. Swagger UI: ${BASE%/api/v1}/docs"
