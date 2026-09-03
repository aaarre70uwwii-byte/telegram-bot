import sqlite3

DB_NAME = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ranks (chat_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY(chat_id, user_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (chat_id INTEGER PRIMARY KEY, welcome TEXT, link TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS marriages (chat_id INTEGER, user1 INTEGER, user2 INTEGER, PRIMARY KEY(chat_id, user1))''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes (chat_id INTEGER, target INTEGER, voter INTEGER, PRIMARY KEY(chat_id, target, voter))''')
    c.execute('''CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS gbans (user_id INTEGER PRIMARY KEY)''')
    conn.commit(); conn.close()

def set_rank(chat_id, user_id, rank):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("REPLACE INTO ranks VALUES (?,?,?)", (chat_id, user_id, rank))
    conn.commit(); conn.close()

def get_ranks(chat_id):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT * FROM ranks WHERE chat_id=?", (chat_id,)); data = c.fetchall()
    conn.close(); return data

def set_welcome(chat_id, text):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (chat_id, welcome) VALUES (?,?)", (chat_id, text))
    conn.commit(); conn.close()

def set_link(chat_id, text):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (chat_id, link) VALUES (?,?)", (chat_id, text))
    conn.commit(); conn.close()

def get_settings(chat_id):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT * FROM settings WHERE chat_id=?", (chat_id,)); data = c.fetchone()
    conn.close(); return {"welcome": data[1] if data else "", "link": data[2] if data else ""}

def add_marriage(chat_id, user1, user2):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("REPLACE INTO marriages VALUES (?,?,?)", (chat_id, user1, user2))
    conn.commit(); conn.close()

def remove_marriage(chat_id, user1):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM marriages WHERE chat_id=? AND user1=?", (chat_id, user1))
    conn.commit(); conn.close()

def add_vote(chat_id, target, voter):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO votes VALUES (?,?,?)", (chat_id, target, voter))
    c.execute("SELECT COUNT(*) FROM votes WHERE chat_id=? AND target=?", (chat_id, target)); count = c.fetchone()[0]
    conn.commit(); conn.close(); return count

def add_dev(user_id):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO devs VALUES (?)", (user_id,)); conn.commit(); conn.close()

def remove_dev(user_id):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM devs WHERE user_id=?", (user_id,)); conn.commit(); conn.close()

def get_devs():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT user_id FROM devs"); data = [i[0] for i in c.fetchall()]
    conn.close(); return data

def add_gban(user_id):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO gbans VALUES (?)", (user_id,)); conn.commit(); conn.close()
