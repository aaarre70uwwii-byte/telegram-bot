import sqlite3
from config import DB_NAME, OWNER_ID

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS devs (id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS whispers (id INTEGER PRIMARY KEY AUTOINCREMENT, to_id INTEGER, from_id INTEGER, text TEXT, time DATETIME DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (chat_id INTEGER, name TEXT, content TEXT, PRIMARY KEY(chat_id, name))")
    cursor.execute("INSERT OR IGNORE INTO devs (id) VALUES (?)", (OWNER_ID,))
    conn.commit()

init_db()

def get_setting(key, default="1"):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    r = cursor.fetchone(); return r[0] if r else default

def set_setting(key, value):
    cursor.execute("REPLACE INTO settings (key,value) VALUES (?,?)", (key,value)); conn.commit()

def is_dev(user_id):
    cursor.execute("SELECT id FROM devs WHERE id=?", (user_id,)); return cursor.fetchone() is not None or user_id == OWNER_ID

def is_banned(user_id):
    cursor.execute("SELECT value FROM settings WHERE key=?", (f"ban_{user_id}",)); return cursor.fetchone() is not None
