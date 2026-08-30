import sqlite3
import os
import sys
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

DB_NAME = "dev_data.db"
GROUPS_FILE = "groups.txt"

DEV_DATA = {
    "bot_name": "𝐓𝐢𝐚",
    "welcome": "✨ أهلاً بك في بوت 𝐓𝐢𝐚 ✨",
    "owner_id": 7488375443
}
bot_status = True

def get_dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.row(KeyboardButton("📊 قائمة العام"), KeyboardButton("📢 اذاعة"), KeyboardButton("🔄 تحديث"))
    markup.row(KeyboardButton("👤 رفع مطور"), KeyboardButton("👤 تنزيل مطور"))
    markup.row(KeyboardButton("✅ تفعيل البوت"), KeyboardButton("🔴 تعطيل البوت"), KeyboardButton("♻️ اعادة تشغيل"))
    return markup

def init_db():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS replies (chat_id INTEGER, trigger TEXT, reply TEXT, type TEXT, PRIMARY KEY(chat_id, trigger))")
    cursor.execute("CREATE TABLE IF NOT EXISTS gban (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS gmute (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS clips (name TEXT PRIMARY KEY, text TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit(); conn.close()
init_db()

MAIN_DEV = 7488375443  # غيره لايديك
DEV_PHOTO = "https://t.me/YourPhoto" # حط صورة المطور
DEV_USERNAME = "@YourUsername" # حط يوزرك
DEV_NAME = "المطور الاساسي"

def is_dev(user_id):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("SELECT user_id FROM devs WHERE user_id =?", (user_id,)); is_secondary = cursor.fetchone(); conn.close()
    return user_id == MAIN_DEV or is_secondary

def add_dev(user_id): conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("INSERT OR IGNORE INTO devs VALUES (?)", (user_id,)); conn.commit(); conn.close()
def del_dev(user_id): conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("DELETE FROM devs WHERE user_id =?", (user_id,)); conn.commit(); conn.close()
def save_group(chat_id):
    if not os.path.exists(GROUPS_FILE): open(GROUPS_FILE, 'w').close()
    with open(GROUPS_FILE, 'r') as f: groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, 'a') as f: f.write(f"{chat_id}\n")
def get_all_groups():
    if not os.path.exists(GROUPS_FILE): return []
    with open(GROUPS_FILE, 'r') as f: return [int(x) for x in f.read().splitlines()]

def register_handlers(bot):

    @bot.message_handler(commands=['المطور2'], chat_types=['group','supergroup','private'])
    def dev_menu(m):
        if not is_dev(m.from_user.id): return bot.reply_to(m, "❌ هذا الامر للمطور فقط")
        bot.reply_to(m, "- اهلا بك عزي Dev\n━━━━━━━━━━━━\n- رفع Dev - تنزيل Dev\n- حظر عام - الغاء عام\n- كتم عام - الغاء كتم عام\n- قائمه العام - مسح المحظورين عام\n- اذاعه + بالرد\n- تحديث - اعاده تشغيل\n━━━━━━━━━━━━", reply_markup=get_dev_keyboard())

    @bot.message_handler(commands=['المطور'], chat_types=['group','supergroup','private'])
    def show_dev_info(m):
        caption = f"◂ **معلومات المطور**\n━━━━━━━━━━━━\n**الاسم:** {DEV_NAME}\n**اليوزر:** {DEV_USERNAME}\n**الايدي:** `{MAIN_DEV}`\n━━━━━━━━━━━━\nللتواصل: {DEV_USERNAME}"
        try: bot.send_photo(m.chat.id, DEV_PHOTO, caption=caption, parse_mode="Markdown")
        except: bot.reply_to(m, caption, parse_mode="Markdown")

    @bot.message_handler(chat_types=['group','supergroup'])
    def save_group_id(m): save_group(m.chat.id)

    @bot.message_handler(func=lambda m: is_dev(m.from_user.id) and m.text)
    def process_dev(m):
        global bot_status
        text = m.text.strip(); user_id = m.from_user.id; chat_id = m.chat.id

        if text.startswith("رفع Dev") and m.reply_to_message: target = m.reply_to_message.from_user.id; add_dev(target); bot.reply_to(m, f"👑 تم رفع {m.reply_to_message.from_user.first_name} مطور ثانوي")
        if text.startswith("تنزيل Dev") and m.reply_to_message: target = m.reply_to_message.from_user.id; del_dev(target); bot.reply_to(m, f"🗑️ تم تنزيل {m.reply_to_message.from_user.first_name} من المطورين")
        if text == "مسح المالكين الاساسيين": conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("DELETE FROM devs"); conn.commit(); conn.close(); bot.reply_to(m, "🗑️ تم مسح كل المطورين الثانويين")

        if text.startswith("حظر عام") and m.reply_to_message: target = m.reply_to_message.from_user.id; conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("INSERT OR IGNORE INTO gban VALUES (?)", (target,)); conn.commit(); conn.close(); bot.reply_to(m, f"⛔ تم حظر {m.reply_to_message.from_user.first_name} عام")
        if text.startswith("الغاء عام") and m.reply_to_message: target = m.reply_to_message.from_user.id; conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("DELETE FROM gban WHERE user_id =?", (target,)); conn.commit(); conn.close(); bot.reply_to(m, f"✅ تم الغاء الحظر العام")
        if text == "قائمه العام": conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("SELECT user_id FROM gban"); rows = cursor.fetchall(); conn.close(); bot.reply_to(m, f"المحظورين عام: {len(rows)}")
        if text == "مسح المحظورين عام": conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("DELETE FROM gban"); conn.commit(); conn.close(); bot.reply_to(m, "🗑️ تم مسح المحظورين عام")

        if text.startswith("كتم عام") and m.reply_to_message: target = m.reply_to_message.from_user.id; conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("INSERT OR IGNORE INTO gmute VALUES (?)", (target,)); conn.commit(); conn.close(); bot.reply_to(m, f"🔇 تم كتم {m.reply_to_message.from_user.first_name} عام")
        if text.startswith("الغاء كتم عام") and m.reply_to_message: target = m.reply_to_message.from_user.id; conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("DELETE FROM gmute WHERE user_id =?", (target,)); conn.commit(); conn.close(); bot.reply_to(m, f"🔊 تم الغاء الكتم العام")
        if text == "مسح المكتومين عام": conn = sqlite3.connect(DB_NAME); cursor = conn.cursor(); cursor.execute("DELETE FROM gmute"); conn.commit(); conn.close(); bot.reply_to(m, "🗑️ تم مسح المكتومين عام")

        if text == "✅ تفعيل البوت": bot_status = True; bot.reply_to(m, "✅ تم تفعيل البوت")
        if text == "🔴 تعطيل البوت": bot_status = False; bot.reply_to(m, "🔴 تم تعطيل البوت")
        if text == "📊 قائمة العام":
            groups = get_all_groups(); bot.reply_to(m, f"📊 عدد القروبات: {len(groups)}")

        if text == "📢 اذاعة" or text == "اذاعه": bot.reply_to(m, "📢 ارسل الرسالة اللي تريد تذيعها بالرد")
        if text.startswith("ذيع") and m.reply_to_message:
            groups = get_all_groups(); count = 0
            for g in groups:
                try: bot.forward_message(g, m.chat.id, m.reply_to_message.message_id); count += 1
                except: pass
            bot.reply_to(m, f"📢 تمت الاذاعة لـ {count} قروب")

        if "غادر" in text: bot.reply_to(m, "👋 تم المغادرة"); bot.leave_chat(chat_id)
        if text == "تحديث": bot.reply_to(m, "🔄 جاري التحديث..."); os.system("git pull")
        if text == "اعاده تشغيل" or text == "♻️ اعادة تشغيل": bot.reply_to(m, "♻️ جاري اعادة التشغيل..."); os.execv(sys.executable, ['python'] + sys.argv)

    @bot.message_handler(func=lambda m: True, chat_types=['group','supergroup'])
    def dev_auto_reply(m):
        if not m.text: return
        dev_names = ["المطور", "المبرمج", "dev", "الادمن الاساسي", DEV_USERNAME.lower()]
        if any(name in m.text.lower() for name in dev_names):
            replies = [f"نعم؟ المطور {DEV_USERNAME} موجود 😎", f"تحتاج المطور؟ كلمه على {DEV_USERNAME}"]
            bot.reply_to(m, random.choice(replies))
