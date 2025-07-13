import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yourpassword',
    'database': 'yourdatabase',
    'port': 3306
}

def create_user_table():
    with mysql.connector.connect(**config) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE,
                    password VARCHAR(100)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100),
                    message TEXT,
                    response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

def register_user(username, password):
    try:
        with mysql.connector.connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                return True
    except mysql.connector.errors.IntegrityError:
        return False

def validate_user(username, password):
    with mysql.connector.connect(**config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            result = cursor.fetchone()
            return result is not None

def save_chat_history(username, message, response):
    with mysql.connector.connect(**config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO chat_history (username, message, response)
                VALUES (%s, %s, %s)
            """, (username, message, response))
            conn.commit()

def load_chat_memory_for_user(username):
    """Fetch last 5 user+bot messages (10 rows) from DB"""
    with mysql.connector.connect(**config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT message, response FROM chat_history
                WHERE username = %s
                ORDER BY timestamp DESC
                LIMIT 5
            """, (username,))
            rows = cursor.fetchall()
            return rows[::-1]  # reverse to oldest first
