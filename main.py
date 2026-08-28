import os
import random
import sqlite3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# === قراءة الإعدادات من المتغيرات البرمجية ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "ضع_توكن_البوت_هنا")
MAIN_DEV_ID = int(os.getenv("MAIN_DEV_ID", 123456789))  # ضع آيدي حسابك التليجرام هنا
BOT_NAME = "سورس"  # اسم البوت الافتراضي للمغادرة

bot = telebot.TeleBot(BOT_TOKEN)

# === 🛠️ إعداد وتجهيز قاعدة بيانات SQLite3 دائمية ===
DB_FILE = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # جدول حفظ الجروبات المفعلة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activated_chats (
            chat_id INTEGER PRIMARY KEY
        )
    """)
    # جدول حفظ أرصدة بنك الأعضاء
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bank (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# استدعاء دالة بناء وإنشاء ملف قاعدة البيانات فوراً عند بدء التشغيل
init_db()

# دوال التعامل مع قاعدة البيانات بأمان كامل (تفتح وتقفل تلقائياً)
def is_chat_activated(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM activated_chats WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def activate_chat(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO activated_chats (chat_id) VALUES (?)", (chat_id,))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def deactivate_chat(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activated_chats WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

# [تم الإصلاح السطري الفوري] دالة جلب الرصيد تستخرج الرقم من الـ Tuple بأمان كامل
def get_balance(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM bank WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return int(result[0])  # استخراج العنصر الرقمي الأول من الصف
    return 0

def add_balance(user_id, amount):
    current = get_balance(user_id)
    new_balance = current + amount
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO bank (user_id, balance) VALUES (?, ?)", (user_id, new_balance))
    conn.commit()
    conn.close()
    return new_balance

# قاعدة بيانات مؤقتة للهمسات فقط
whisper_database = {}   

# قوائم ألعاب مدمجة
KAT_QUESTIONS = [
    "شخص مستحيل تنسى ملامحه؟",
    "تفضل العزلة والهدوء أو الصخب والجمعات؟",
    "شنو الشيء اللي يغير مزاجك بثواني؟",
    "لو اتيحت لك فرصة لتغيير اسمك، شنو تختار؟"
]

NAME_MEANINGS = {
    "أحمد": "من صفات الحمد، وهو الشخص كثير الحمد والشكر لله.",
    "محمد": "المحمود الخصال، المثني عليه، المشكور.",
    "فاطمة": "التي فُطمت عن الرضاعة، وتدل على النضج والستر.",
    "علي": "الشريف، المرتفع، ذو المكانة العالية."
}

# دالة فحص المطور الأساسي لحماية الأوامر
def is_main_dev(user_id):
    return user_id == MAIN_DEV_ID

# دالة التحقق مما إذا كان المستخدم أدمن أو منشئ (مالك) في المجموعة
def is_admin_or_owner(chat_id, user_id):
    if is_main_dev(user_id):
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception:
        return False

# === 1. كيبورد الخاص التفاعلي للمطور ===
def get_private_dev_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📊 قائمة العام", callback_data="dev_general_list"),
        InlineKeyboardButton("💬 ردود التواصل", callback_data="dev_contact_replies"),
        InlineKeyboardButton("🔄 تحديث البوت", callback_data="dev_update")
    )
    markup.row(
        InlineKeyboardButton("⚙️ فتح ردود MY", callback_data="dev_open_my"),
        InlineKeyboardButton("🔒 قفل ردود MY", callback_data="dev_close_my")
    )
    markup.row(
        InlineKeyboardButton("📈 فتح الإحصائيات", callback_data="dev_open_stats"),
        InlineKeyboardButton("📉 قفل الإحصائيات", callback_data="dev_close_stats")
    )
    markup.row(
        InlineKeyboardButton("🚫 مسح المحظورين عام", callback_data="dev_clear_banned"),
        InlineKeyboardButton("🔇 مسح المكتومين عام", callback_data="dev_clear_muted")
    )
    markup.row(
        InlineKeyboardButton("👑 مسح المالكين الأساسيين", callback_data="dev_clear_owners"),
        InlineKeyboardButton("🖼️ مسح صورة الترحيب", callback_data="dev_clear_welcome_pic")
    )
    markup.row(
        InlineKeyboardButton("♻️ إعادة تشغيل - Reload", callback_data="dev_reload")
    )
    return markup

# === 2. كيبورد الأرقام التفاعلي للجروبات (م1-م6) ===
def get_group_commands_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("1", callback_data="show_m1"))
    markup.row(
        InlineKeyboardButton("2", callback_data="show_m2"),
        InlineKeyboardButton("3", callback_data="show_m3"),
        InlineKeyboardButton("4", callback_data="show_m4"),
        InlineKeyboardButton("5", callback_data="show_m5"),
        InlineKeyboardButton("6", callback_data="show_m6")
    )
    return markup

# === نصوص القوائم التفاعلية لجروبات (م1 إلى م6) ===
M1_TEXT = "🔹 **قائمة اوامر الادمنيه (م1) :**\n━━━━━━━━━━━━━━━\n• رفع - تنزيل: مالك، منشئ، مدير، مشرف، ادمن\n• مسح: الكل، المحظورين، المكتومين، الردود\n• حظر | طرد | كتم | تقييد | فك التقييد"
M2_TEXT = "⚙️ **قائمة اوامر الاعدادات (م2) :**\n━━━━━━━━━━━━━━━\n• رؤية: الرابط، المالكين، القوانين، المجموعه\n• وضع: ضع الترحيب، ضع قوانين، اضف امر\n• تحميل: تفعيل/تعطيل التحميل (يوتيوب، تيك توك، ساوند)"
M3_TEXT = "🔒 **قائمة القفل والتعطيل (م3) :**\n━━━━━━━━━━━━━━━\n• قفل/فتح: الكتابه، الروابط، الصور، البوتات، التكرار\n• تفعيل/تعطيل: الاذكار، التسليه، الردود، الايدي بالصوره"
M4_TEXT = "🎮 **قائمة اوامر التسليه (م4) :**\n━━━━━━━━━━━━━━━\n• كت / كت تويت (لعبة الأسئلة العشوائية)\n• راتب / فلوسي (نظام البنك التفاعلي)\n• افتاري / الايدي بالصوره\n• رفع وتنزيل رتب التسلية (هطف، بثر، خروف، كلب)\n• زواج | طلاق | تتزوجني"
M5_TEXT = "👑 **قائمة أوامر المطور الأساسي (م5) :**\n━━━━━━━━━━━━━━━\n• ذيع + ايدي المجموعه (بالرد لإرسال إذاعة)\n• تحديث | اعاده تشغيل - reload\n• حظر عام | كتم عام | رفع وتنزيل Dev"
M6_TEXT = "🛠️ **قائمة الاوامر الخدميه (م6) :**\n━━━━━━━━━━━━━━━\n• همسه (بالرد على شخص لرسالة سرية)\n• معنى + اسمك | العمر + عمرك\n• ترجمة | قران | اذكار | اقتباسات | ميمز | افلام"


# === 3. معالج الخاص (لوحة المطور بالخاص تعمل تلقائياً) ===
@bot.message_handler(commands=['start', 'panel'], chat_types=['private'])
def private_panel(message):
    if not is_main_dev(message.from_user.id):
        bot.reply_to(message, "❌ هذا البوت مخصص للمطور الأساسي فقط.")
        return
    bot.send_message(
        message.chat.id,
        f"🙋‍♂️ أهلاً بك عزيزي Dev في الخاص\n🛠️ هذه لوحة التحكم الخاصة بك للتحكم بالبنية التحتية لسورس البوت:",
        reply_markup=get_private_dev_keyboard()
    )


# === 4. المعالج المركزي للجروبات والقنوات ===
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup', 'channel'])
def handle_group_messages(message):
    text = message.text
    if not text:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    # أمر التفعيل الحصري للإدارة والمالكين
    if text == "تفعيل":
        if not is_admin_or_owner(chat_id, user_id):
            return
        if is_chat_activated(chat_id):
            bot.reply_to(message, "⚙️ البوت مفعل مسبقاً في هذه المجموعة ومسجّل في قاعدة البيانات.")
        else:
            activate_chat(chat_id)
            bot.reply_to(message, "🟢 تم تفعيل البوت وحفظ المجموعة في قاعدة البيانات الدائمة! جميع المزايا نشطة الآن.")
        return

    # أمر التعطيل الحصري للإدارة والمالكين
    if text == "تعطيل":
        if not is_admin_or_owner(chat_id, user_id):
            return
        if is_chat_activated(chat_id):
            deactivate_chat(chat_id)
            bot.reply_to(message, "🔴 تم تعطيل البوت ومسح المجموعة من قاعدة البيانات بنجاح.")
        else:
            bot.reply_to(message, "⚠️ البوت غير مفعّل في هذه المجموعة من الأساس.")
        return

    # الفحص الصارم من ملف الـ DB؛ إذا لم يكن الجروب مفعلاً يتجاهل البوت الرسائل تماماً
    if not is_chat_activated(chat_id):
        return

    # أمر قائمة الأوامر التفاعلية بالجروبات
    if text == "الاوامر":
        if not is_admin_or_owner(chat_id, user_id):
            return
        bot.send_message(
            chat_id,
            "الاوامر\n- أهلاً بك عزيزي في قائمة الاوامر :\n━━━━━━━━━━━━━━━\n🔹 م1 : اوامر الادمنيه\n🔹 م2 : اوامر الاعدادات\n🔹 م3 : اوامر القفل - الفتح\n🔹 م4 : اوامر التسليه\n🔹 م5 : اوامر Dev\n🔹 م6 : الاوامر الخدميه\n━━━━━━━━━━━━━━━",
            reply_markup=get_group_commands_keyboard(),
            reply_to_message_id=message.message_id
        )
        return

    # لعبة (كت تويت)
    if text in ["كت", "كت تويت"]:
        bot.reply_to(message, f"💬 **كت تويت :**\n━━━━━━━━━━━━\n{random.choice(KAT_QUESTIONS)}")

    # لعبة (معنى الأسماء)
    elif text.startswith("معنى "):
        name = text.replace("معنى ", "").strip()
        bot.reply_to(message, f"📖 **معنى اسم ({name}) :**\n━━━━━━━━━━━━\n{NAME_MEANINGS.get(name, 'عذراً، هذا الاسم غير متوفر في قاموسي حالياً.')}")

    # نظام البنك (تعديل الرصيد داخل SQLite3 بأمان)
    elif text == "راتب":
        reward = random.randint(50, 500)
        new_bal = add_balance(user_id, reward)
        bot.reply_to(message, f"💰 تم نزول راتبك اليومي بقيمة **{reward}** ريال!\n💳 رصيدك الإجمالي المحفوظ في البنك: **{new_bal}** ريال.")
    elif text == "flosy" or text == "فلوسي":
        bal = get_balance(user_id)
        bot.reply_to(message, f"💳 رصيدك الحالي المحفوظ آمن في البنك هو: **{bal}** ريال.")

    # الأيدي بالصورة وافتاري
    elif text in ["الايدي بالصوره", "افتاري"]:
