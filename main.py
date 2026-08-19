import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import random
import re
import os # 1. ضفنا os عشان نقرا من المتغيرات

# ==========================================
# ⚙️ قسم المتغيرات والإعدادات (تعديل هنا بسهولة)
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN") # 2. صار يقرا من Railway تلقائي
CHANNEL_URL = "https://t.me" # رابط قناة التحديثات الخاص بك

MAIN_MENU_TEXT = """↤اهلا فيك بعد عمري في قائمه اوامر : ✓ 𝐓𝐢𝐚 :
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه
━━━━━━━━━━━━
                  1. 2. 3.
                  4. 5. 6"""

M1_TEXT = """↢ أهلاً فيك يا حلو ♡
• قائمة اوامر الادمنيه

⚙️ اوامر الرفع والتنزيل:
• رفع - تنزيل مالك اساسي
↢ رفع - تنزيل مالك
↢ رفع - تنزيل مشرف
↢ رفع - تنزيل منشئ
↢ رفع - تنزيل مدير
↢ رفع - تنزيل ادمن
↢ رفع - تنزيل مميز
↢ تنزيل الكل - لازاله جميع الرتب اعلاه

🗑️ اوامر المسح :
• مسح + عدد
↢ مسح بالرد
↢ مسح الايدي
↢ مسح الكل
↢ مسح المنشئين
↢ مسح المدراء
↢ مسح المالكين
↢ مسح الادمنيه

🚫 اوامر الطرد والحظر :
↢ تقييد + الوقت
↢ حظر
↢ طرد
↢ كتم
↢ تقييد
↢ الغاء الحظر
↢ الغاء الكتم
↢ فك التقييد
↢ رفع القيود"""

M2_TEXT = """حياك الله في قائمة الاعدادات :
• اكتب في قروبك كذا ↓
↢ الرابط
↢ المالكين
↢ المالكين الاساسين
↢ المنشئين
↢ الادمنيه
↢ المدراء
↢ المميزين
↢ المحظورين
↢ القوانين
↢ المكتومين
↢ معلوماتي
↢ الحمايه
↢ الاعدادت
↢ المجموعه

⚙️ اوامر وضع الاعدادات :
↢ مسح الرابط
↢ انشاء رابط
↢ ضع الترحيب
↢ ضـع رابط
↢ اضف امر
↢ تعيين الايدي"""

M3_TEXT = """- حياك في قائمة القفل - التعطيل :

🔒 اولا : اوامر القفل والفتح :
↢ قفل - فتح جمثون | السب | الكتابه | التعديل | الفيديو | الصور | الملصقات | المتحركه
↢ قفل - فتح الدردشه | الروابط | التاك | البوتات | المعرفات | التكرار | التوجيه | الانلاين | الجهات | الصوت | الكل

⚙️ ثانيا : اوامر التفعيل - التعطيل :
↢ تفعيل - تعطيل ضافني | الاذكار | الثنائي | افتاري | التسليه | الكت | الترحيب | الردود | الانذار | التحذير | الايدي | الحمايه"""

M4_TEXT = """اهلا بك عزي
- اوامر التسليه :
━━━━━━━━━━━━
🎯 اوامر تسلية تظهر بالايدي :
• رفع - تنزيل : حمار : الحمير
• رفع بقلبي : تنزيل من قلبي

👥 للجروب:
• رفع + اسم اختياري
• مسح رتب التسليه | رتب التسليه | تعطيل التسليه
━━━━━━━━━━━━
🌍 للعام:
• رفع عام + اسم اختياري | رتب التسليه عام | مسح رتب التسليه
━━━━━━━━━━━━
💍 أوامر أخرى:
• طلاق - زواج | زوجي - زوجتي | تتزوجني
• اكتموه (تصويت)
• تعطيل - تفعيل : اكتموه | زوجني"""

M5_TEXT = """- اهلا بك عزي Dev
• اضف رد تواصل | حذف رد تواصل | ردود التواصل
• ترحيب البوت | مسح صوره الترحيب | تعطيل | اسم بوتك + غادر
• تعطيل - تفعيل الزاجل | مسح المالكين الاساسيين | ذيع + ايدي المجموعه - بالرد
• فتح - قفل ردود MY | رفع - تنزيل Dev | فتح - قفل الاحصائيات / حظر العام
• حظر - كتم عام | قائمه العام | الردود العامه | اضف رد عام | تحديث | reload"""

M6_TEXT = """• اهلا بك عزي
- اوامر الخدميه :
━━━━━━━━━━━━
📊 ألعاب ونسب تفاعلية:
• نسبه الحب | نسبه الغباء - بالرد | تحبه - بالرد | نسبه انوثتها | نسبه رجولته | شبيهي - شبيهتي

🔍 البحث والخدمات:
• قوقل + كلام البحث | معنى + اسمك | العمر + عمرك | زخرف + اسمك | ترجم عربي / انقليزي + الكلام
• قران | اذكار | شعر ، قصائد | اقتباسات | ثريد | قصص ، كتب | اطربني | اغاني | ميمز

📥 التحميل وتحويل الصيغ:
• ساوند + الرابط | تيك + الرابط | تويتر + الرابط | تحويل الصيغ"""

TEXT_HIDE_BUTTON = "❌ اخفاء الاوامر"
TEXT_UPDATES_BUTTON = "📢 تحديثات 𝐓𝐢𝐚"
TEXT_BACK_BUTTON = "⬅️ عودة للقائمة الرئيسية"
NOTIFICATION_HIDE = "تم إخفاء القائمة"

# ==========================================
# 🎛️ قسم البناء وقاعدة البيانات والوظائف التنفيذية
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

def init_db():
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS roles (chat_id INTEGER, user_id INTEGER, role TEXT, PRIMARY KEY (chat_id, user_id))") # 3. فصلناه بسطر
    cursor.execute("CREATE TABLE IF NOT EXISTS locks (chat_id INTEGER, lock_type TEXT, status INTEGER, PRIMARY KEY (chat_id, lock_type))")
    cursor.execute("CREATE TABLE IF NOT EXISTS custom_replies (chat_id INTEGER, keyword TEXT, reply TEXT, PRIMARY KEY (chat_id, keyword))")
    cursor.execute("CREATE TABLE IF NOT EXISTS fun_roles (chat_id INTEGER, user_id INTEGER, fun_role TEXT, PRIMARY KEY (chat_id, user_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY, link TEXT, rules TEXT, welcome TEXT, description TEXT)") # 4. ضفنا جدول groups
    conn.commit()
    conn.close()

init_db()

def db_execute(query, params=(), fetch=False, fetchone=False):
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    res = None
    if fetch:
        res = cursor.fetchone() if fetchone else cursor.fetchall()
    else:
        conn.commit()
    conn.close()
    return res

def is_user_admin(chat_id, user_id):
    if chat_id == user_id: return True
    try:
        return bot.get_chat_member(chat_id, user_id).status in ['creator', 'administrator']
    except Exception: return False

def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    row1 = [InlineKeyboardButton("1️⃣", callback_data="cmd_1"), InlineKeyboardButton("2️⃣", callback_data="cmd_2"), InlineKeyboardButton("3️⃣", callback_data="cmd_3")]
    row2 = [InlineKeyboardButton("4️⃣", callback_data="cmd_4"), InlineKeyboardButton("5️⃣", callback_data="cmd_5"), InlineKeyboardButton("6️⃣", callback_data="cmd_6")]
    markup.row(*row1)
    markup.row(*row2)
    markup.row(InlineKeyboardButton(TEXT_HIDE_BUTTON, callback_data="hide_menu"))
    markup.row(InlineKeyboardButton(TEXT_UPDATES_BUTTON, url=CHANNEL_URL))
    return markup

def sub_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(TEXT_BACK_BUTTON, callback_data="back_to_main"))
    markup.row(InlineKeyboardButton(TEXT_UPDATES_BUTTON, url=CHANNEL_URL))
    return markup

@bot.message_handler(commands=['start', 'help', 'menu'])
@bot.message_handler(func=lambda msg: msg.text == "الاوامر")
def send_menu(message):
    bot.send_message(message.chat.id, MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text in ["ايدي", "الايدي", "معلوماتي", "المجموعه", "الاعدادت"] if msg.text else False)
def get_info(message):
    user = message.from_user
    cm = bot.get_chat_member(message.chat.id, user.id)
    role = "المالك الأساسي 👑" if cm.status == 'creator' else ("مشرف المجموعة 🛡️" if cm.status == 'administrator' else "عضو")
    if role == "عضو":
        saved = db_execute("SELECT role FROM roles WHERE chat_id =? AND user_id =?", (message.chat.id, user.id), fetch=True, fetchone=True)
        if saved: role = saved[0]

    if message.text in ["ايدي", "الايدي", "معلوماتي"]:
        bot.reply_to(message, f"👤 معلوماتك:\n↢ اسمك: {user.first_name}\n↢ ايديك: {user.id}\n↢ رتبتك: {role}")
    elif message.text == "المجموعه" or message.text == "الاعدادت":
        bot.reply_to(message, f"📊 معلومات المجموعة:\n↢ اسم الجروب: {message.chat.title}\n↢ ايدي الجروب: {message.chat.id}\n↢ الحماية: نشطة بالذكاء وقاعدة البيانات")

@bot.message_handler(func=lambda msg: msg.text in ["حظر", "طرد", "كتم", "الغاء الحظر", "الغاء الكتم", "فك التقييد", "رفع القيود"] if msg.text else False)
def admin_action(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ يرجى الرد على رسالة العضو المستهدف.")
        return
    tid = message.reply_to_message.from_user.id
    tname = message.reply_to_message.from_user.first_name
    cmd = message.text
    try:
        if cmd == "حظر": # 5. فصلنا السطور
            bot.ban_chat_member(message.chat.id, tid)
            bot.reply_to(message, f"🚷 تم حظر {tname}.")
        elif cmd == "طرد":
            bot.ban_chat_member(message.chat.id, tid)
            bot.unban_chat_member(message.chat.id, tid)
            bot.reply_to(message, f"🏃‍♂️ تم طرد {tname}.")
        elif cmd == "كتم" or cmd == "تقييد":
            bot.restrict_chat_member(message.chat.id, tid, can_send_messages=False)
            bot.reply_to(message, f"🤫 تم كتم {tname}.")
        elif cmd in ["الغاء الحظر", "رفع القيود"]:
            bot.unban_chat_member(message.chat.id, tid)
            bot.reply_to(message, f"✅ تم فك حظر/قيود {tname}.")
        elif cmd in ["الغاء الكتم", "فك التقييد"]:
            bot.restrict_chat_member(message.chat.id, tid, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            bot.reply_to(message, f"🔊 تم إلغاء كتم {tname}.")
    except Exception:
        bot.reply_to(message, "❌ خطأ بالصلاحيات، تأكد أن البوت مشرف كامل الصلاحية.")

@bot.message_handler(func=lambda msg: msg.text.startswith(("رفع ", "تنزيل ")) if msg.text else False)
def manage_roles(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    tid = message.reply_to_message.from_user.id
    tname = message.reply_to_message.from_user.first_name
    cmd = message.text

    if "حمار" in cmd or "قلبي" in cmd:
        role_type = "حمار الجروب 🐴" if "حمار" in cmd else "في قلبي ❤️"
        if "رفع" in cmd:
            db_execute("INSERT OR REPLACE INTO fun_roles (chat_id, user_id, fun_role) VALUES (?,?,?)", (message.chat.id, tid, role_type))
            bot.reply_to(message, f"🔥 تم رفع {tname} {role_type}!")
        else:
            db_execute("DELETE FROM fun_roles WHERE chat_id =? AND user_id =?", (message.chat.id, tid))
            bot.reply_to(message, f"📉 تم تنزيل {tname} من رتبة التسلية.")
        return

    if cmd.startswith("رفع "):
        rname = cmd.replace("رفع ", "")
        db_execute("INSERT OR REPLACE INTO roles (chat_id, user_id, role) VALUES (?,?,?)", (message.chat.id, tid, rname))
        bot.reply_to(message, f"💼 تم رفع {tname} برتبة {rname}.")
    elif cmd.startswith("تنزيل "):
        db_execute("DELETE FROM roles WHERE chat_id =? AND user_id =?", (message.chat.id, tid))
        bot.reply_to(message, f"📉 تم تنزيل {tname} من الرتب.")

bot.infinity_polling()
