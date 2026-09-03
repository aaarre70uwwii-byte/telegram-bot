import sqlite3

DB_NAME = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (chat_id INTEGER PRIMARY KEY, welcome TEXT, link TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ranks
                 (chat_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY(chat_id, user_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS marriages
                 (chat_id INTEGER, user1 INTEGER, user2 INTEGER, PRIMARY KEY(chat_id, user1))''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (chat_id INTEGER, user_id INTEGER, voters TEXT, PRIMARY KEY(chat_id, user_id))''')
    conn.commit()
    conn.close()

def get_settings(chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT welcome, link FROM settings WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    if row: return {"welcome": row[0], "link": row[1]}
    return {"welcome": "اهلا بك", "link": "لا يوجد"}

def set_welcome(chat_id, text):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT chat_id FROM settings WHERE chat_id=?", (chat_id,))
    if c.fetchone():
        c.execute("UPDATE settings SET welcome=? WHERE chat_id=?", (text, chat_id))
    else:
        c.execute("INSERT INTO settings (chat_id, welcome) VALUES (?,?)", (chat_id, text))
    conn.commit()
    conn.close()

def set_link(chat_id, link):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT chat_id FROM settings WHERE chat_id=?", (chat_id,))
    if c.fetchone():
        c.execute("UPDATE settings SET link=? WHERE chat_id=?", (link, chat_id))
    else:
        c.execute("INSERT INTO settings (chat_id, link) VALUES (?,?)", (chat_id, link))
    conn.commit()
    conn.close()

def set_rank(chat_id, user_id, rank):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO ranks (chat_id, user_id, rank) VALUES (?,?,?)", (chat_id, user_id, rank))
    conn.commit()
    conn.close()

def get_rank(chat_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT rank FROM ranks WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_ranks(chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, rank FROM ranks WHERE chat_id=?", (chat_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def clear_ranks(chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM ranks WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

def add_marriage(chat_id, user1, user2):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO marriages (chat_id, user1, user2) VALUES (?,?,?)", (chat_id, user1, user2))
    c.execute("REPLACE INTO marriages (chat_id, user1, user2) VALUES (?,?,?)", (chat_id, user2, user1))
    conn.commit()
    conn.close()

def get_spouse(chat_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user2 FROM marriages WHERE chat_id=? AND user1=?", (chat_id, user_id))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def remove_marriage(chat_id, user1):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM marriages WHERE chat_id=? AND (user1=? OR user2=?)", (chat_id, user1, user1))
    conn.commit()
    conn.close()

def add_vote(chat_id, user_id, voter_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT voters FROM votes WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    row = c.fetchone()
    voters = row[0].split(",") if row else []
    if str(voter_id) not in voters:
        voters.append(str(voter_id))
    c.execute("REPLACE INTO votes (chat_id, user_id, voters) VALUES (?,?,?)", (chat_id, user_id, ",".join(voters)))
    conn.commit()
    conn.close()
    return len(voters)

def add_dev(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO ranks (chat_id, user_id, rank) VALUES (0,?,?)", (user_id, "dev"))
    conn.commit()
    conn.close()

def remove_dev(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM ranks WHERE chat_id=0 AND user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_devs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM ranks WHERE rank='dev'")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def add_gban(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO ranks (chat_id, user_id, rank) VALUES (0,?,?)", (user_id, "gban"))
    conn.commit()
    conn.close()
