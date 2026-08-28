import os
import time
import random
import sqlite3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ========================================================================
# 1. تهيئة وقراءة متغيرات بيئة Railway البيئية
# ========================================================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not BOT_TOKEN or not OWNER_ID:
    raise ValueError("⚠️ خطأ حرجي: المتغيرات الأساسية BOT_TOKEN أو OWNER_ID مفقودة في إعدادات Railway!")

# إنشاء البوت مع معالج استثنائيات لامتصاص الأخطاء الداخلية ومنع التحطم كلياً
bot = telebot.TeleBot(BOT_TOKEN, exception_handler=telebot.ExceptionHandler())

# ========================================================================
# 2. إنشاء وتجهيز قاعدة البيانات الثابتة (SQLite)
# ========================================================================
DB_FILE = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_settings (
        chat_id TEXT PRIMARY KEY, link TEXT, rules TEXT, welcome TEXT, download_enabled INTEGER
    )""")
    cursor.execute("CREATE TABLE IF NOT EXISTS global_restrictions (user_id TEXT PRIMARY KEY, type TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS group_roles (chat_id TEXT, user_id TEXT, role_name TEXT, PRIMARY KEY (chat_id, user_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS chat_locks (chat_id TEXT, lock_name TEXT, is_locked INTEGER, PRIMARY KEY (chat_id, lock_name))")
    conn.commit()
    conn.close()

init_db()

# دالات مساعدة لإدارة وإدخال الحالات تلقائياً في قاعدة البيانات
def set_lock_status(chat_id, lock_name, is_locked):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO chat_locks VALUES (?, ?, ?)", (str(chat_id), lock_name, 1 if is_locked else 0))
    conn.commit()
    conn.close()

def get_lock_status(chat_id, lock_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT is_locked FROM chat_locks WHERE chat_id=? AND lock_name=?", (str(chat_id), lock_name))
    res = cursor.fetchone()
    conn.close()
    return res[0] == 1 if res else False

def check_global_restriction(user_id, r_type):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT type FROM global_restrictions WHERE user_id=?", (str(user_id),))
    res = cursor.fetchone()
    conn.close()
    return res[0] == r_type if res else False

# مخزن الهمسات المؤقت في الذاكرة السريعة
WHISPERS = {}

# ========================================================================
# 3. نصوص الصفحات والأقسام الكاملة من 1 إلى 7
# ========================================================================
MAIN_MENU_TEXT = """- ‌‌‏أهلاً بك عزيزي في قائمة الاوامر :
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
    "1": """• أهلاً بك عزيزي في قائمة اوامر الادمنيه
━━━━━━━━━━━━ 
- اوامر الرفع والتنزيل :
• رفع - تنزيل مالك اساسي | • رفع - تنزيل مالك
• رفع - تنزيل مشرف | • رفع - تنزيل منشئ
• رفع - تنزيل مدير | • رفع - تنزيل ادمن
• رفع - تنزيل مميز | • تنزيل الكل

- اوامر المسح :
• مسح الكل | • مسح المنشئين | • مسح المدراء
• مسح المالكين | • مسح الادمنيه | • مسح المميزين
• مسح المحظورين | • مسح المكتومين | • مسح قائمه المنع
• مسح الردود | • مسح + عدد | • مسح بالرد

- اوامر الطرد والحظر :
• تقييد + الوقت | • حظر | • طرد | • كتم
• الغاء الحظر | • الغاء الكتم | • فك التقييد | • طرد البوتات
━━━━━━━━━━━━""",
    "2": """- اهلا بك في قائمة اوامر الاعدادات :
━━━━━━━━━━━━ 
• الرابط | • المالكين | • المنشئين | • الادمنيه | • المدراء
• القوانين | • معلوماتي | • الحمايه | • الاعدادت | • المجموعه
- اوامر وضع الاعدادات :
• وضع الترحيب | • وضع قوانين | • ضـع رابط | • انشاء رابط
- اوامر التحميل :
• تفعيل - تعطيل التحميل | • بحث + الاسم | • تيك + الرابط | • ساوند + الرابط
━━━━━━━━━━━━""",
    "3": """- اهلا بك في قائمة القفل - التعطيل :
━━━━━━━━━━━━ 
• قفل - فتح جمثون | • قفل - فتح السب | • قفل - فتح الكتابه
• قفل - فتح الفيديو | • قفل - فتح الصور | • قفل - فتح الملصقات 
• قفل - فتح الروابط | • قفل - فتح التاك | • قفل - فتح البوتات 
• قفل البوتات بالطرد | •️ قفل - فتح التكرار | • قفل - فتح التوجيه 
• قفل - فتح الكل | • قفل - فتح الروابط بالتقييد
- اوامر التفعيل - التعطيل :
• تفعيل - تعطيل الاذكار | • تفعيل - تعطيل التسليه 
• تفعيل - تعطيل الترحيب | • تفعيل - تعطيل الردود
━━━━━━━━━━━━""",
    "4": """• اهلا بك عزيزي في قائمة اوامر التسليه :
━━━━━━━━━━━━
- رتب تسلية تظهر بالايدي :
• رفع - تنزيل (هطف، بثر، حمار، كلب، عتوي، لحجي، خروف، خفيف)
• رفع بقلبي : تنزيل من قلبي
- رتب المجموعه والعام :
• رفع + اسم اختياري | • مسح رتب التسليه | • رتب التسليه
• رفع عام + اسم اختياري | • رتب التسليه عام
- أنظمة تفاعلية :
• طلاق - زواج | • زوجي - زوجتي | • تتزوجني
• اكتموه (تصويت كتم ديمقراطي)
━━━━━━━━━━━━""",
    "5": """- اهلا بك عزيزي Dev (قائمة المطور)
━━━━━━━━━━━━
• اضف رد تواصل | • ترحيب البوت | • ردود التواصل
• اسم بوتك + غادر | • تعطيل - تفعيل الزاجل
• رفع - تنزيل Dev = مطور ثانوي
• فتح - قفل الاحصائيات | • فتح - قفل حظر العام
• حظر - كتم عام | • قائمه العام | • الغاء عام
• مسح المحظورين عام | • مسح المكتومين عام
• اضف رد عام | • مسح الردود العامه 
• تحديث | • اعاده تشغيل - reload
━━━━━━━━━━━━""",
    "6": """• أهلاً بك في القائمة الخدمية العامة (م6) :
━━━━━━━━━━━━
• نسبه الحب | • نسبه الغباء | • تحبه | • شرايك في افتاري
• صيح | • صيح + اليوزر | • شبيهي | • افتاره بالرد | • البايو بالرد
• قوقل + كلمة البحث | • تطبيق + الاسم | • تحميل لعبه + الاسم
• معنى + اسمك | • العمر + عمرك | • زخرف + اسمك | • ترجم + النص
• قران | • اذكار | • شعر ، قصائد | • اقتباسات | • ثريد | • ميمز
━━━━━━━━━━━━""",
    "7": """• دليل أوامر الهمسات والميديا المتقدمة (م7) :
━━━━━━━━━━━━
🔒 **نظام الهمسات السرية الفوري:**
• `همسه` أو `همسة` : بالرد على العضو لكتابة همسة سرية له.
• `همسه` + [النص] + [@يوزر_العضو] : لإرسال همسة مباشرة دون رد.

📥 **أدوات تحويل الصيغ بالرد على الميديا:**
• تحويل فيديو إلى صوت (بصمة).
• تحويل ميديا إلى متحركة (Gif).
━━━━━━━━━━━━"""
}

# ========================================================================
# 4. دالات لوحات المفاتيح (Keyboards)
# ========================================================================

def get_dev_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, placeholder="لوحة تحكم المطور الأساسي ⚙️")
    markup.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📣 أوامر الإذاعة"), KeyboardButton("📊 قائمة العام"))
    markup.row(KeyboardButton("👑 تغيير المطور الأساسي"), KeyboardButton("🔔 مسح المطورين"))
    markup.row(KeyboardButton("🗑️ مسح اسم البوت"), KeyboardButton("❌ مسح قائمة العام"))
    markup.row(KeyboardButton("✏️ تغيير اسم البوت"), KeyboardButton("👥 مسح المطورين الثانويين"))
    markup.row(KeyboardButton("📴 تعطيل التواصل"), KeyboardButton("📦 جلب النسخة الاحتياطية"))
    markup.row(KeyboardButton("📲 تفعيل التواصل"), KeyboardButton("🔄 تحديث الملفات"))
    markup.row(KeyboardButton("🔴 تعطيل البوت الخدمي"), KeyboardButton("⚡ تفعيل البوت"))
    markup.row(KeyboardButton("▶️ تفعيل البوت الخدمي"), KeyboardButton("👋 أضف ترحيب"), KeyboardButton("📢 قناة تحديثات البوت"))
    return markup

def create_inline_keyboard(current_page=None):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("1", callback_data="page_1")
    btn2 = InlineKeyboardButton("2", callback_data="page_2")
    btn3 = InlineKeyboardButton("3", callback_data="page_3")
    btn4 = InlineKeyboardButton("4", callback_data="page_4")
    btn5 = InlineKeyboardButton("5", callback_data="page_5")
    btn6 = InlineKeyboardButton("6", callback_data="page_6")
    btn7 = InlineKeyboardButton("7", callback_data="page_7")
    
    markup.row(btn1, btn2, btn3, btn4)
    markup.row(btn5, btn6, btn7)
    
    if current_page:
        try:
            current_num = int(current_page)
            prev_num = 7 if current_num == 1 else current_num - 1
            next_num = 1 if current_num == 7 else current_num + 1
            markup.row(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{prev_num}"), InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu"), InlineKeyboardButton("التالي ➡️", callback_data=f"page_{next_num}"))
        except ValueError: pass
            
    markup.row(InlineKeyboardButton("تحديثات 𝐓𝐢α", url="https://t.me"))
    return markup

# ========================================================================
# 5. معالجة وتدقيق صلاحيات الإشراف والتحكم
# ========================================================================

def is_user_admin(chat_id, user_id):
    try:
        if str(user_id) == str(OWNER_ID) or check_global_restriction(user_id, "secondary_dev"):
            return True
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception: return False

# أ) المجموعات والقنوات
@bot.message_handler(func=lambda message: message.text in ["الاوامر", "قائمة الاوامر"] and message.chat.type in ["group", "supergroup"])
def cmd_menu_groups(message):
    bot.reply_to(message, MAIN_MENU_TEXT, reply_markup=create_inline_keyboard(), parse_mode="Markdown")

@bot.channel_post_handler(func=lambda message: message.text in ["الاوامر", "قائمة الاوامر"])
def cmd_menu_channels(message):
    bot.send_message(message.chat.id, MAIN_MENU_TEXT, reply_markup=create_inline_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text in ["تفعيل", "تفعيل الاوامر"] and message.chat.type in ["group", "supergroup"])
def activate_system(message):
    bot.reply_to(message, "⚙️ تم تفعيل البوت وتشغيل أنظمة المجموعات بنجاح! أرسل الآن كلمة `الاوامر` لفتح اللوحة الشفافة.", parse_mode="Markdown")

