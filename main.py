import os
import sys
import time
import io
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. جلب توكن البوت بشكل آمن من متغيرات الاستضافة
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ خطأ: لم يتم العثور على متغير البيئة 'BOT_TOKEN'. يرجى إضافته في منصة الاستضافة.")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# تخزين الأكواد الخاصة بكل مطور في الخاص
user_codes = {}
# تخزين إعدادات الحماية لكل جروب بشكل منفصل
group_settings = {}

# قوائم ألعاب التسلية (م4)
FUN_QUESTIONS = [
    "لو خيروك تعيش في جزيرة لوحدك أو مع شخص تكرهه؟",
    "كت تويت: صفة مستحيل تتحملها بالشخص اللي قدامك؟",
    "صراحة: هل اطلعت على جوال شخص بدون علمه من قبل؟",
    "لو خيروك تسافر للمستقبل أو ترجع للماضي؟"
]
JOKES = [
    "مرة واحد اشترى حذاء ضيق، قام يركض عشان يوسعه!",
    "محشش شاف إشارة ممنوع الوقوف، قام انسدح!",
    "مرة نملة شافت عصير فراولة قالت: واو أخيراً شفت البحر الأحمر!"
]

# نص لوحة أوامر الجروبات الأساسي
GROUP_MENU_TEXT = (
    "↤اهلا عمري في قائمه اوامر» 𝐓𝐢𝐚: ✓\n"
    "━━━━━ 𝐓𝐢α ━━━━━\n\n"
    "◂ م2 : اوامر الاعدادات\n"
    "◂ م3 : اوامر القفل - الفتح\n"
    "◂ م4 : اوامر التسليه\n"
    "◂ م5 : اوامر Dev\n"
    "◂ م6 : الاوامر الخدميه \n\n"
    "━━━━━ 𝐓𝐢α ━━━━━\n"
    "القائمه الريئسيه» التالي» اخفاء الاوامر\n\n"
    "تحديثاث:« 𝐓𝐢α»: @eeccvu"
)

# ---------- دالات فحص الهوية والتهيئة ----------

def is_admin(chat_id, user_id):
    """التحقق من صلاحيات المشرف في الجروبات"""
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['creator', 'administrator']
    except Exception:
        return False

def init_group_settings(chat_id):
    """تهيئة نظام الحماية عند دخول الجروب"""
    if chat_id not in group_settings:
        group_settings[chat_id] = {
            "status": True,       
            "welcome": True,      
            "welcome_msg": "أهلاً بك يا قلبي في المجموعة! نورتنا ✨",
            "bot_name": "𝐓𝐢𝐚",
            "lock_links": False,
            "lock_photos": False,
            "lock_stickers": False
        }
    return group_settings[chat_id]

# ---------- 🛠️ قسم لوحات المفاتيح (Keyboards) ----------

# [الخاص] لوحة المطور الرئيسية
def get_dev_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⌨️ فتح كيبورد الرموز", callback_data="dev_open_kb"),
        InlineKeyboardButton("🚀 تشغيل الكود البرمي", callback_data="dev_run_code")
    )
    markup.add(
        InlineKeyboardButton("📋 عرض كودي الحالي", callback_data="dev_show_code"),
        InlineKeyboardButton("🧹 مسح الشاشة", callback_data="dev_clear_code")
    )
    return markup

# [الخاص] لوحة الرموز واختصارات لغات البرمجة للمطور
def get_dev_symbols_keyboard():
    markup = InlineKeyboardMarkup(row_width=4)
    markup.row(
        InlineKeyboardButton("🐍 Python", callback_data="dev_lang_py"),
        InlineKeyboardButton("🌐 Web/JS", callback_data="dev_lang_web"),
        InlineKeyboardButton("🗄️ SQL", callback_data="dev_lang_sql"),
        InlineKeyboardButton("🐙 Git", callback_data="dev_lang_git")
    )
    markup.row(
        InlineKeyboardButton("{ }", callback_data="dev_add_{ }"),
        InlineKeyboardButton("[ ]", callback_data="dev_add_[ ]"),
        InlineKeyboardButton("( )", callback_data="dev_add_( )"),
        InlineKeyboardButton("< >", callback_data="dev_add_< >")
    )
    markup.row(
        InlineKeyboardButton(";", callback_data="dev_add_;"),
        InlineKeyboardButton("=", callback_data="dev_add_="),
        InlineKeyboardButton("+", callback_data="dev_add_+"),
        InlineKeyboardButton("-", callback_data="dev_add_-")
    )
    markup.row(InlineKeyboardButton("🔙 العودة للتحكم", callback_data="dev_main_menu"))
    return markup

# [الخاص] لوحة أزرار الأكواد الجاهزة (Templates)
def get_dev_templates_keyboard(category):
    markup = InlineKeyboardMarkup(row_width=1)
    templates = {
        'py': [('print("Hello")', 'dtpl_print("Hello")'), ('if condition:', 'dtpl_if condition:'), ('for i in range(5):', 'dtpl_for i in range(5):')],
        'web': [('console.log()', 'dtpl_console.log()'), ('<div></div>', 'dtpl_<div></div>')],
        'sql': [('SELECT * FROM', 'dtpl_SELECT * FROM'), ('WHERE id = 1', 'dtpl_WHERE id = 1')],
        'git': [('git add .', 'dtpl_git add .'), ('git commit -m', 'dtpl_git commit -m')]
    }
    for text, callback in templates.get(category, []):
        markup.add(InlineKeyboardButton(text, callback_data=callback))
    markup.add(InlineKeyboardButton("⬅️ العودة لكيبورد الرموز", callback_data="dev_open_kb"))
    return markup

# [الجروبات] لوحة أزرار الإدارة (م1 إلى م6) - تم إصلاح المسميات البرمجية هنا
def get_group_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.row(InlineKeyboardButton("م1", callback_data="g_m1"), InlineKeyboardButton("م2", callback_data="g_m2"), InlineKeyboardButton("م3", callback_data="g_m3"))
    markup.row(InlineKeyboardButton("م4", callback_data="g_m4"), InlineKeyboardButton("م5", callback_data="g_m5"), InlineKeyboardButton("م6", callback_data="g_m6"))
    markup.row(InlineKeyboardButton("التالي ➡️", callback_data="g_next"), InlineKeyboardButton("إخفاء الأوامر ✖️", callback_data="g_hide"))
    markup.row(InlineKeyboardButton("تحديثات 𝐓𝐢α 📢", url="https://t.me"))
    return markup

def get_group_back_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 العودة لقائمة الأوامر", callback_data="g_main_menu"))
    return markup


# ---------- 💬 قسم استقبال الرسائل والأوامر النصية ----------

@bot.message_handler(commands=['start', 'help', 'الاوامر', 'أوامر', 'اوامر'])
def handle_start_and_commands(message):
    chat_id = message.chat.id
    
    # 1. إذا كان الاستخدام في الخاص (تفعيل لوحة المطور)
    if message.chat.type == "private":
        if chat_id not in user_codes: user_codes[chat_id] = ""
        welcome_txt = (
            "💻 **مرحباً بك في لوحة كيبورد المطور المتكاملة والمفحوصة!**\n\n"
            "أنت الآن في المحادثة الخاصة. يمكنك كتابة أي كود بايثون مباشرة أو استخدام أزرار الرموز بالأسفل، "
            "ثم الضغط على زر التشغيل لتنفيذ الكود وقراءة المخرجات فوراً!"
        )
        bot.send_message(chat_id, welcome_txt, reply_markup=get_dev_main_keyboard(), parse_mode="Markdown")
        
    # 2. إذا كان الاستخدام في الجروبات والقنوات (تفعيل لوحة الإدارة والحماية)
    else:
        init_group_settings(chat_id)
        bot.reply_to(message, GROUP_MENU_TEXT, reply_markup=get_group_keyboard())


# --- [الجروبات] برمجة وظائف أوامر م2 (الإعدادات) تفاعلياً وواقعياً ---
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text in ['تفعيل', 'تعطيل', 'الترحيب تفعيل', 'الترحيب تعطيل', 'الاعدادات'])
def handle_group_m2(message):
    chat_id = message.chat.id
    if not is_admin(chat_id, message.from_user.id): return
    settings = init_group_settings(chat_id)
    text = message.text
    
    if text == 'تفعيل': settings["status"] = True; bot.reply_to(message, "🟢 تم تفعيل البوت في المجموعة.")
    elif text == 'تعطيل': settings["status"] = False; bot.reply_to(message, "🔴 تم تعطيل البوت في المجموعة.")
    elif text == 'الترحيب تفعيل': settings["welcome"] = True; bot.reply_to(message, "✅ تم تفعيل رسائل الترحيب.")
    elif text == 'الترحيب تعطيل': settings["welcome"] = False; bot.reply_to(message, "✖️ تم تعطيل رسائل الترحيب.")
    elif text == 'الاعدادات':
        status_txt = f"⚙️ **إعدادات حماية الجروب الحالية:**\n\n• البوت: {'مفعل 🟢' if settings['status'] else 'معطل 🔴'}\n• الترحيب: {'مفعل ✅' if settings['welcome'] else 'معطل ✖️'}\n• قفل الروابط: {'مقفل 🔒' if settings['lock_links'] else 'مفتوح 🔓'}\n• قفل الصور: {'مقفل 🔒' if settings['lock_photos'] else 'مفتوح 🔓'}\n• قفل الملصقات: {'مقفل 🔒' if settings['lock_stickers'] else 'مفتوح 🔓'}"
        bot.reply_to(message, status_txt, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text and (msg.text.startswith('وضع ترحيب ') or msg.text.startswith('تعيين اسم ')))
def handle_group_m2_inputs(message):
    chat_id = message.chat.id
    if not is_admin(chat_id, message.from_user.id): return
    settings = init_group_settings(chat_id)
    
    if message.text.startswith('وضع ترحيب '):
        settings["welcome_msg"] = message.text.replace('وضع ترحيب ', '')
        bot.reply_to(message, "📝 تم حفظ نص الترحيب الجديد بنجاح.")
    elif message.text.startswith('تعيين اسم '):
        settings["bot_name"] = message.text.replace('تعيين اسم ', '')
        bot.reply_to(message, f"⚜️ تم تغيير اسم البوت بالجروب إلى: {settings['bot_name']}")


# --- [الجروبات] برمجة وظائف أوامر م3 (القفل والفتح والأمان) ---
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text in ['قفل الروابط', 'فتح الروابط', 'قفل الصور', 'فتح الصور', 'قفل الملصقات', 'فتح الملصقات'])
def handle_group_m3_locks(message):
    chat_id = message.chat.id
    if not is_admin(chat_id, message.from_user.id): return
    settings = init_group_settings(chat_id)
    text = message.text
    
    if text == 'قفل الروابط': settings["lock_links"] = True
    elif text == 'فتح الروابط': settings["lock_links"] = False
    elif text == 'قفل الصور': settings["lock_photos"] = True
    elif text == 'فتح الصور': settings["lock_photos"] = False
    elif text == 'قفل الملصقات': settings["lock_stickers"] = True
    elif text == 'فتح الملصقات': settings["lock_stickers"] = False
    
    bot.reply_to(message, f"🔒 تم تنفيذ أمر: **{text}** بنجاح.", parse_mode="Markdown")


# --- [الجروبات] برمجة وظائف أوامر م4 (التسلية والالعاب العشوائية) ---
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text in ['فعالية', 'كت تويت', 'صراحه', 'لو خيروك', 'نكته'])
def handle_group_m4_fun(message):
    text = message.text
    if text in ['فعالية', 'كت تويت', 'صراحه', 'لو خيروك']:
        bot.reply_to(message, f"🎯 **{text}:**\n\n{random.choice(FUN_QUESTIONS)}")
    elif text == 'نكته':
