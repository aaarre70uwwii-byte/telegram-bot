import sqlite3
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

DEV_DATA = {
    "welcome": "اهلا بيك يا مطور 👑\nهذا بوت Tia",
    "bot_name": "Tia",
    "channel": "https://t.me/your_channel" # حط رابط قناتك هنا
}
bot_status = True
OWNER_ID = 7488375443

DB_FILE = "bot_database.db"

# ===== ضفت الجدول والدالة دي عشان التفعيل =====
def init_group_status():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS group_status (chat_id INTEGER PRIMARY KEY, status INTEGER)")
    conn.commit()
    conn.close()

init_group_status() # شغل الجدول اول ما الملف يفتح

def check_group(chat_id): # << دي اللي كان ناقصه
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT status FROM group_status WHERE chat_id =?", (chat_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1
# ==============================================

def get_dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📢 أوامر الإذاعة"), KeyboardButton("📋 قائمة العام"))
    markup.row(KeyboardButton("👑 تغيير المطور الاساسي"), KeyboardButton("✨ مسح المطورين"))
    markup.row(KeyboardButton("🗂️ مسح اسم البوت"), KeyboardButton("❌ مسح قائمة العام"))
    markup.row(KeyboardButton("✏️ تغيير اسم البوت"), KeyboardButton("👥 مسح المطورين الثانويين"))
    markup.row(KeyboardButton("📵 تعطيل التواصل"), KeyboardButton("📦 جلب النسخة الاحتياطيه"))
    markup.row(KeyboardButton("📲 تفعيل التواصل"), KeyboardButton("🔄 تحديث الملفات"))
    markup.row(KeyboardButton("🔴 تعطيل البوت الخدمي"), KeyboardButton("⚡ تفعيل البوت"))
    markup.row(KeyboardButton("▶️ تفعيل البوت الخدمي"))
    markup.row(KeyboardButton("⚙️ 0_اظهار _ اخفاء _ قائمة اعداد البوت"))
    markup.row(KeyboardButton("👋 اضف ترحيب"), KeyboardButton("📢 تغير قناة البوت"))
    markup.row(KeyboardButton("📢 قناه تحديثات البوت"))
    return markup

def register_handlers(bot):
    global bot_status

    @bot.message_handler(func=lambda m: str(m.from_user.id)!= str(OWNER_ID))
    def not_owner(m): pass

    @bot.message_handler(func=lambda m: m.text == "⚡ تفعيل البوت")
    def enable(m):
        global bot_status; bot_status = True
        bot.send_message(m.chat.id, "✅ تم تفعيل البوت")

    @bot.message_handler(func=lambda m: m.text == "🔴 تعطيل البوت الخدمي" and m.chat.type == "private")
    def disable(m):
        global bot_status; bot_status = False
        bot.send_message(m.chat.id, "🔴 تم تعطيل البوت")

    # ===== ضفت دول عشان تفعيل الجروب =====
    @bot.message_handler(func=lambda m: m.text == "▶️ تفعيل البوت الخدمي")
    def enable_group(m):
        if m.chat.type in ["group", "supergroup"]:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO group_status VALUES (?, 1)", (m.chat.id,))
            conn.commit()
            conn.close()
            bot.send_message(m.chat.id, "✅ تم تفعيل البوت في هذه المجموعة")
        else:
            bot.send_message(m.chat.id, "الامر ده للجروبات فقط")

    @bot.message_handler(func=lambda m: m.text == "🔴 تعطيل البوت الخدمي" and m.chat.type in ["group", "supergroup"])
    def disable_group(m):
        if m.chat.type in ["group", "supergroup"]:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO group_status VALUES (?, 0)", (m.chat.id,))
            conn.commit()
            conn.close()
            bot.send_message(m.chat.id, "🔴 تم تعطيل البوت في هذه المجموعة")
        else:
            bot.send_message(m.chat.id, "الامر ده للجروبات فقط")
    # =======================================

    @bot.message_handler(func=lambda m: m.text == "📢 تغير قناة البوت")
    def ask_channel(m):
        msg = bot.send_message(m.chat.id, "ارسل رابط القناة الجديد:\nمثال: https://t.me/xxxx")
        bot.register_next_step_handler(msg, save_channel)

    def save_channel(m):
        DEV_DATA["channel"] = m.text
        bot.send_message(m.chat.id, f"✅ تم تغير قناة البوت الى:\n{m.text}")

    @bot.message_handler(func=lambda m: m.text == "👋 اضف ترحيب")
    def ask_welcome(m):
        msg = bot.send_message(m.chat.id, "ارسل رسالة الترحيب الجديدة")
        bot.register_next_step_handler(msg, save_welcome)

    def save_welcome(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("UPDATE welcome_msg SET text =?", (m.text,)); conn.commit(); conn.close()
        bot.send_message(m.chat.id, "✅ تم تغير رسالة الترحيب")

    @bot.message_handler(func=lambda m: m.text == "📊 الاحصائيات")
    def stats(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM groups"); groups = c.fetchone()[0]; conn.close()
        bot.send_message(m.chat.id, f"📊 الاحصائيات:\nالمستخدمين: {users}\nالمجموعات: {groups}")

    @bot.message_handler(func=lambda m: m.text == "📢 قناه تحديثات البوت")
    def show_channel(m):
        bot.send_message(m.chat.id, f"📢 قناة البوت:\n{DEV_DATA['channel']}")

    @bot.message_handler(func=lambda m: m.text == "⚙️ إعدادات البوت")
    def settings(m):
        bot.send_message(m.chat.id, "⚙️ اهلا في اعدادات البوت\nاختار من الازرار اللي تحت")

    @bot.message_handler(func=lambda m: m.text == "📢 أوامر الإذاعة")
    def broadcast(m):
        msg = bot.send_message(m.chat.id, "ارسل الرسالة للاذاعة للكل")
        bot.register_next_step_handler(msg, do_broadcast)

    def do_broadcast(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT user_id FROM users"); users = c.fetchall(); conn.close()
        for u in users:
            try: bot.send_message(u[0], f"📢 إذاعة:\n{m.text}")
            except: pass
        bot.send_message(m.chat.id, "✅ تمت الاذاعة")

    @bot.message_handler(func=lambda m: m.text in ["📋 قائمة العام","👑 تغيير المطور الاساسي","✨ مسح المطورين","🗂️ مسح اسم البوت","❌ مسح قائمة العام","✏️ تغيير اسم البوت","👥 مسح المطورين الثانويين","📵 تعطيل التواصل","📦 جلب النسخة الاحتياطيه","📲 تفعيل التواصل","🔄 تحديث الملفات","⚙️ 0_اظهار _ اخفاء _ قائمة اعداد البوت"])
    def other(m):
        bot.send_message(m.chat.id, f"تم الضغط على: {m.text}\n✅ الزر شغال")
