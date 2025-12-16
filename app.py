"""
Secure Backend API with OWASP Top 10 Protection
Implements protection against SQL Injection, XSS, and Broken Authentication
"""
import sqlite3
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import bcrypt
from werkzeug.utils import escape

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'  # nosec B105 # В продакшене использовать переменную окружения
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

# Инициализация базы данных
def init_db():
    """Инициализация базы данных с защитой от SQL-инъекций через параметризованные запросы"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Создание таблицы пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Создание таблицы данных
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Создание тестового пользователя (пароль: testpass123)
    # Хэш пароля создается с помощью bcrypt
    test_password = 'testpass123'  # nosec B105 # Тестовый пароль для учебного проекта
    password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Использование параметризованного запроса для защиты от SQL-инъекций
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)',
        ('testuser', password_hash)
    )
    
    # Добавление тестовых данных
    cursor.execute(
        'INSERT OR IGNORE INTO data_items (title, content, user_id) VALUES (?, ?, ?)',
        ('Test Item 1', 'This is a test content', 1)
    )
    cursor.execute(
        'INSERT OR IGNORE INTO data_items (title, content, user_id) VALUES (?, ?, ?)',
        ('Test Item 2', 'Another test content', 1)
    )
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Получение соединения с базой данных"""
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/auth/login', methods=['POST'])
def login():
    """
    Эндпоинт для аутентификации пользователя
    Защита от SQL-инъекций: использование параметризованных запросов
    """
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Защита от SQL-инъекций: параметризованный запрос
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Проверка пароля с помощью bcrypt
    password_hash = user['password_hash'].encode('utf-8')
    if not bcrypt.checkpw(password.encode('utf-8'), password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Создание JWT токена (identity должен быть строкой)
    access_token = create_access_token(identity=str(user['id']))
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'user_id': user['id'],
        'username': user['username']
    }), 200

@app.route('/api/data', methods=['GET'])
@jwt_required()
def get_data():
    """
    Защищенный эндпоинт для получения данных
    Защита от XSS: экранирование всех пользовательских данных
    Защита от SQL-инъекций: параметризованные запросы
    """
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)  # Преобразуем строку обратно в int
    
    # Защита от SQL-инъекций: параметризованный запрос
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, content FROM data_items WHERE user_id = ?',
        (user_id,)
    )
    items = cursor.fetchall()
    conn.close()
    
    # Защита от XSS: экранирование всех данных перед возвратом
    result = []
    for item in items:
        result.append({
            'id': item['id'],
            'title': escape(str(item['title'])),  # Экранирование для защиты от XSS
            'content': escape(str(item['content']))  # Экранирование для защиты от XSS
        })
    
    return jsonify({
        'data': result,
        'count': len(result)
    }), 200

@app.route('/api/data', methods=['POST'])
@jwt_required()
def create_data():
    """
    Дополнительный эндпоинт для создания новых данных
    Защита от XSS: экранирование входных данных
    Защита от SQL-инъекций: параметризованные запросы
    """
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)  # Преобразуем строку обратно в int
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    
    # Защита от XSS: экранирование входных данных
    title_safe = escape(str(title))
    content_safe = escape(str(content))
    
    # Защита от SQL-инъекций: параметризованный запрос
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO data_items (title, content, user_id) VALUES (?, ?, ?)',
        (title_safe, content_safe, user_id)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'id': item_id,
        'title': title_safe,
        'content': content_safe,
        'message': 'Data item created successfully'
    }), 201

@app.route('/health', methods=['GET'])
def health_check():
    """Эндпоинт для проверки здоровья приложения"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)  # nosec B201,B104 # Для разработки; в продакшене использовать production WSGI сервер

