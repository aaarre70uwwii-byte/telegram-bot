import os
import sqlite3
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

DB_FILE = "bot_database.db"
waiting = {}
MAIN_DEV_ID = 7488375443 # << ايديك
DEV_DATA = {
    "channel": "@TiaUpdates", # تقدر تغيره من الزر
    "bot_name": "𝐓𝐢𝐚", # << اسم البوت
    "welcome": "🙋‍♂️ اهلا بك في بوت 𝐓𝐢𝐚"
}
contact_status = True
bot_status = True

def get_dev_keyboard():
    k = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    k.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📣 أوامر الإذاعة"), KeyboardButton("📊 قائمة العام"))
    k.row(KeyboardButton("👑 تغير المطور الاساسي"), KeyboardButton("🧹 مسح المطورين"))
    k.row(KeyboardButton("🗑️ مسح اسم البوت"), KeyboardButton("❌ مسح قائمة العام"))
    k.row(KeyboardButton("✏️ تغير اسم البوت"), KeyboardButton("👥 مسح المطورين الثانويين"))
    k.row(KeyboardButton("📵 تعطيل التواصل"), KeyboardButton("💾 جلب النسخه الاحتياطيه"))
    k.row(KeyboardButton("✅ تفعيل التواصل"), KeyboardButton("🔄 تحديث الملفات"))
    k.row(KeyboardButton("🔴 تعطيل البوت الخدمي"), KeyboardButton("⚡ تفعيل البوت"))
    k.row(KeyboardButton("▶️ تفعيل البوت الخدمي"))
    k.row(KeyboardButton("⚙️ اظهار _ اخفاء • قائمة اعداد البوت"))
    k.row(KeyboardButton("👋 اضف ترحيب"))
    k.row(KeyboardButton("📢 قناة تحديثات البوت"))
    k.row(KeyboardButton("🗑️ اخفاء الكيبورد"))
    return k

def get_setting(key):
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"); c.execute("SELECT value FROM settings WHERE key=?",(key,)); r=c.fetchone(); c.connection.close()
    return r[0] if r else DEV_DATA["channel"]

def set_setting(key, value):
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"); c.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",(key,value)); c.connection.commit(); c.connection.close()

def get_stats():
    c=sqlite3.connect(DB_FILE).cursor()
    c.execute("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    c.execute("SELECT COUNT(*) FROM groups"); groups=c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users"); users=c.fetchone()[0]
    c.connection.close()
    return users, groups

def broadcast_message(bot, text):
    c=sqlite3.connect(DB_FILE).cursor()
    c.execute("SELECT user_id FROM users"); users=[x[0] for x in c.fetchall()]
    c.execute("SELECT chat_id FROM groups"); groups=[x[0] for x in c.fetchall()]
    c.connection.close()
    success = 0; fail = 0
    for chat_id in users + groups:
        try:
            bot.send_message(chat_id, f"📢 **اذاعة من {DEV_DATA['bot_name']}**\n\n{text}", parse_mode="Markdown")
            success += 1; time.sleep(0.1) # عشان ما يعمل حظر
        except: fail += 1
    return success, fail

def register_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type == 'private' and m.from_user.id == MAIN_DEV_ID)
    def handle_dev(m):
        global waiting, contact_status, bot_status, DEV_DATA
        t = m.text

        if t == "⚙️ إعدادات البوت":
            users, groups = get_stats()
            status = f"⚙️ **إعدادات {DEV_DATA['bot_name']}:**\n\n🤖 الاسم: {DEV_DATA['bot_name']}\n📢 القناة: {get_setting('channel')}\n👥 المستخدمين: {users}\n👨‍👩‍👧‍👦 القروبات: {groups}\n📵 التواصل: {'مفعل' if contact_status else 'معطل'}\n⚡ البوت: {'شغال' if bot_status else 'متوقف'}"
            bot.send_message(m.chat.id, status, parse_mode="Markdown")

        elif t == "📊 قائمة العام":
            users, groups = get_stats()
            bot.send_message(m.chat.id, f"📊 **إحصائيات {DEV_DATA['bot_name']}:**\n\n👥 المستخدمين: {users}\n👨‍👩‍👧‍👦 القروبات: {groups}\n📨 الاجمالي: {users+groups}")

        elif t == "📣 أوامر الإذاعة":
            sent = bot.send_message(m.chat.id, "📣 ارسل نص الاذاعة الان:\n*سيرسل لكل القروبات والخاص*")
            bot.register_next_step_handler(sent, lambda msg: process_broadcast(bot, msg))

        elif t == "👑 تغير المطور الاساسي":
            sent = bot.send_message(m.chat.id, "👑 ارسل ايدي المطور الجديد:")
            bot.register_next_step_handler(sent, process_change_owner)

        elif t == "🧹 مسح المطورين" or t == "👥 مسح المطورين الثانويين":
            c=sqlite3.connect(DB_FILE).cursor(); c.execute("CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)"); c.execute("DELETE FROM devs"); c.connection.commit(); c.connection.close()
            bot.send_message(m.chat.id, "✅ تم مسح جميع المطورين الثانويين")

        elif t == "🗑️ مسح اسم البوت":
            DEV_DATA["bot_name"] = "𝐓𝐢𝐚"
            bot.send_message(m.chat.id, "✅ تم ارجاع اسم البوت الى 𝐓𝐢𝐚")

        elif t == "❌ مسح قائمة العام":
            c=sqlite3.connect(DB_FILE).cursor(); c.execute("CREATE TABLE IF NOT EXISTS gbanned (user_id INTEGER PRIMARY KEY)"); c.execute("DELETE FROM gbanned"); c.connection.commit(); c.connection.close()
            bot.send_message(m.chat.id, "✅ تم مسح قائمة الحظر العام")

        elif t == "✏️ تغير اسم البوت":
            sent = bot.send_message(m.chat.id, "✏️ ارسل اسم البوت الجديد:")
            bot.register_next_step_handler(sent, process_change_name)

        elif t == "📵 تعطيل التواصل": contact_status = False; bot.send_message(m.chat.id, "📵 تم تعطيل التواصل")
        elif t == "✅ تفعيل التواصل": contact_status = True; bot.send_message(m.chat.id, "✅ تم تفعيل التواصل")
        elif t == "💾 جلب النسخه الاحتياطيه": bot.send_document(m.chat.id, open(DB_FILE, 'rb'), caption="💾 النسخة الاحتياطية")
        elif t == "🔄 تحديث الملفات": bot.send_message(m.chat.id, "🔄 جاري التحديث..."); time.sleep(1); bot.send_message(m.chat.id, "✅ تم تحديث الملفات")
        elif t == "🔴 تعطيل البوت الخدمي": bot_status = False; bot.send_message(m.chat.id, "🔴 تم تعطيل البوت الخدمي")
        elif t == "⚡ تفعيل البوت" or t == "▶️ تفعيل البوت الخدمي": bot_status = True; bot.send_message(m.chat.id, "⚡ تم تفعيل البوت الخدمي")
        elif t == "⚙️ اظهار _ اخفاء • قائمة اعداد البوت": bot.send_message(m.chat.id, "استخدم /start لاظهار الكيبورد", reply_markup=ReplyKeyboardRemove())
        elif t == "👋 اضف ترحيب":
            sent = bot.send_message(m.chat.id, "👋 ارسل نص الترحيب الجديد:\nتقدر تستخدم {name} للاسم")
            bot.register_next_step_handler(sent, process_change_welcome)
        elif t == "📢 قناة تحديثات البوت":
            current = get_setting('channel')
            sent = bot.send_message(m.chat.id, f"📢 القناة الحالية: `{current}`\n\nارسل يوزر القناة الجديد مع @", parse_mode="Markdown")
            bot.register_next_step_handler(sent, process_change_channel)
        elif t == "🗑️ اخفاء الكيبورد":
            bot.send_message(m.chat.id, "✅ تم اخفاء الكيبورد", reply_markup=ReplyKeyboardRemove())

    def process_broadcast(bot, message):
        bot.send_message(message.chat.id, "📢 جاري الارسال... انتظر")
        success, fail = broadcast_message(bot, message.text)
        bot.send_message(message.chat.id, f"✅ **تمت الاذاعة**\n\n📨 وصل: {success}\n❌ فشل: {fail}")

    def process_change_owner(message):
        global MAIN_DEV_ID
        try:
            MAIN_DEV_ID = int(message.text)
            bot.send_message(message.chat.id, f"✅ تم تغير المطور الاساسي الى `{message.text}`\n⚠️ لازم تعمل اعادة تشغيل للبوت", parse_mode="Markdown")
        except: bot.send_message(message.chat.id, "❌ الايدي خطأ")

    def process_change_name(message):
        DEV_DATA["bot_name"] = message.text
        bot.send_message(message.chat.id, f"✅ تم تغير اسم البوت الى: {message.text}")

    def process_change_welcome(message):
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("CREATE TABLE IF NOT EXISTS welcome (text TEXT)"); c.execute("DELETE FROM welcome"); c.execute("INSERT INTO welcome VALUES (?)",(message.text,)); c.connection.commit(); c.connection.close()
        DEV_DATA["welcome"] = message.text
        bot.send_message(message.chat.id, "✅ تم حفظ الترحيب الجديد")

    def process_change_channel(message):
        ch = message.text.strip()
        if not ch.startswith("@"):
            return bot.send_message(message.chat.id, "❌ لازم تبدا بـ @\nمثال: @TiaUpdates")
        set_setting('channel', ch)
        DEV_DATA["channel"] = ch
        bot.send_message(message.chat.id, f"✅ تم تغير قناة البوت الى: {ch}")
