import sqlite3
from pyrogram import filters
from pyrogram.types import Message
from bot import app # مهم

# إعداد قاعدة بيانات للإعدادات
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS settings (
    chat_id INTEGER PRIMARY KEY,
    welcome TEXT DEFAULT 'تفعيل',
    replies TEXT DEFAULT 'تفعيل'
)''')
conn.commit()

# دالة مساعدة لتحديث حالة الإعداد
def update_setting(chat_id, column, value):
    cursor.execute(f'INSERT INTO settings (chat_id, {column}) VALUES (?,?) ON CONFLICT(chat_id) DO UPDATE SET {column}=?', (chat_id, value, value))
    conn.commit()

# أوامر تفعيل وتعطيل الإعدادات
@app.on_message(filters.command(["تفعيل_الترحيب", "تعطيل_الترحيب", "تفعيل_الردود", "تعطيل_الردود"]) & filters.group)
async def change_settings(client, message: Message):
    cmd = message.command[0] # اول كلمة فقط
    chat_id = message.chat.id

    if cmd == "تفعيل_الترحيب":
        update_setting(chat_id, "welcome", "تفعيل")
        await message.reply("• أهلاً بك، تم تفعيل الترحيب بنجاح ✅")
    elif cmd == "تعطيل_الترحيب":
        update_setting(chat_id, "welcome", "تعطيل")
        await message.reply("• أهلاً بك، تم تعطيل الترحيب بنجاح ✅")
    elif cmd == "تفعيل_الردود":
        update_setting(chat_id, "replies", "تفعيل")
        await message.reply("• أهلاً بك، تم تفعيل الردود بنجاح ✅")
    elif cmd == "تعطيل_الردود":
        update_setting(chat_id, "replies", "تعطيل")
        await message.reply("• أهلاً بك، تم تعطيل الردود بنجاح ✅")
