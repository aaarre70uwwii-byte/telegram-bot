import os
import sys
import time
import io
import random
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# ---------- 🌐 خادم الويب لإبقاء البوت حياً ----------
app = Flask('')

@app.route('/')
def home():
    return "🟢 البوت العام مستقر 24/7 ومؤمن بالكامل ضد أي توقف برمي!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()

# ---------- 🤖 إعدادات البوت والتوكن ----------
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ خطأ: لم يتم العثور على متغير البيئة 'BOT_TOKEN'. يرجى إضافته في منصة الاستضافة.")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

user_codes = {}
group_settings = {}
secret_whispers = {}
custom_commands = {}

# 👑 آيدي حسابك الحقيقي ليتعرف عليك البوت فوراً في الجروبات ويحميك
DEVELOPER_ID = 7488375443  

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

GROUP_MENU_TEXT = (
    "↤اهلا عمري في قائمه اوامر» 𝐓𝐢α: ✓\n"
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
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['creator', 'administrator']
    except Exception:
        return False

def get_user_rank(chat_id, user_id):
    if user_id == DEVELOPER_ID:
        return "مطور السورس الأساسي 👑"
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status == 'creator': return "المالك الأساسي للمجموعة 💎"
        elif member.status == 'administrator': return "مشرف الجروب 👮‍♂️"
        else: return "عضو محترم 👤"
    except Exception:
        return "عضو 👤"

def init_group_settings(chat_id):
    if chat_id not in group_settings:
        group_settings[chat_id] = {
            "status": True,       
            "welcome": True,      
            "welcome_msg": "أهلاً بك يا قلبي في المجموعة! نورتنا ✨",
            "bot_name": "𝐓𝐢α",
            "lock_links": False,
            "lock_photos": False,
            "lock_stickers": False
        }
    return group_settings[chat_id]

def get_command(chat_id, text):
    if chat_id in custom_commands and text in custom_commands[chat_id]:
        return custom_commands[chat_id][text]
    return text

# ---------- 🛠️ قسم لوحات المفاتيح ----------

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
    if message.chat.type == "private":
        if chat_id not in user_codes: user_codes[chat_id] = ""
        welcome_txt = (
            "💻 **مرحباً بك في لوحة كيبورد المطور المتكاملة والمحمية 24/7!**\n\n"
            "أنت الآن في المحادثة الخاصة. يمكنك كتابة أي كود بايثون مباشرة أو استخدام أزرار الرموز بالأسفل, "
            "ثم الضغط على زر التشغيل لتنفيذ الكود وقراءة المخرجات فوراً!"
        )
        bot.send_message(chat_id, welcome_txt, reply_markup=get_dev_main_keyboard(), parse_mode="Markdown")
    else:
        init_group_settings(chat_id)
        bot.reply_to(message, GROUP_MENU_TEXT, reply_markup=get_group_keyboard())

# نظام تعيين وتغيير أسماء الأوامر بالجروب (تم تأمين الثغرة والفحص هنا)
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text and msg.text.startswith("تعيين امر "))
def handle_change_command_name(message):
    chat_id = message.chat.id
    if not is_admin(chat_id, message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, "⚠️ طريقة الاستخدام خطأ! اكتب كالتالي:\n`تعيين امر` + [الأمر القديم] + [الأمر الجديد]")
        return
    old_cmd = parts[2]
    new_cmd = parts[3]
    if chat_id not in custom_commands: custom_commands[chat_id] = {}
    custom_commands[chat_id][new_cmd] = old_cmd
    bot.reply_to(message, f"⚜️ تم تعيين الأمر الجديد بنجاح!\n• أصبح أمر **[{new_cmd}]** يقوم بوظيفة أمر **[{old_cmd}]**.", parse_mode="Markdown")

# نظام الهمسات الحقيقي (اهمس)
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text and msg.text.startswith("اهمس "))
def handle_whisper_command(message):
    chat_id = message.chat.id
    sender_id = message.from_user.id
    sender_name = message.from_user.first_name
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ يجب إرسال الأمر بالرد على الشخص الذي تريد الهمس له!")
        return
    target_user_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    whisper_text = message.text.replace("اهمس ", "").strip()
    if not whisper_text: return
    whisper_id = f"w_{int(time.time())}_{random.randint(100, 999)}"
    secret_whispers[whisper_id] = {"sender": sender_id, "target": target_user_id, "text": whisper_text}
    try: bot.delete_message(chat_id, message.message_id)
    except Exception: pass
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔒 قراءة الهمسة السرية", callback_data=f"read_{whisper_id}"))
    bot.send_message(chat_id, f"🗣️ مستخدم: {sender_name}\n👤 أرسل همسة سرية إلى: {target_name}\n👇 لا يمكن لأحد قراءتها غيرهما!", reply_markup=markup)

# نظام ردود المطور التلقائية
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text and ('مطور' in msg.text or 'المطور' in msg.text))
def handle_developer_replies(message):
    dev_replies = [
        "تاج راسي المطور وغالينا، تبي منه شيء؟ 😎",
        "المطور مشغول حالياً ببرمجة أكواد خارقة مثلي، لا تزعجه 💻✨",
        "لبيك! ذكرت اسم المطور الحاضر بقلوبنا، شبيك لبيك؟ ⚜️"
    ]
    if message.from_user.id != DEVELOPER_ID:
        bot.reply_to(message, random.choice(dev_replies))

# المعالج الشامل لأقسام الأوامر مع دعم ميزة "تغيير اسم الأمر" الذكية
@bot.message_handler(func=lambda msg: msg.chat.type != "private" and msg.text)
def handle_all_group_text_commands(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = get_command(chat_id, message.text)
    
