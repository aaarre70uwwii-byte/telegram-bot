import os
import sqlite3
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAIN_DEV_ID = int(os.getenv("OWNER_ID"))
bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "bot_database.db"
waiting = {}

def init_db():
    c = sqlite3.connect(DB_FILE).cursor()
    c.execute("CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS activated (chat_id INTEGER PRIMARY KEY)")
    c.connection.commit(); c.connection.close()
init_db()

def is_main_dev(u): return u == MAIN_DEV_ID
def is_dev(u):
    c=sqlite3.connect(DB_FILE).cursor(); c.execute("SELECT user_id FROM devs"); r=[x[0] for x in c.fetchall()]; c.connection.close()
    return u == MAIN_DEV_ID or u in r

def is_admin_or_dev(chat_id, user_id):
    if is_dev(user_id): return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except: return False

# === 1. كيبورد المطور للخاص = يطلع مكان الكتابة ===
def kb_private():
    k = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    k.add(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📢 أوامر الإذاعة"), KeyboardButton("📊 قائمة العام"))
    k.add(KeyboardButton("👑 تغير المطور الاساسي"), KeyboardButton("🧹 مسح المطورين"))
    k.add(KeyboardButton("➕ رفع Dev"), KeyboardButton("➖ تنزيل Dev"))
    k.add(KeyboardButton("🔴 تعطيل البوت الخدمي"), KeyboardButton("⚡ تفعيل البوت"))
    k.add(KeyboardButton("🗑️ اخفاء الكيبورد"))
    return k

# === 2. كيبورد المطور للقروبات = يطلع مكان الكتابة ===
def kb_dev_group():
    k = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    k.add(KeyboardButton("اهلا بك عزيزي Dev"))
    k.add(KeyboardButton("اضف رد تواصل"), KeyboardButton("حذف رد تواصل"))
    k.add(KeyboardButton("رفع Dev"), KeyboardButton("تنزيل Dev"))
    k.add(KeyboardButton("ذيع + ايدي المجموعه"), KeyboardButton("حظر - كتم عام"))
    k.add(KeyboardButton("تحديث"), KeyboardButton("اعاده تشغيل - reload"))
    k.add(KeyboardButton("🗑️ اخفاء الكيبورد"))
    return k

# === الخاص ===
@bot.message_handler(commands=['start'], chat_types=['private'])
def start_private(m):
    if not is_main_dev(m.from_user.id):
        return bot.reply_to(m, "❌ للمطور الاساسي فقط")
    bot.send_message(m.chat.id, "🙋‍♂️ اهلا بك عزي Dev\n🛠️ لوحة التحكم:", reply_markup=kb_private())

# === القروبات ===
@bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'])
def group(m):
    t=m.text; uid=m.from_user.id; cid=m.chat.id
    if not t: return

    # تفعيل للادمن
    if t == "تفعيل":
        if not is_admin_or_dev(cid, uid): return
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("INSERT OR IGNORE INTO activated VALUES (?)",(cid,)); c.connection.commit(); c.connection.close()
        return bot.reply_to(m, "🟢 تم تفعيل البوت")

    # امر اظهار الكيبورد للمطور فقط
    if t == "كيبورد المطور":
        if not is_main_dev(uid): return
        return bot.send_message(cid, "🛠️ تم تفعيل كيبورد المطور", reply_markup=kb_dev_group())

    if not is_main_dev(uid): return

    # اوامر الكيبورد
    if t == "اهلا بك عزي Dev": bot.reply_to(m, "نورت يا مطور ❤️")
    elif t == "رفع Dev": waiting[uid] = "add_dev"; bot.reply_to(m, "ارسل ايدي المطور")
    elif t == "تنزيل Dev": waiting[uid] = "del_dev"; bot.reply_to(m, "ارسل ايدي المطور")
    elif t == "ذيع + ايدي المجموعه": waiting[uid] = "broadcast"; bot.reply_to(m, "ارسل: الايدي - الرسالة")
    elif t == "🗑️ اخفاء الكيبورد": bot.send_message(cid, "تم اخفاء الكيبورد", reply_markup=ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: m.from_user.id in waiting)
def wait_handler(m):
    act = waiting.pop(m.from_user.id)
    if act == "add_dev":
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("INSERT OR IGNORE INTO devs VALUES (?)",(int(m.text),)); c.connection.commit(); c.connection.close()
        bot.send_message(m.chat.id, f"✅ تم رفع {m.text}")
    elif act == "del_dev":
        c=sqlite3.connect(DB_FILE).cursor(); c.execute("DELETE FROM devs WHERE user_id=?",(int(m.text),)); c.connection.commit(); c.connection.close()
        bot.send_message(m.chat.id, f"❌ تم تنزيل {m.text}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
