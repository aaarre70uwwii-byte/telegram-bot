import sqlite3
from config import DB_NAME
import threading

class Database:
    def __init__(self):
        self.local = threading.local()

    def get_conn(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        return self.local.conn

    def init_tables(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
            (user_id INTEGER, chat_id INTEGER, warns INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0, muted INTEGER DEFAULT 0,
            PRIMARY KEY(user_id, chat_id))''')
        conn.commit()

    def get_user(self, user_id: int, chat_id: int) -> tuple:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id=? AND chat_id=?", (user_id, chat_id))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO users(user_id, chat_id) VALUES (?,?)", (user_id, chat_id))
            conn.commit()
            return (user_id, chat_id, 0, 0, 0)
        return user

    def update(self, user_id: int, chat_id: int, field: str, value: int):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"UPDATE users SET {field}=? WHERE user_id=? AND chat_id=?", (value, user_id, chat_id))
        conn.commit()

db = Database()
db.init_tables() # يشتغل تلقائي اول ما تستدعيه
