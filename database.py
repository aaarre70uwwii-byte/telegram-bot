import sqlite3

conn = None
cursor = None

def init_db():
    global conn, cursor
    conn = sqlite3.connect('tia.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # جدول القفل
    cursor.execute("""CREATE TABLE IF NOT EXISTS locks 
                      (chat_id INTEGER, lock_type TEXT, PRIMARY KEY(chat_id, lock_type))""")
    
    # جدول الاعدادات
    cursor.execute("""CREATE TABLE IF NOT EXISTS settings 
                      (chat_id INTEGER PRIMARY KEY, welcome TEXT)""")
    
    conn.commit()
    print("Database Connected ✅")

def get_cursor():
    return cursor, conn
