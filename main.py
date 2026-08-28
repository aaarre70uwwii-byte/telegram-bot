import os
import time
import random
import sqlite3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ========================================================================
# 1. تهيئة وقراءة متغيرات بيئة Railway
# ========================================================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not BOT_TOKEN or not OWNER_ID:
    raise ValueError("⚠️ خطأ حرجي: المتغيرات BOT_TOKEN أو OWNER_ID مفقودة في Railway!")

bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "bot_database.db"
WHISPERS = {}
DEV_CONTACT_ON = True
BOT_SERVICE_ON = True
BOT_NAME = "𝐓𝐢α Bot"

# ========================================================================
# 2. قاعدة البيانات
# ========================================================================
def init_db():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS group_settings (chat_id TEXT PRIMARY KEY, link TEXT, rules TEXT, welcome TEXT, download_enabled INTEGER DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS global_restrictions (user_id TEXT PRIMARY KEY, type TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS group_roles (chat_id TEXT, user_id TEXT, role_name TEXT, PRIMARY KEY (chat_id, user_id))")
    c.execute("CREATE TABLE IF NOT EXISTS chat_locks (chat_id TEXT, lock_name TEXT, is_locked INTEGER, PRIMARY KEY (chat_id, lock_name))")
    c.execute("CREATE TABLE IF NOT EXISTS secondary_devs (user_id TEXT PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS welcome_msg (text TEXT)")
    c.execute("INSERT OR IGNORE INTO welcome_msg VALUES (?)", (f"🙋‍♂️ أهلاً بك عزي في بوت {BOT_NAME}",))
    conn.commit(); conn.close()

init_db()

def set_lock_status(chat_id, lock_name, is_locked):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO chat_locks VALUES (?,?,?)", (str(chat_id), lock_name, 1 if is_locked else 0))
    conn.commit(); conn.close()

def get_lock_status(chat_id, lock_name):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT is_locked FROM chat_locks WHERE chat_id=? AND lock_name=?", (str(chat_id), lock_name))
    res = c.fetchone(); conn.close()
    return res[0] == 1 if res else False

def is_secondary_dev(user_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT user_id FROM secondary_devs WHERE user_id=?", (str(user_id),))
    res = c.fetchone(); conn.close()
    return res is not None

def is_main_dev(user_id): return str(user_id) == str(OWNER_ID)
def is_dev(user_id): return is_main_dev(user_id) or is_secondary_dev(user_id)

def is_user_admin(chat_id, user_id):
    if is_dev(user_id): return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except: return False

# ========================================================================
# 3. نصوص الصفحات
# ========================================================================
MAIN_MENU_TEXT = """- ‌‌‏أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه
◂ م7 : اوامر الهمسات والميديا
━━━━━━━━━━━━"""

PAGES_TEXT = {
    "1": "• أهلاً بك عزي في قائمة اوامر الادمنيه\n━━━━━━━━━━━━\n• رفع - تنزيل مالك | رفع - تنزيل مشرف | حظر | طرد | كتم | تقييد\n• مسح الكل | مسح المحظورين | مسح المكتومين",
    "2": "- اهلا بك في قائمة اوامر الاعدادات :\n━━━━━━━━━━━━\n• الرابط | القوانين | معلوماتي | الاعدادت\n• وضع الترحيب | وضع قوانين | ضـع رابط",
    "3": "- اهلا بك في قائمة القفل - التعطيل :\n━━━━━━━━━━━━\n• قفل - فتح الروابط | قفل - فتح الصور | قفل - فتح الفيديو\n• قفل - فتح الملصقات | قفل - فتح الكل",
    "4": "• اهلا بك عزيزي في قائمة اوامر التسليه :\n━━━━━━━━━━━━\n• رفع - تنزيل هطف | رفع - تنزيل كلب | زواج | طلاق",
    "5": "- اهلا بك عزي Dev (قائمة المطور)\n━━━━━━━━━━━━\n• رفع - تنزيل Dev | حظر - كتم عام | اذاعة\n• اضف رد عام | ترحيب البوت | تحديث",
    "6": "• أهلاً بك في القائمة الخدمية العامة (م6) :\n━━━━━━━━━━━━\n• نسبه الحب | نسبه الغباء | قوقل + كلمة | ترجم + النص\n• قران | اذكار | شعر",
    "7": "• دليل أوامر الهمسات والميديا (م7) :\n━━━━━━━━━━━━\n🔒 `همسه` بالرد على العضو\n📥 `تحويل فيديو الى صوت` بالرد"
}

# ========================================================================
# 4. الكيبوردات
# ========================================================================
def get_dev_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, placeholder="لوحة تحكم المطور الأساسي ⚙️")
    markup.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📣 أوامر الإذاعة"), KeyboardButton("📊 قائمة العام"))
    markup.row(KeyboardButton("👑 تغيير المطور الأساسي"), KeyboardButton("🔔 مسح المطورين"))
    markup.row(KeyboardButton("✏️ تغيير اسم البوت"), KeyboardButton("👥 مسح المطورين الثانويين"))
    markup.row(KeyboardButton("📴 تعطيل التواصل"), KeyboardButton("📲 تفعيل التواصل"))
    markup.row(KeyboardButton("🔄 تحديث الملفات"), KeyboardButton("👋 أضف ترحيب"), KeyboardButton("📢 قناة تحديثات البوت"))
    return markup

def create_inline_keyboard(current_page=None):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("1", callback_data="page_1"), InlineKeyboardButton("2", callback_data="page_2"), InlineKeyboardButton("3", callback_data="page_3"), InlineKeyboardButton("4", callback_data="page_4"))
    markup.row(InlineKeyboardButton("5", callback_data="page_5"), InlineKeyboardButton("6", callback_data="page_6"), InlineKeyboardButton("7", callback_data="page_7"))
    if current_page:
        try:
            current_num = int(current_page)
            prev_num = 7 if current_num == 1 else current_num - 1
            next_num = 1 if current_num == 7 else current_num + 1
            markup.row(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{prev_num}"), InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu"), InlineKeyboardButton("التالي ➡️", callback_data=f"page_{next_num}"))
        except: pass
    markup.row(InlineKeyboardButton("تحديثات 𝐓𝐢α", url="https://t.me"))
    return markup

# ========================================================================
# 5. الهاندلرات الاساسية
# ========================================================================
@bot.message_handler(commands=['start'])
def cmd_start(message):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("SELECT text FROM welcome_msg"); w = c.fetchone(); conn.close()
    welcome = w[0] if w else f"🙋‍♂️ اهلا بك في بوت {BOT_NAME}"
    if is_main_dev(message.from_user.id):
        bot.send_message(message.chat.id, welcome, reply_markup=get_dev_reply_keyboard())
    else:
        bot.send_message(message.chat.id, welcome, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("الاوامر")))

@bot.message_handler(func=lambda m: m.text in ["الاوامر", "قائمة الاوامر"] and m.chat.type in ["group", "supergroup"])
def cmd_menu_groups(message):
    bot.reply_to(message, MAIN_MENU_TEXT, reply_markup=create_inline_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id; msg_id = call.message_id # تم التصحيح
    if call.data == "main_menu":
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=MAIN_MENU_TEXT, reply_markup=create_inline_keyboard())
    elif call.data.startswith("page_"):
        page_num = call.data.split("_")[1]
        text = PAGES_TEXT.get(page_num, "الصفحة غير موجودة")
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=create_inline_keyboard(page_num))
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text in ["مطور", "المطور", "/dev"] and m.chat.type == "private")
def dev_private_keyboard(message):
    if is_main_dev(message.from_user.id):
        bot.send_message(message.chat.id, "👑 تم تفعيل لوحة تحكم المطور:", reply_markup=get_dev_reply_keyboard())

# ========================================================================
# 6. اوامر المطور
# ========================================================================
@bot.message_handler(func=lambda m: is_main_dev(m.from_user.id) and m.text == "⚙️ إعدادات البوت")
def dev_settings(m):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("SELECT COUNT(*) FROM group_settings"); groups = c.fetchone()[0]; conn.close()
    bot.reply_to(m, f"⚙️ **حالة البوت**\n🤖 الاسم: {BOT_NAME}\n👑 المطور: `{OWNER_ID}`\n📊 القروبات: {groups}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: is_main_dev(m.from_user.id) and m.text == "📣 أوامر الإذاعة")
def broadcast_cmd(m):
    msg = bot.send_message(m.chat.id, "📢 ارسل نص الاذاعة الان")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("SELECT chat_id FROM group_settings"); groups = c.fetchall(); conn.close()
    count = 0
    for g in groups:
        try: bot.send_message(g[0], f"📢 **اذاعة من المطور:**\n\n{message.text}", parse_mode="Markdown"); count += 1; time.sleep(0.1)
        except: pass
    bot.send_message(message.chat.id, f"✅ تم الاذاعة لـ {count} قروب")

@bot.message_handler(func=lambda m: is_main_dev(m.from_user.id) and m.text == "👥 مسح المطورين الثانويين")
def add_sec_dev(m):
    msg = bot.send_message(m.chat.id, "➕ ارسل ايدي المطور الثانوي")
    bot.register_next_step_handler(msg, process_add_dev)

def process_add_dev(message):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("INSERT OR IGNORE INTO secondary_devs VALUES (?)", (message.text,)); conn.commit(); conn.close()
    bot.send_message(message.chat.id, f"✅ تم رفع `{message.text}` كمطور ثانوي", parse_mode="Markdown")

# ========================================================================
# 7. نظام القفل - الفتح
# ========================================================================
@bot.message_handler(func=lambda m: m.text.startswith("قفل ") and m.chat.type in ["group", "supergroup"])
def lock_cmd(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    lock_name = message.text.replace("قفل ", "")
    mapping = {"الروابط": "links", "الصور": "photo", "الفيديو": "video", "الملصقات": "sticker", "الكتابه": "text", "الكل": "all"}
    if lock_name in mapping:
        set_lock_status(message.chat.id, mapping[lock_name], True)
        bot.reply_to(message, f"🔒 تم قفل {lock_name}")

@bot.message_handler(func=lambda m: m.text.startswith("فتح ") and m.chat.type in ["group", "supergroup"])
def unlock_cmd(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    lock_name = message.text.replace("فتح ", "")
    mapping = {"الروابط": "links", "الصور": "photo", "الفيديو": "video", "الملصقات": "sticker", "الكتابه": "text", "الكل": "all"}
    if lock_name in mapping:
        set_lock_status(message.chat.id, mapping[lock_name], False)
        bot.reply_to(message, f"🔓 تم فتح {lock_name}")

@bot.message_handler(content_types=['text', 'photo', 'video', 'sticker'])
def check_locks(message):
    if message.chat.type not in ['group', 'supergroup'] or is_user_admin(message.chat.id, message.from_user.id): return
    chat_id = message.chat.id
    if get_lock_status(chat_id, "links") and message.text and "http" in message.text: bot.delete_message(chat_id, message.message_id)
    if get_lock_status(chat_id, "photo") and message.content_type == "photo": bot.delete_message(chat_id, message.message_id)
    if get_lock_status(chat_id, "video") and message.content_type == "video": bot.delete_message(chat_id, message.message_id)
    if get_lock_status(chat_id, "sticker") and message.content_type == "sticker": bot.delete_message(chat_id, message.message_id)

# ========================================================================
# 8. حفظ القروبات
# ========================================================================
@bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'])
def save_group(m):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO group_settings (chat_id) VALUES (?)", (str(m.chat.id),))
    conn.commit(); conn.close()

# ========================================================================
# 9. التشغيل
# ========================================================================
if __name__ == "__main__":
    print(f"البوت {BOT_NAME} شغال")
    print(f"OWNER_ID: {OWNER_ID}")
    bot.infinity_polling(skip_pending=True)
