import os, sqlite3, shutil
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

DB_FILE = "bot_database.db"
bot_status = True
comm_status = True
OWNER_ID = "" # بنستلمه من main

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS group_status (chat_id INTEGER PRIMARY KEY, status INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS welcome_msg (id INTEGER PRIMARY KEY, text TEXT, photo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS dev_data (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS secondary_devs (user_id INTEGER PRIMARY KEY)")
    c.execute("INSERT OR IGNORE INTO welcome_msg (id, text, photo) VALUES (1, 'اهلا بيك في المجموعة', '')")
    c.execute("INSERT OR IGNORE INTO dev_data (key, value) VALUES ('channel', 'https://t.me/your_channel')")
    c.execute("INSERT OR IGNORE INTO dev_data (key, value) VALUES ('bot_name', 'Tia')")
    c.execute("INSERT OR IGNORE INTO dev_data (key, value) VALUES ('comm', '1')")
    conn.commit(); conn.close()
init_db()

def get_value(key):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT value FROM dev_data WHERE key=?", (key,)); res = c.fetchone(); conn.close()
    return res[0] if res else ""
def set_value(key, val):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE dev_data SET value=? WHERE key=?", (val, key)); conn.commit(); conn.close()
def get_comm(): return get_value('comm') == '1'

def get_dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📢 أوامر الإذاعة"), KeyboardButton("📋 قائمة العام"))
    markup.row(KeyboardButton("👑 تغيير المطور الاساسي"), KeyboardButton("✨ مسح المطورين"))
    markup.row(KeyboardButton("🗂️ مسح اسم البوت"), KeyboardButton("❌ مسح قائمة العام"))
    markup.row(KeyboardButton("✏️ تغيير اسم البوت"), KeyboardButton("👥 مسح المطورين الثانويين"))
    markup.row(KeyboardButton("📵 تعطيل التواصل"), KeyboardButton("📦 جلب النسخة الاحتياطيه"))
    markup.row(KeyboardButton("📲 تفعيل التواصل"), KeyboardButton("🔄 تحديث الملفات"))
    markup.row(KeyboardButton("🔴 تعطيل البوت الخدمي"), KeyboardButton("⚡ تفعيل البوت"))
    markup.row(KeyboardButton("⚙️ 0_اظهار _ اخفاء _ قائمة اعداد البوت"))
    markup.row(KeyboardButton("👋 اضف ترحيب"), KeyboardButton("🖼️ ترحيب بصوره"))
    markup.row(KeyboardButton("📢 تغير قناة البوت"), KeyboardButton("📢 قناه تحديثات البوت"))
    markup.row(KeyboardButton("❌ اخفاء الكيبورد"))
    return markup

def register_handlers(bot, owner_id):
    global bot_status, comm_status, OWNER_ID
    OWNER_ID = owner_id # نستلم الايدي هنا
    comm_status = get_comm()

    @bot.message_handler(func=lambda m: m.chat.type!= "private")
    def block_group(m): return

    @bot.message_handler(func=lambda m: str(m.from_user.id)!= OWNER_ID and m.chat.type == "private")
    def not_owner(m): bot.send_message(m.chat.id, "هذا الامر للمطور فقط")

    @bot.message_handler(func=lambda m: m.text == "❌ اخفاء الكيبورد" and m.chat.type == "private")
    def hide_kb(m): bot.send_message(m.chat.id, "تم اخفاء الكيبورد", reply_markup=ReplyKeyboardRemove())

    @bot.message_handler(func=lambda m: m.text == "⚡ تفعيل البوت" and m.chat.type == "private")
    def enable(m): global bot_status; bot_status = True; bot.send_message(m.chat.id, "✅ تم تفعيل البوت")

    @bot.message_handler(func=lambda m: m.text == "🔴 تعطيل البوت الخدمي" and m.chat.type == "private")
    def disable(m): global bot_status; bot_status = False; bot.send_message(m.chat.id, "🔴 تم تعطيل البوت")

    @bot.message_handler(func=lambda m: m.text == "👑 تغيير المطور الاساسي" and m.chat.type == "private")
    def ask_new_owner(m): bot.send_message(m.chat.id, "❌ ممنوع تغير المطور من هنا. غيره من متغيرات Railway: OWNER_ID")

    @bot.message_handler(func=lambda m: m.text == "📢 تغير قناة البوت" and m.chat.type == "private")
    def ask_channel(m): msg = bot.send_message(m.chat.id, "ارسل رابط القناة الجديد"); bot.register_next_step_handler(msg, lambda x: set_value('channel', x.text) or bot.send_message(x.chat.id, f"✅ تم حفظ القناة"))

    @bot.message_handler(func=lambda m: m.text == "👋 اضف ترحيب" and m.chat.type == "private")
    def ask_welcome(m): msg = bot.send_message(m.chat.id, "ارسل نص الترحيب الجديد"); bot.register_next_step_handler(msg, lambda x: save_welcome(x))
    def save_welcome(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("UPDATE welcome_msg SET text=?, photo='' WHERE id=1", (m.text,)); conn.commit(); conn.close()
        bot.send_message(m.chat.id, "✅ تم حفظ الترحيب")

    @bot.message_handler(func=lambda m: m.text == "🖼️ ترحيب بصوره" and m.chat.type == "private")
    def ask_welcome_photo(m): msg = bot.send_message(m.chat.id, "ارسل الصوره + الكابشن"); bot.register_next_step_handler(msg, lambda x: save_photo(bot, x))
    def save_photo(bot, m):
        if m.photo: conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("UPDATE welcome_msg SET text=?, photo=? WHERE id=1", (m.caption or "", m.photo[-1].file_id)); conn.commit(); conn.close(); bot.send_message(m.chat.id, "✅ تم حفظ الترحيب بصوره")
        else: bot.send_message(m.chat.id, "ارسل صوره")

    @bot.message_handler(func=lambda m: m.text == "📢 أوامر الإذاعة" and m.chat.type == "private")
    def broadcast(m): msg = bot.send_message(m.chat.id, "ارسل الرسالة للاذاعة"); bot.register_next_step_handler(msg, lambda x: do_broadcast(bot, x))
    def do_broadcast(bot, m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor(); groups = c.execute("SELECT chat_id FROM group_status WHERE status=1").fetchall(); conn.close()
        count=0
        for g in groups:
            try: bot.send_message(g[0], f"📢 إذاعة:\n{m.text}"); count+=1
            except: pass
        bot.send_message(m.chat.id, f"✅ تمت الاذاعة لـ {count} مجموعه")

    @bot.message_handler(func=lambda m: m.text == "📋 قائمة العام" and m.chat.type == "private")
    def list_groups(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor(); groups = c.execute("SELECT chat_id FROM group_status WHERE status=1").fetchall(); conn.close()
        txt = "📋 قائمة المجموعات:\n" + "\n".join([str(g[0]) for g in groups]) if groups else "مافي مجموعات"
        bot.send_message(m.chat.id, txt)

    @bot.message_handler(func=lambda m: m.text == "❌ مسح قائمة العام" and m.chat.type == "private")
    def clear_groups(m): conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("DELETE FROM group_status"); conn.commit(); conn.close(); bot.send_message(m.chat.id, "✅ تم المسح")

    @bot.message_handler(func=lambda m: m.text == "✨ مسح المطورين" and m.chat.type == "private")
    def clear_devs(m): conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("DELETE FROM secondary_devs"); conn.commit(); conn.close(); bot.send_message(m.chat.id, "✅ تم مسح المطورين")

    @bot.message_handler(func=lambda m: m.text == "👥 مسح المطورين الثانويين" and m.chat.type == "private")
    def list_devs(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor(); devs = c.execute("SELECT user_id FROM secondary_devs").fetchall(); conn.close()
        txt = "👥 المطورين:\n" + "\n".join([str(d[0]) for d in devs]) if devs else "مافي مطورين"
        bot.send_message(m.chat.id, txt)

    @bot.message_handler(func=lambda m: m.text == "✏️ تغيير اسم البوت" and m.chat.type == "private")
    def ask_name(m): msg = bot.send_message(m.chat.id, "ارسل الاسم الجديد"); bot.register_next_step_handler(msg, lambda x: set_value('bot_name', x.text) or bot.send_message(x.chat.id, f"✅ تم التغير الى {x.text}"))

    @bot.message_handler(func=lambda m: m.text == "🗂️ مسح اسم البوت" and m.chat.type == "private")
    def reset_name(m): set_value('bot_name', 'Tia'); bot.send_message(m.chat.id, "✅ تم ارجاع الاسم Tia")

    @bot.message_handler(func=lambda m: m.text == "📦 جلب النسخة الاحتياطيه" and m.chat.type == "private")
    def backup(m): shutil.copy(DB_FILE, "backup.db"); bot.send_document(m.chat.id, open("backup.db", 'rb'))

    @bot.message_handler(func=lambda m: m.text == "🔄 تحديث الملفات" and m.chat.type == "private")
    def restart(m): bot.send_message(m.chat.id, "🔄 جاري اعادة التشغيل..."); os._exit(0)

    @bot.message_handler(func=lambda m: m.text == "📊 الاحصائيات" and m.chat.type == "private")
    def stats(m): conn = sqlite3.connect(DB_FILE); c = conn.cursor(); groups = c.execute("SELECT COUNT(*) FROM group_status WHERE status=1").fetchone()[0]; conn.close(); bot.send_message(m.chat.id, f"📊 الاحصائيات:\nالبوت: {'شغال' if bot_status else 'متوقف'}\nالتواصل: {'مفعل' if comm_status else 'معطل'}\nالمجموعات: {groups}")

    @bot.message_handler(func=lambda m: m.text == "📢 قناه تحديثات البوت" and m.chat.type == "private")
    def show_channel(m): bot.send_message(m.chat.id, f"📢 القناة:\n{get_value('channel')}")

    @bot.message_handler(func=lambda m: m.text == "⚙️ إعدادات البوت" and m.chat.type == "private")
    def settings(m): bot.send_message(m.chat.id, f"⚙️ الاعدادات:\nالاسم: {get_value('bot_name')}\nالمطور: {OWNER_ID}\nالقناة: {get_value('channel')}")

    @bot.message_handler(func=lambda m: m.text == "📲 تفعيل التواصل" and m.chat.type == "private")
    def enable_comm(m): global comm_status; comm_status = True; set_value('comm', '1'); bot.send_message(m.chat.id, "✅ تم تفعيل التواصل")

    @bot.message_handler(func=lambda m: m.text == "📵 تعطيل التواصل" and m.chat.type == "private")
    def disable_comm(m): global comm_status; comm_status = False; set_value('comm', '0'); bot.send_message(m.chat.id, "🔴 تم تعطيل التواصل")

    @bot.message_handler(func=lambda m: m.text == "⚙️ 0_اظهار _ اخفاء _ قائمة اعداد البوت" and m.chat.type == "private")
    def toggle_menu(m): bot.send_message(m.chat.id, "الكيبورد", reply_markup=get_dev_keyboard())
