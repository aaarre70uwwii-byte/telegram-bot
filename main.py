import os
import sqlite3
import telebot
import time

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

@bot.message_handler(commands=['start'], chat_types=['private'])
def start_private(m):
    if not is_main_dev(m.from_user.id):
        return bot.reply_to(m, "❌ هذا البوت للمطور الاساسي فقط")
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT text FROM welcome"); w=c.fetchone(); c.connection.close()
    welcome_text = w[0] if w else f"🙋‍♂️ اهلا بك في بوت {bot_name}"
    help_text = f"""
⚙️ اوامر بوت {bot_name}:
`/settings` - اعدادات البوت
`/broadcast` - شرح الاذاعة
`/gbanned` - قائمة العام
`/setowner` - تغير المطور الاساسي
`/deldevs` - مسح المطورين
`/setname` - تغير اسم البوت
`/delname` - ارجاع اسم البوت
`/delgbanned` - مسح قائمة العام
`/contactoff` - تعطيل التواصل
`/contacton` - تفعيل التواصل
`/backup` - جلب النسخة الاحتياطية
`/restart` - تحديث الملفات
`/botstop` - تعطيل البوت
`/botstart` - تفعيل البوت
`/addwelcome` - اضافة ترحيب
`/adddev` - رفع مطور
`/addreply` - اضافة رد عام
`/replies` - قائمة الردود
`/setchannel` - تغير قناة التحديثات
`/help` - اظهار الاوامر
"""
    bot.send_message(m.chat.id, welcome_text + "\n" + help_text, parse_mode="Markdown")

@bot.message_handler(commands=['settings'], chat_types=['private'])
def cmd_settings(m):
    if not is_main_dev(m.from_user.id): return
    g = len(get_groups())
    ch = get_setting('channel')
    bot.send_message(m.chat.id, f"⚙️ اسم البوت: {bot_name}\nالقروبات: {g}\nالمطورين: {len(get_devs())}\nقناة التحديثات: {ch}\nالحالة: {'شغال' if bot_status else 'متوقف'}")

@bot.message_handler(commands=['broadcast'], chat_types=['private'])
def cmd_broadcast(m):
    if not is_main_dev(m.from_user.id): return
    bot.send_message(m.chat.id, "📢 اوامر الاذاعة:\n`ذيع + النص` = اذاعة نص\nارسل صورة + `ذيع` = اذاعة صورة\nسوي توجيه + `ذيع` = اذاعة توجيه", parse_mode="Markdown")

@bot.message_handler(commands=['gbanned'], chat_types=['private'])
def cmd_gbanned(m):
    if not is_main_dev(m.from_user.id): return
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT COUNT(*) FROM gbanned"); r=c.fetchone()[0]; c.connection.close()
    bot.send_message(m.chat.id, f"📊 المحظورين عام: {r}")

@bot.message_handler(commands=['setowner'], chat_types=['private'])
def cmd_setowner(m):
    if not is_main_dev(m.from_user.id): return
    waiting[m.from_user.id] = "change_owner"
    bot.send_message(m.chat.id, "ارسل ايدي المطور الجديد")

@bot.message_handler(commands=['deldevs'], chat_types=['private'])
def cmd_deldevs(m):
    if not is_main_dev(m.from_user.id): return
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("DELETE FROM devs"); c.connection.commit(); c.connection.close()
    bot.send_message(m.chat.id, "✅ تم مسح جميع المطورين الثانويين")

@bot.message_handler(commands=['setname'], chat_types=['private'])
def cmd_setname(m):
    if not is_main_dev(m.from_user.id): return
    waiting[m.from_user.id] = "change_name"
    bot.send_message(m.chat.id, "ارسل الاسم الجديد")

@bot.message_handler(commands=['delname'], chat_types=['private'])
def cmd_delname(m):
    if not is_main_dev(m.from_user.id): return
    global bot_name; bot_name = "𝐓𝐢𝐚"
    bot.send_message(m.chat.id, "✅ تم ارجاع اسم البوت الى 𝐓𝐢𝐚")

@bot.message_handler(commands=['delgbanned'], chat_types=['private'])
def cmd_delgbanned(m):
    if not is_main_dev(m.from_user.id): return
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("DELETE FROM gbanned"); c.connection.commit(); c.connection.close()
    bot.send_message(m.chat.id, "✅ تم مسح قائمة الحظر العام")

@bot.message_handler(commands=['contactoff'], chat_types=['private'])
def cmd_contactoff(m):
    if not is_main_dev(m.from_user.id): return
    global contact_status; contact_status = False
    bot.send_message(m.chat.id, "📵 تم تعطيل التواصل")

@bot.message_handler(commands=['contacton'], chat_types=['private'])
def cmd_contacton(m):
    if not is_main_dev(m.from_user.id): return
    global contact_status; contact_status = True
    bot.send_message(m.chat.id, "✅ تم تفعيل التواصل")

@bot.message_handler(commands=['backup'], chat_types=['private'])
def cmd_backup(m):
    if not is_main_dev(m.from_user.id): return
    bot.send_document(m.chat.id, open(DB_FILE, 'rb'), caption="💾 النسخة الاحتياطية")

@bot.message_handler(commands=['restart'], chat_types=['private'])
def cmd_restart(m):
    if not is_main_dev(m.from_user.id): return
    bot.send_message(m.chat.id, "🔄 جاري التحديث..."); time.sleep(1); bot.send_message(m.chat.id, "✅ تم تحديث الملفات")

@bot.message_handler(commands=['botstop'], chat_types=['private'])
def cmd_botstop(m):
    if not is_main_dev(m.from_user.id): return
    global bot_status; bot_status = False
    bot.send_message(m.chat.id, "🔴 تم تعطيل البوت الخدمي")

@bot.message_handler(commands=['botstart'], chat_types=['private'])
def cmd_botstart(m):
    if not is_main_dev(m.from_user.id): return
    global bot_status; bot_status = True
    bot.send_message(m.chat.id, "⚡ تم تفعيل البوت الخدمي")

@bot.message_handler(commands=['addwelcome'], chat_types=['private'])
def cmd_addwelcome(m):
    if not is_main_dev(m.from_user.id): return
    waiting[m.from_user.id] = "add_welcome"
    bot.send_message(m.chat.id, "ارسل نص الترحيب الجديد\nتقدر تستخدم: {name} للاسم")

@bot.message_handler(commands=['adddev'], chat_types=['private'])
def cmd_adddev(m):
    if not is_main_dev(m.from_user.id): return
    waiting[m.from_user.id] = "add_dev"
    bot.send_message(m.chat.id, "ارسل ايدي المطور الثانوي")

@bot.message_handler(commands=['addreply'], chat_types=['private'])
def cmd_addreply(m):
    if not is_main_dev(m.from_user.id): return
    waiting[m.from_user.id] = "add_g_reply"
    bot.send_message(m.chat.id, "ارسل: الكلمة - الرد")

@bot.message_handler(commands=['replies'], chat_types=['private'])
def cmd_replies(m):
    if not is_main_dev(m.from_user.id): return
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT word FROM g_reply"); r=c.fetchall(); c.connection.close()
    if not r: bot.send_message(m.chat.id, "📜 لا توجد ردود عامة")
    else:
        text = "📜 **الردود العامة:**\n" + "\n".join([f"- `{x[0]}`" for x in r])
        bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['setchannel'], chat_types=['private'])
def cmd_setchannel(m):
    if not is_main_dev(m.from_user.id): return
    waiting[m.from_user.id] = "change_channel"
    current = get_setting('channel')
    bot.send_message(m.chat.id, f"📢 القناة الحالية: {current}\nارسل يوزر القناة الجديد مع @")

@bot.message_handler(commands=['help'], chat_types=['private'])
def cmd_help(m):
    if not is_main_dev(m.from_user.id): return
    bot.send_message(m.chat.id, "اكتب /start لعرض كل الاوامر")

@bot.message_handler(func=lambda m: m.from_user.id in waiting, chat_types=['private'])
def wait_handler(m):
    global bot_name, MAIN_DEV_ID
    act = waiting.pop(m.from_user.id)

    if act == "change_owner":
        MAIN_DEV_ID = int(m.text)
        bot.send_message(m.chat.id, f"✅ تم تغير المطور الاساسي الى {m.text}\nلازم تعمل اعادة تشغيل للبوت")

    elif act == "change_name":
        bot_name = m.text
        bot.send_message(m.chat.id, f"✅ تم تغير اسم البوت الى {m.text}")

    elif act == "change_channel":
        ch = m.text.strip()
        if not ch.startswith("@"):
            return bot.send_message(m.chat.id, "❌ لازم تبدا بـ @\nمثال: @channelname")
        set_setting('channel', ch)
        bot.send_message(m.chat.id, f"✅ تم تغير قناة التحديثات الى {ch}")

    elif act == "add_welcome":
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("DELETE FROM welcome"); c.execute("INSERT INTO welcome VALUES (?)",(m.text,)); c.connection.commit(); c.connection.close()
        bot.send_message(m.chat.id, "✅ تم حفظ الترحيب\nسيظهر عند /start")

    elif act == "add_dev":
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("INSERT OR IGNORE INTO devs VALUES (?)",(int(m.text),)); c.connection.commit(); c.connection.close()
        bot.send_message(m.chat.id, f"✅ تم رفع {m.text} كمطور ثانوي")

    elif act == "add_g_reply":
        try:
            word, reply = m.text.split(" - ", 1)
            c=sqlite3.connect(DB_FILE).cursor(); c.execute("INSERT OR REPLACE INTO g_reply VALUES (?,?)",(word, reply)); c.connection.commit(); c.connection.close()
            bot.send_message(m.chat.id, f"✅ تم اضافة رد عام\nالكلمة: {word}")
        except:
            bot.send_message(m.chat.id, "❌ الصيغة خطأ\nارسل: الكلمة - الرد")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and is_main_dev(m.from_user.id) and m.text.startswith("ذيع "))
def broadcast_text(m):
    do_broadcast(m.chat.id, ["broadcast_text", m.text.replace("ذيع ", "", 1)])

@bot.message_handler(content_types=['photo'], func=lambda m: m.chat.type == 'private' and is_main_dev(m.from_user.id) and m.caption and m.caption.startswith("ذيع"))
def broadcast_photo(m):
    do_broadcast(m.chat.id, ["broadcast_photo", m.photo[-1].file_id, m.caption.replace("ذيع", "", 1)])

@bot.message_handler(content_types=['forward'], func=lambda m: m.chat.type == 'private' and is_main_dev(m.from_user.id) and m.text and m.text.startswith("ذيع"))
def broadcast_forward(m):
    do_broadcast(m.chat.id, ["broadcast_forward", m.forward_from_message_id, m.chat.id])

def do_broadcast(chat_id, data):
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
