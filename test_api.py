#!/usr/bin/env python3
"""
Скрипт для тестирования API
Убедитесь, что сервер запущен на http://localhost:5001
"""
import requests
import json

BASE_URL = "http://localhost:5001"
TIMEOUT = 5  # Timeout для HTTP запросов (секунды)

def print_response(title, response):
    """Красивый вывод ответа"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

def main():
    # Тест 1: Аутентификация
    print("\n🔐 Тест 1: Аутентификация")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=TIMEOUT)
    print_response("Ответ на /auth/login", response)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"\n✅ Токен получен: {token[:50]}...")
        
        # Тест 2: Получение данных с токеном
        print("\n📋 Тест 2: Получение данных (с токеном)")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/data", headers=headers, timeout=TIMEOUT)
        print_response("Ответ на GET /api/data", response)
        
        # Тест 3: Создание данных
        print("\n➕ Тест 3: Создание данных")
        new_item = {
            "title": "Test Item from Python Script",
            "content": "This is a test content created by test script"
        }
        response = requests.post(f"{BASE_URL}/api/data", json=new_item, headers=headers, timeout=TIMEOUT)
        print_response("Ответ на POST /api/data", response)
        
        # Тест 4: Попытка доступа без токена
        print("\n🚫 Тест 4: Попытка доступа без токена (должна вернуть ошибку)")
        response = requests.get(f"{BASE_URL}/api/data", timeout=TIMEOUT)
        print_response("Ответ на GET /api/data без токена", response)
        
    else:
        print("❌ Не удалось получить токен. Проверьте, что сервер запущен и данные верны.")
    
    # Тест 5: Health check
    print("\n💚 Тест 5: Health check")
    response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    print_response("Ответ на /health", response)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Не удалось подключиться к серверу.")
        print("Убедитесь, что сервер запущен на http://localhost:5001")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

