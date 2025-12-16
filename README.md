# Secure Backend API

Безопасное backend-приложение с автоматизированной проверкой кода на уязвимости. Реализована защита от OWASP Top 10 и интеграция инструментов безопасности в процесс разработки.

## Технологический стек

- **Python 3.11+**
- **Flask** - веб-фреймворк
- **Flask-JWT-Extended** - JWT аутентификация
- **bcrypt** - хэширование паролей
- **SQLite** - база данных
- **Bandit** - SAST (Static Application Security Testing)
- **Safety** - SCA (Software Composition Analysis)

## Реализованные меры защиты

### 1. Защита от SQL-инъекций (SQL Injection)
- Использование параметризованных запросов во всех операциях с БД
- Никакой конкатенации строк для формирования SQL-запросов

### 2. Защита от XSS (Cross-Site Scripting)
- Экранирование всех пользовательских данных с помощью `escape()` из Werkzeug
- Санитизация данных перед возвратом в ответах API

### 3. Защита от Broken Authentication
- JWT токены для аутентификации
- Хэширование паролей с помощью bcrypt
- Middleware для проверки JWT на защищенных эндпоинтах
- Пароли никогда не хранятся в открытом виде

## API Эндпоинты

### 1. POST /auth/login
Аутентификация пользователя.

**Запрос:**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "user_id": 1,
  "username": "testuser"
}
```

### 2. GET /api/data
Получение списка данных (требует аутентификации).

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Test Item 1",
      "content": "This is a test content"
    }
  ],
  "count": 1
}
```

### 3. POST /api/data
Создание нового элемента данных (требует аутентификации).

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Запрос:**
```json
{
  "title": "New Item",
  "content": "New content"
}
```

**Ответ:**
```json
{
  "id": 2,
  "title": "New Item",
  "content": "New content",
  "message": "Data item created successfully"
}
```

### 4. GET /health
Проверка здоровья приложения (публичный эндпоинт).

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd IB-1
```

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Запустите приложение:
```bash
python app.py
```

Приложение будет доступно по адресу: `http://localhost:5000`

## Тестирование API

### С помощью curl

1. **Аутентификация:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

2. **Получение данных (с токеном):**
```bash
curl -X GET http://localhost:5000/api/data \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

3. **Создание данных:**
```bash
curl -X POST http://localhost:5000/api/data \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Item", "content": "New content"}'
```

4. **Проверка без токена (должна вернуть ошибку):**
```bash
curl -X GET http://localhost:5000/api/data
```

### С помощью Postman

1. Создайте новый запрос POST на `http://localhost:5000/auth/login`
2. В Body выберите `raw` и `JSON`, введите:
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```
3. Скопируйте `access_token` из ответа
4. Для защищенных эндпоинтов добавьте заголовок:
   - Key: `Authorization`
   - Value: `Bearer <ваш_токен>`

## CI/CD Pipeline

Проект настроен с GitHub Actions для автоматической проверки безопасности при каждом push или pull request.

### Запускаемые проверки:

1. **Bandit (SAST)** - статический анализ кода на уязвимости
2. **Safety (SCA)** - проверка зависимостей на известные уязвимости
3. **pip-audit** - дополнительная проверка зависимостей

Отчеты сохраняются как артефакты в GitHub Actions.

### Локальный запуск проверок:

```bash
# Запуск Bandit
bandit -r .

# Запуск Safety
safety check

# Запуск pip-audit
pip-audit
```

## Структура проекта

```
IB-1/
├── app.py                 # Основное приложение Flask
├── requirements.txt       # Зависимости проекта
├── .bandit               # Конфигурация Bandit
├── .gitignore           # Игнорируемые файлы
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions workflow
└── README.md            # Документация
```

## Тестовые учетные данные

- **Username:** `testuser`
- **Password:** `testpass123`

⚠️ **Внимание:** В продакшене обязательно измените JWT_SECRET_KEY и используйте переменные окружения для хранения секретов!

## Безопасность

Все меры защиты соответствуют рекомендациям OWASP Top 10:

- ✅ Защита от SQL-инъекций
- ✅ Защита от XSS
- ✅ Защита от Broken Authentication
- ✅ Автоматизированное тестирование безопасности в CI/CD

## Лицензия

Учебный проект для изучения безопасности веб-приложений.

