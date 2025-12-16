#!/bin/bash

# Скрипт для тестирования API
# Убедитесь, что сервер запущен на http://localhost:5000

BASE_URL="http://localhost:5000"

echo "=== Тест 1: Аутентификация ==="
RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')

echo "$RESPONSE" | python3 -m json.tool
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo -e "\n=== Тест 2: Получение данных (с токеном) ==="
curl -s -X GET $BASE_URL/api/data \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\n=== Тест 3: Создание данных ==="
curl -s -X POST $BASE_URL/api/data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test from script", "content": "This is a test"}' | python3 -m json.tool

echo -e "\n=== Тест 4: Попытка доступа без токена (должна вернуть ошибку) ==="
curl -s -X GET $BASE_URL/api/data | python3 -m json.tool

echo -e "\n=== Тест 5: Health check ==="
curl -s -X GET $BASE_URL/health | python3 -m json.tool

