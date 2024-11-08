import mysql.connector
from mysql.connector import Error


def get_conn():
    """Створює та повертає з'єднання з базою даних."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="notes_db"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Помилка підключення до бази даних: {e}")
    return None


def add_user(username, telegram_id=None):
    """Додає нового користувача в базу даних і повертає його ID."""
    conn = get_conn()
    user_id = None
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO users (username, telegram_id) VALUES (%s, %s)"
            cursor.execute(query, (username, telegram_id))
            conn.commit()
            user_id = cursor.lastrowid  # Отримуємо ID останнього доданого користувача
        except Error as e:
            print(f"Помилка при додаванні користувача: {e}")
        finally:
            cursor.close()
            conn.close()
    return user_id


def add_note(user_id, title, content):
    """Додає нову нотатку для користувача."""
    conn = get_conn()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, title, content))
            conn.commit()
        except Error as e:
            print(f"Помилка при додаванні нотатки: {e}")
        finally:
            cursor.close()
            conn.close()


def get_notes(user_id):
    """Отримує всі нотатки користувача."""
    conn = get_conn()
    notes = []
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT id, title, content FROM notes WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            notes = cursor.fetchall()
        except Error as e:
            print(f"Помилка при отриманні нотаток: {e}")
        finally:
            cursor.close()
            conn.close()
    return notes


def update_note(note_id, title, content):
    """Оновлює вибрану нотатку в базі даних."""
    conn = get_conn()
    if conn:
        try:
            cursor = conn.cursor()
            query = "UPDATE notes SET title = %s, content = %s WHERE id = %s"
            cursor.execute(query, (title, content, note_id))
            conn.commit()
        except Error as e:
            print(f"Помилка при оновленні нотатки: {e}")
        finally:
            cursor.close()
            conn.close()
