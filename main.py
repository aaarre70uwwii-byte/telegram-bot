import os
import sys
import io
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ خطأ: لم يتم العثور على متغير البيئة 'BOT_TOKEN'.")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
user_codes = {}

def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⌨️ فتح الكيبورد البرمجي", callback_data="open_kb"),
        InlineKeyboardButton("🚀 تشغيل الكود المكتوب", callback_data="run_code")
    )
    markup.add(
        InlineKeyboardButton("📋 عرض الكود الحالي", callback_data="show_code"),
        InlineKeyboardButton("🧹 مسح الكود بالكامل", callback_data="clear_code")
    )
    return markup

def get_dev_keyboard():
    markup = InlineKeyboardMarkup(row_width=4)
    markup.row(
        InlineKeyboardButton("🐍 Python", callback_data="lang_py"),
        InlineKeyboardButton("🌐 Web/JS", callback_data="lang_web"),
        InlineKeyboardButton("🗄️ SQL", callback_data="lang_sql"),
        InlineKeyboardButton("🐙 Git", callback_data="lang_git")
    )
    markup.row(
        InlineKeyboardButton("{ }", callback_data="add_{ }"),
        InlineKeyboardButton("[ ]", callback_data="add_[ ]"),
        InlineKeyboardButton("( )", callback_data="add_( )"),
        InlineKeyboardButton("< >", callback_data="add_< >")
    )
    markup.row(
        InlineKeyboardButton(";", callback_data="add_;"),
        InlineKeyboardButton("=", callback_data="add_="),
        InlineKeyboardButton("+", callback_data="add_+"),
        InlineKeyboardButton("-", callback_data="add_-")
    )
    markup.row(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu"))
    return markup

def get_sub_keyboard(category):
    markup = InlineKeyboardMarkup(row_width=1)
    templates = {
        'py': [('print("Hello")', 'tpl_print("Hello")'), ('if condition:', 'tpl_if condition:'), ('for i in range(5):', 'tpl_for i in range(5):')],
        'web': [('console.log()', 'tpl_console.log()'), ('<div></div>', 'tpl_<div></div>'), ('document.id', 'tpl_document.id')],
        'sql': [('SELECT * FROM', 'tpl_SELECT * FROM'), ('WHERE id = 1', 'tpl_WHERE id = 1')],
        'git': [('git add.', 'tpl_git add.'), ('git commit -m', 'tpl_git commit -m'), ('git push', 'tpl_git push')]
    }
    for text, callback in templates.get(category, []):
        markup.add(InlineKeyboardButton(text, callback_data=callback))
    markup.add(InlineKeyboardButton("⬅️ العودة لكيبورد الرموز", callback_data="open_kb"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    user_codes.setdefault(chat_id, "")
    welcome_text = "👋 أهلاً بك في كيبورد المطورين العام!\n\nهذا البوت يدعم الاستخدام الجماعي، لكل مستخدم مساحة برمجة خاصة به."
    bot.send_message(chat_id, welcome_text, reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_text_input(message):
    chat_id = message.chat.id
    user_codes.setdefault(chat_id, "")
    user_codes[chat_id] += message.text + "\n"
    bot.reply_to(message, "📥 تم حفظ الكود في مساحتك الخاصة!", reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    user_codes.setdefault(chat_id, "")

    if data == "main_menu":
        bot.edit_message_text("📱 القائمة الرئيسية:", chat_id, call.message_id, reply_markup=get_main_keyboard())
    elif data == "open_kb":
        bot.edit_message_text("⌨️ كيبورد الرموز والأوامر الجاهزة:", chat_id, call.message.message_id, reply_markup=get_dev_keyboard())
    elif data.startswith("lang_"):
        lang = data.split("_")[1]
        bot.edit_message_text(f"🚀 اختصارات {lang.upper()}:", chat_id, call.message.message_id, reply_markup=get_sub_keyboard(lang))
    elif data.startswith("add_"):
        symbol = data.replace("add_", "")
        user_codes[chat_id] += symbol + " "
        bot.answer_callback_query(call.id, f"تم إضافة: {symbol}")
    elif data.startswith("tpl_"):
        template = data.replace("tpl_", "")
        user_codes[chat_id] += template + "\n"
        bot.answer_callback_query(call.id, "تم إضافة الجملة البرمجية!")
    elif data == "show_code":
        current_code = user_codes[chat_id] if user_codes[chat_id].strip() else "[مساحة كودك فارغة]"
        bot.send_message(chat_id, f"📝 كودك الحالي:\n```\n{current_code}\n```")
        bot.answer_callback_query(call.id)
    elif data == "clear_code":
        user_codes[chat_id] = ""
        bot.send_message(chat_id, "🧹 تم مسح مساحة الأكواد الخاصة بك.")
        bot.answer_callback_query(call.id)
    elif data == "run_code":
        bot.send_message(chat_id, "⚠️ التشغيل معطل لأسباب أمنية.\nالبوت للكتابة والحفظ فقط.")
        bot.answer_callback_query(call.id)

if __name__ == '__main__': # تم التصليح
    print("🟢 البوت يعمل الآن...")
    bot.infinity_polling()
