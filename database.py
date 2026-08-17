import sqlite3
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER, chat_id INTEGER, warns INTEGER DEFAULT 0,
                 banned INTEGER DEFAULT 0, muted INTEGER DEFAULT 0,
                 PRIMARY KEY(user_id, chat_id))''')
    conn.commit()
    conn.close()

def get_user(user_id, chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=? AND chat_id=?", (user_id, chat_id))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users(user_id, chat_id) VALUES (?,?)", (user_id, chat_id))
        conn.commit()
        user = (user_id, chat_id, 0, 0, 0)
    conn.close()
    return user

def update_user(user_id, chat_id, field, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field}=? WHERE user_id=? AND chat_id=?", (value, user_id, chat_id))
    conn.commit()
    conn.close()
