import sqlite3
from pyrogram import filters
from pyrogram.types import Message
from bot import app # مهم جدا نستدعي app من bot.py

# إعداد قاعدة بيانات للأقفال
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS locks (
    chat_id INTEGER,
    lock_name TEXT,
    status TEXT DEFAULT 'فتحه',
    PRIMARY KEY (chat_id, lock_name)
)''')
conn.commit()

# دالة لتحديث حالة القفل
def set_lock(chat_id, lock_name, status):
    cursor.execute('REPLACE INTO locks (chat_id, lock_name, status) VALUES (?,?,?)', (chat_id, lock_name, status))
    conn.commit()

# أوامر القفل والفتح
@app.on_message(filters.command(["قفل", "فتح"]) & filters.group)
async def handle_locks(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("• يرجى تحديد الشيء المراد قفله أو فتحه \nمثال: `قفل الروابط`")

    action = message.command[0] # قفل أو فتح
    target = " ".join(message.command[1:]) # الروابط، الصور، التكرار...
    chat_id = message.chat.id

    status = "قفله" if action == "قفل" else "فتحه"
    set_lock(chat_id, target, status)

    await message.reply(f"• تم {action} {target} بنجاح ✅")
