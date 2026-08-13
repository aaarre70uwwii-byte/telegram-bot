import sqlite3

# نربط مع ملف قاعدة البيانات tia.db
conn = sqlite3.connect('tia.db', check_same_thread=False)
cursor = conn.cursor()

# جدول المستخدمين والرتب
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    rank TEXT DEFAULT 'member'
)
''')

# جدول الحظر المؤقت
cursor.execute('''
CREATE TABLE IF NOT EXISTS bans (
    user_id INTEGER,
    chat_id INTEGER,
    time INTEGER
)
''')

# جدول الكتم المؤقت
cursor.execute('''
CREATE TABLE IF NOT EXISTS mutes (
    user_id INTEGER,
    chat_id INTEGER,
    time INTEGER
)
''')

conn.commit()

def set_rank(user_id, chat_id, rank):
    cursor.execute("INSERT OR REPLACE INTO users (user_id, chat_id, rank) VALUES (?, ?, ?)", (user_id, chat_id, rank))
    conn.commit()

def get_rank(user_id, chat_id):
    cursor.execute("SELECT rank FROM users WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
    result = cursor.fetch
