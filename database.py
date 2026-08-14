import sqlite3

# الاتصال بقاعدة بيانات مركزية واحدة
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()

# إنشاء كافة الجداول مرة واحدة
def create_tables():
    # جدول الأدمنية
    cursor.execute('CREATE TABLE IF NOT EXISTS admins (chat_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY (chat_id, user_id))')
    # جدول الإعدادات
    cursor.execute('CREATE TABLE IF NOT EXISTS settings (chat_id INTEGER PRIMARY KEY, welcome TEXT DEFAULT "تفعيل", replies TEXT DEFAULT "تفعيل")')
    # جدول الأقفال
    cursor.execute('CREATE TABLE IF NOT EXISTS locks (chat_id INTEGER, lock_name TEXT, status TEXT DEFAULT "فتحه", PRIMARY KEY (chat_id, lock_name))')
    conn.commit()

# دوال جاهزة نستخدمها في باقي الملفات
def set_lock(chat_id, lock_name, status):
    cursor.execute('REPLACE INTO locks (chat_id, lock_name, status) VALUES (?,?,?)', (chat_id, lock_name, status))
    conn.commit()

def get_lock(chat_id, lock_name):
    cursor.execute('SELECT status FROM locks WHERE chat_id=? AND lock_name=?', (chat_id, lock_name))
    result = cursor.fetchone()
    return result[0] if result else "فتحه"

def update_setting(chat_id, column, value):
    cursor.execute(f'INSERT INTO settings (chat_id, {column}) VALUES (?,?) ON CONFLICT(chat_id) DO UPDATE SET {column}=?', (chat_id, value, value))
    conn.commit()

create_tables() # تشغيل عند بدء البوت
