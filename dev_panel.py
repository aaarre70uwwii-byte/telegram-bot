import os, sqlite3, shutil, threading
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

DB_FILE = "bot_database.db"
bot_status = True
comm_status = True
OWNER_ID = ""

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

def get_comm():
    return get_value('comm') == '1'

def get_dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📢 أوامر الإذاعة"), KeyboardButton("📋 قائمة العام"))
    markup.row(KeyboardButton("👑 اضافة مطور"), KeyboardButton("👑 حذف مطور"), KeyboardButton("👥 المطورين الثانويين"))
    markup.row(KeyboardButton("🗂️ مسح اسم البوت"), KeyboardButton("❌ مسح قائمة العام"), KeyboardButton("✨ مسح المطورين"))
    markup.row(KeyboardButton("✏️ تغيير اسم البوت"), KeyboardButton("📵 تعطيل التواصل"), KeyboardButton("📲 تفعيل التواصل"))
    markup.row(KeyboardButton("📦 جلب النسخة الاحتياطيه"), KeyboardButton("🔄 تحديث الملفات"), KeyboardButton("📊 الاحصائيات"))
    markup.row(KeyboardButton("🔴 تعطيل البوت الخدمي"), KeyboardButton("⚡ تفعيل البوت"))
    markup.row(KeyboardButton("👋 اضف ترحيب"), KeyboardButton("🖼️ ترحيب بصوره"))
    markup.row(KeyboardButton("📢 تغير قناة البوت"), KeyboardButton("📢 قناه تحديثات البوت"))
    markup.row(KeyboardButton("❌ اخفاء الكيبورد"))
    return markup

def register_handlers(bot, owner_id):
    global bot_status, comm_status, OWNER_ID
    OWNER_ID = owner_id
    comm_status = get_comm()

    def is_owner(m):
        return str(m.from_user.id) == OWNER_ID and m.chat.type == "private"

    @bot.message_handler(func=lambda m: m.chat.type == "private" and not is_owner(m))
    def not_owner(m):
        bot.send_message(m.chat.id, "❌ هذا الامر للمطور فقط")

    @bot.message_handler(func=lambda m: m.text == "❌ اخفاء الكيبورد" and is_owner(m))
    def hide_kb(m):
        bot.send_message(m.chat.id, "✅ تم اخفاء الكيبورد", reply_markup=ReplyKeyboardRemove())

    @bot.message_handler(func=lambda m: m.text == "⚡ تفعيل البوت" and is_owner(m))
    def enable(m):
        global bot_status; bot_status = True
        bot.send_message(m.chat.id, "✅ تم تفعيل البوت")

    @bot.message_handler(func=lambda m: m.text == "🔴 تعطيل البوت الخدمي" and is_owner(m))
    def disable(m):
        global bot_status; bot_status = False
        bot.send_message(m.chat.id, "🔴 تم تعطيل البوت")

    @bot.message_handler(func=lambda m: m.text == "👑 اضافة مطور" and is_owner(m))
    def add_dev(m):
        msg = bot.send_message(m.chat.id, "ارسل ايدي المطور الجديد");
        bot.register_next_step_handler(msg, save_dev)
    def save_dev(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO secondary_devs VALUES (?)", (m.text,));
        conn.commit(); conn.close()
        bot.send_message(m.chat.id, f"✅ تم اضافة المطور {m.text}")

    @bot.message_handler(func=lambda m: m.text == "👑 حذف مطور" and is_owner(m))
    def del_dev(m):
        msg = bot.send_message(m.chat.id, "ارسل ايدي المطور للحذف");
        bot.register_next_step_handler(msg, del_dev2)
    def del_dev2(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("DELETE FROM secondary_devs WHERE user_id=?", (m.text,));
        conn.commit(); conn.close()
        bot.send_message(m.chat.id, f"✅ تم حذف المطور {m.text}")

    @bot.message_handler(func=lambda m: m.text == "📢 تغير قناة البوت" and is_owner(m))
    def ask_channel(m):
        msg = bot.send_message(m.chat.id, "ارسل رابط القناة الجديد");
        bot.register_next_step_handler(msg, lambda x: set_value('channel', x.text) or bot.send_message(x.chat.id, f"✅ تم حفظ القناة"))

    @bot.message_handler(func=lambda m: m.text == "👋 اضف ترحيب" and is_owner(m))
    def ask_welcome(m):
        msg = bot.send_message(m.chat.id, "ارسل نص الترحيب الجديد");
        bot.register_next_step_handler(msg, save_welcome)
    def save_welcome(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("UPDATE welcome_msg SET text=?, photo='' WHERE id=1", (m.text,));
        conn.commit(); conn.close()
        bot.send_message(m.chat.id, "✅ تم حفظ الترحيب")

    @bot.message_handler(func=lambda m: m.text == "🖼️ ترحيب بصوره" and is_owner(m))
    def ask_welcome_photo(m):
        msg = bot.send_message(m.chat.id, "ارسل الصوره + الكابشن");
        bot.register_next_step_handler(msg, save_photo)
    def save_photo(m):
        if m.photo:
            conn = sqlite3.connect(DB_FILE); c = conn.cursor()
            c.execute("UPDATE welcome_msg SET text=?, photo=? WHERE id=1", (m.caption or "", m.photo[-1].file_id));
            conn.commit(); conn.close()
            bot.send_message(m.chat.id, "✅ تم حفظ الترحيب بصوره")
        else:
            bot.send_message(m.chat.id, "ارسل صوره")

    @bot.message_handler(func=lambda m: m.text == "📢 أوامر الإذاعة" and is_owner(m))
    def broadcast(m):
        msg = bot.send_message(m.chat.id, "ارسل الرسالة للاذاعة");
        bot.register_next_step_handler(msg, do_broadcast)
    def do_broadcast(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        groups = c.execute("SELECT chat_id FROM group_status WHERE status=1").fetchall();
        conn.close()
        count=0
        for g in groups:
            try:
                bot.send_message(g[0], f"📢 إذاعة:\n{m.text}");
                count+=1
            except:
                pass
        bot.send_message(m.chat.id, f"✅ تمت الاذاعة لـ {count} مجموعه")

    @bot.message_handler(func=lambda m: m.text == "📋 قائمة العام" and is_owner(m))
    def list_groups(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        groups = c.execute("SELECT chat_id FROM group_status WHERE status=1").fetchall();
        conn.close()
        txt = "📋 قائمة المجموعات:\n" + "\n".join([str(g[0]) for g in groups]) if groups else "مافي مجموعات"
        bot.send_message(m.chat.id, txt)

    @bot.message_handler(func=lambda m: m.text == "❌ مسح قائمة العام" and is_owner(m))
    def clear_groups(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("DELETE FROM group_status");
        conn.commit(); conn.close()
        bot.send_message(m.chat.id, "✅ تم مسح قائمة العام")

    @bot.message_handler(func=lambda m: m.text == "✨ مسح المطورين" and is_owner(m))
    def clear_devs(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("DELETE FROM secondary_devs");
        conn.commit(); conn.close()
        bot.send_message(m.chat.id, "✅ تم مسح المطورين الثانويين")

    @bot.message_handler(func=lambda m: m.text == "👥 المطورين الثانويين" and is_owner(m))
    def list_devs(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        devs = c.execute("SELECT user_id FROM secondary_devs").fetchall();
        conn.close()
        txt = "👥 المطورين الثانويين:\n" + "\n".join([str(d[0]) for d in devs]) if devs else "مافي مطورين"
        bot.send_message(m.chat.id, txt)

    @bot.message_handler(func=lambda m: m.text == "✏️ تغيير اسم البوت" and is_owner(m))
    def ask_name(m):
        msg = bot.send_message(m.chat.id, "ارسل الاسم الجديد");
        bot.register_next_step_handler(msg, lambda x: set_value('bot_name', x.text) or bot.send_message(x.chat.id, f"✅ تم التغير الى {x.text}"))

    @bot.message_handler(func=lambda m: m.text == "🗂️ مسح اسم البوت" and is_owner(m))
    def reset_name(m):
        set_value('bot_name', 'Tia')
        bot.send_message(m.chat.id, "✅ تم ارجاع الاسم Tia")

    @bot.message_handler(func=lambda m: m.text == "📦 جلب النسخة الاحتياطيه" and is_owner(m))
    def backup(m):
        shutil.copy(DB_FILE, "backup.db")
        bot.send_document(m.chat.id, open("backup.db", 'rb'))

    @bot.message_handler(func=lambda m: m.text == "🔄 تحديث الملفات" and is_owner(m))
    def restart(m):
        bot.send_message(m.chat.id, "🔄 جاري اعادة التشغيل...")
        threading.Timer(1.0, lambda: os._exit(0)).start()

    @bot.message_handler(func=lambda m: m.text == "📊 الاحصائيات" and is_owner(m))
    def stats(m):
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        groups = c.execute("SELECT COUNT(*) FROM group_status WHERE status=1").fetchone()[0];
        conn.close()
        bot.send_message(m.chat.id, f"📊 الاحصائيات:\nالبوت: {'شغال' if bot_status else 'متوقف'}\nالتواصل: {'مفعل' if comm_status else 'معطل'}\nالمجموعات: {groups}")

    @bot.message_handler(func=lambda m: m.text == "📢 قناه تحديثات البوت" and is_owner(m))
    def show_channel(m):
        bot.send_message(m.chat.id, f"📢 القناة:\n{get_value('channel')}")

    @bot.message_handler(func=lambda m: m.text == "⚙️ إعدادات البوت" and is_owner(m))
    def settings(m):
        bot.send_message(m.chat.id, f"⚙️ الاعدادات:\nالاسم: {get_value('bot_name')}\nالمطور: {OWNER_ID}\nالقناة: {get_value('channel')}")

    @bot.message_handler(func=lambda m: m.text == "📲 تفعيل التواصل" and is_owner(m))
    def enable_comm(m):
        global comm_status; comm_status = True; set_value('comm', '1')
        bot.send_message(m.chat.id, "✅ تم تفعيل التواصل")

    @bot.message_handler(func=lambda m: m.text == "📵 تعطيل التواصل" and is_owner(m))
    def disable_comm(m):
        global comm_status; comm_status = False; set_value('comm', '0')
        bot.send_message(m.chat.id, "🔴 تم تعطيل التواصل")
