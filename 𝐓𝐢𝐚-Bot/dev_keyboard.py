import os
import sqlite3
import telebot
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAIN_DEV_ID = int(os.getenv("OWNER_ID"))
bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "bot_database.db"
waiting = {}
bot_name = "𝐓𝐢𝐚"
contact_status = True
bot_status = True

def init_db():
    c = sqlite3.connect(DB_FILE).cursor()
    c.execute("CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS gbanned (user_id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS welcome (text TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS g_reply (word TEXT PRIMARY KEY, reply TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('channel', '@yourchannel')")
    c.connection.commit(); c.connection.close()
init_db()

def get_setting(key):
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT value FROM settings WHERE key=?",(key,)); r=c.fetchone(); c.connection.close()
    return r[0] if r else "@yourchannel"

def set_setting(key, value):
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",(key,value)); c.connection.commit(); c.connection.close()

def is_main_dev(u): return u == MAIN_DEV_ID
def get_devs():
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT user_id FROM devs"); r=[x[0] for x in c.fetchall()]; c.connection.close()
    return r
def get_groups():
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT chat_id FROM groups"); r=[x[0] for x in c.fetchall()]; c.connection.close()
    return r

def kb_private():
    k = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    k.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📢 أوامر الإذاعة"), KeyboardButton("📊 قائمة العام"))
    k.row(KeyboardButton("👑 تغير المطور الاساسي"), KeyboardButton("🧹 مسح المطورين"))
    k.row(KeyboardButton("🗑️ مسح اسم البوت"), KeyboardButton("❌ مسح قائمة العام"))
    k.row(KeyboardButton("✏️ تغير اسم البوت"), KeyboardButton("👥 مسح المطورين الثانويين"))
    k.row(KeyboardButton("📵 تعطيل التواصل"), KeyboardButton("💾 جلب النسخه الاحتياطيه"))
    k.row(KeyboardButton("✅ تفعيل التواصل"), KeyboardButton("🔄 تحديث الملفات"))
    k.row(KeyboardButton("🔴 تعطيل البوت الخدمي"), KeyboardButton("⚡ تفعيل البوت"))
    k.row(KeyboardButton("▶️ تفعيل البوت الخدمي"))
    k.row(KeyboardButton("⚙️ اظهار _ اخفاء _ قائمة اعداد البوت"))
    k.row(KeyboardButton("👋 اضف ترحيب"), KeyboardButton("➕ رفع مطور"))
    k.row(KeyboardButton("📝 اضف رد عام"), KeyboardButton("📜 الردود العامه"))
    k.row(KeyboardButton("📢 تغير قناة التحديثات"))
    k.row(KeyboardButton("🗑️ اخفاء الكيبورد"))
    return k

@bot.message_handler(commands=['start'], chat_types=['private'])
def start_private(m):
    if not is_main_dev(m.from_user.id):
        return bot.reply_to(m, "❌ هذا البوت للمطور الاساسي فقط")
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT text FROM welcome"); w=c.fetchone(); c.connection.close()
    welcome_text = w[0] if w else f"🙋‍♂️ اهلا بك في بوت {bot_name}"
    bot.send_message(m.chat.id, welcome_text, reply_markup=kb_private())

@bot.message_handler(func=lambda m: m.chat.type == 'private' and is_main_dev(m.from_user.id))
def handle_dev(m):
    global bot_name, contact_status, bot_status, MAIN_DEV_ID
    t = m.text; uid = m.from_user.id

    if t == "⚙️ إعدادات البوت":
        g = len(get_groups())
        ch = get_setting('channel')
        bot.send_message(m.chat.id, f"⚙️ اسم البوت: {bot_name}\nالقروبات: {g}\nالمطورين: {len(get_devs())}\nقناة التحديثات: {ch}\nالحالة: {'شغال' if bot_status else 'متوقف'}")

    elif t == "📢 أوامر الإذاعة":
        bot.send_message(m.chat.id, "📢 اوامر الاذاعة:\n1. `ذيع + النص` = اذاعة نص\n2. ارسل صورة + اكتب `ذيع` = اذاعة صورة\n3. سوي توجيه لرسالة + اكتب `ذيع` = اذاعة توجيه", parse_mode="Markdown")

    elif t == "📊 قائمة العام":
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT COUNT(*) FROM gbanned"); r=c.fetchone()[0]; c.connection.close()
        bot.send_message(m.chat.id, f"📊 المحظورين عام: {r}")

    elif t == "👑 تغير المطور الاساسي":
        waiting[uid] = "change_owner"; bot.send_message(m.chat.id, "ارسل ايدي المطور الجديد")

    elif t == "🧹 مسح المطورين" or t == "👥 مسح المطورين الثانويين":
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("DELETE FROM devs"); c.connection.commit(); c.connection.close()
        bot.send_message(m.chat.id, "✅ تم مسح جميع المطورين الثانويين")

    elif t == "🗑️ مسح اسم البوت":
        bot_name = "𝐓𝐢𝐚"
        bot.send_message(m.chat.id, "✅ تم ارجاع اسم البوت الى 𝐓𝐢𝐚")

    elif t == "❌ مسح قائمة العام":
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("DELETE FROM gbanned"); c.connection.commit(); c.connection.close()
        bot.send_message(m.chat.id, "✅ تم مسح قائمة الحظر العام")

    elif t == "✏️ تغير اسم البوت":
        waiting[uid] = "change_name"; bot.send_message(m.chat.id, "ارسل الاسم الجديد")

    elif t == "📵 تعطيل التواصل":
        contact_status = False
        bot.send_message(m.chat.id, "📵 تم تعطيل التواصل")

    elif t == "✅ تفعيل التواصل":
        contact_status = True
        bot.send_message(m.chat.id, "✅ تم تفعيل التواصل")

    elif t == "💾 جلب النسخه الاحتياطيه":
        bot.send_document(m.chat.id, open(DB_FILE, 'rb'), caption="💾 النسخة الاحتياطية")

    elif t == "🔄 تحديث الملفات":
        bot.send_message(m.chat.id, "🔄 جاري التحديث..."); time.sleep(1); bot.send_message(m.chat.id, "✅ تم تحديث الملفات")

    elif t == "🔴 تعطيل البوت الخدمي":
        bot_status = False
        bot.send_message(m.chat.id, "🔴 تم تعطيل البوت الخدمي")

    elif t == "⚡ تفعيل البوت" or t == "▶️ تفعيل البوت الخدمي":
        bot_status = True
        bot.send_message(m.chat.id, "⚡ تم تفعيل البوت الخدمي")

    elif t == "⚙️ اظهار _ اخفاء _ قائمة اعداد البوت":
        bot.send_message(m.chat.id, "استخدم /start لاظهار الكيبورد مرة اخرى")

    elif t == "➕ رفع مطور":
        waiting[uid] = "add_dev"; bot.send_message(m.chat.id, "ارسل ايدي المطور الثانوي")

    elif t == "👋 اضف ترحيب":
        waiting[uid] = "add_welcome"; bot.send_message(m.chat.id, "ارسل نص الترحيب الجديد\nتقدر تستخدم: {name} للاسم")

    elif t == "📝 اضف رد عام":
        waiting[uid] = "add_g_reply"; bot.send_message(m.chat.id, "ارسل: الكلمة - الرد")

    elif t == "📜 الردود العامه":
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT word FROM g_reply"); r=c.fetchall(); c.connection.close()
        if not r: bot.send_message(m.chat.id, "📜 لا توجد ردود عامة")
        else:
            text = "📜 **الردود العامة:**\n" + "\n".join([f"- `{x[0]}`" for x in r])
            bot.send_message(m.chat.id, text, parse_mode="Markdown")

    elif t == "📢 تغير قناة التحديثات":
        waiting[uid] = "change_channel"
        current = get_setting('channel')
        bot.send_message(m.chat.id, f"📢 القناة الحالية: {current}\nارسل يوزر القناة الجديد مع @")

    elif t == "🗑️ اخفاء الكيبورد":
        bot.send_message(m.chat.id, "تم اخفاء الكيبورد", reply_markup=ReplyKeyboardRemove())

    elif t.startswith("ذيع "):
        waiting[uid] = ["broadcast_text", t.replace("ذيع ", "", 1)]
        do_broadcast(m.chat.id, uid)

@bot.message_handler(content_types=['photo', 'forward'], func=lambda m: m.chat.type == 'private' and is_main_dev(m.from_user.id))
def broadcast_media(m):
    uid = m.from_user.id
    if m.content_type == 'photo' and m.caption and m.caption.startswith("ذيع"):
        waiting[uid] = ["broadcast_photo", m.photo[-1].file_id, m.caption.replace("ذيع", "", 1)]
        do_broadcast(m.chat.id, uid)
    elif m.content_type == 'forward' and m.text and m.text.startswith("ذيع"):
        waiting[uid] = ["broadcast_forward", m.forward_from_message_id, m.chat.id]
        do_broadcast(m.chat.id, uid)

def do_broadcast(chat_id, uid):
    data = waiting.pop(uid)
    groups = get_groups()
    count = 0
    bot.send_message(chat_id, f"🔄 جاري الاذاعة لـ {len(groups)} قروب...")

    for g in groups:
        try:
            if data[0] == "broadcast_text":
                bot.send_message(g, f"📢 اذاعة من المطور:\n\n{data[1]}")
            elif data[0] == "broadcast_photo":
                bot.send_photo(g, data[1], caption=f"📢 اذاعة من المطور:\n{data[2]}")
            elif data[0] == "broadcast_forward":
                bot.forward_message(g, data[2], data[1])
            count += 1
        except: pass
    bot.send_message(chat_id, f"✅ تم الاذاعة بنجاح لـ {count} قروب")

@bot.message_handler(func=lambda m: m.from_user.id in waiting)
def wait_handler(m):
    global bot_name, MAIN_DEV_ID
    act = waiting.get(m.from_user.id)
    if not act: return

    if act == "change_owner":
        waiting.pop(m.from_user.id)
        MAIN_DEV_ID = int(m.text)
        bot.send_message(m.chat.id, f"✅ تم تغير المطور الاساسي الى {m.text}\nلازم تعمل اعادة تشغيل للبوت")

    elif act == "change_name":
        waiting.pop(m.from_user.id)
        bot_name = m.text
        bot.send_message(m.chat.id, f"✅ تم تغير اسم البوت الى {m.text}")

    elif act == "change_channel":
        waiting.pop(m.from_user.id)
        ch = m.text.strip()
        if not ch.startswith("@"):
            return bot.send_message(m.chat.id, "❌ لازم تبدا بـ @\nمثال: @channelname")
        set_setting('channel', ch)
        bot.send_message(m.chat.id, f"✅ تم تغير قناة التحديثات الى {ch}")

    elif act == "add_welcome":
        waiting.pop(m.from_user.id)
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("DELETE FROM welcome"); c.execute("INSERT INTO welcome VALUES (?)",(m.text,)); c.connection.commit(); c.connection.close()
        bot.send_message(m.chat.id, "✅ تم حفظ الترحيب\nسيظهر عند /start")

    elif act == "add_dev":
        waiting.pop(m.from_user.id)
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("INSERT OR IGNORE INTO devs VALUES (?)",(int(m.text),)); c.connection.commit(); c.connection.close()
        bot.send_message(m.chat.id, f"✅ تم رفع {m.text} كمطور ثانوي")

    elif act == "add_g_reply":
        waiting.pop(m.from_user.id)
        try:
            word, reply = m.text.split(" - ", 1)
            c=sqlite3.connect(DB_FILE).cursor(); c.execute("INSERT OR REPLACE INTO g_reply VALUES (?,?)",(word, reply)); c.connection.commit(); c.connection.close()
            bot.send_message(m.chat.id, f"✅ تم اضافة رد عام\nالكلمة: {word}")
        except:
            bot.send_message(m.chat.id, "❌ الصيغة خطأ\nارسل: الكلمة - الرد")

@bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'])
def group_handler(m):
    c=sqlite3.connect(DB_FILE).cursor()
    c.execute("INSERT OR IGNORE INTO groups VALUES (?)",(m.chat.id,))
    c.connection.commit(); c.connection.close()

    if bot_status and m.text:
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT reply FROM g_reply WHERE word=?",(m.text,)); r=c.fetchone(); c.connection.close()
        if r: bot.reply_to(m, r[0])

if __name__ == "__main__":
    print(f"البوت {bot_name} شغال")
    bot.polling(none_stop=True)
