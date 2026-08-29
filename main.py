import os
import sqlite3
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ====== 1. الاستدعاء للملفين ======
from dev_panel import DEV_DATA, get_dev_keyboard, check_group # غيرت الاسم هنا
import dev_panel
import main_menu
# =====================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID") # خليه يجي من Railway احسن
bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS welcome_msg (text TEXT)")
    c.execute("INSERT OR IGNORE INTO welcome_msg VALUES (?)", (DEV_DATA["welcome"],))
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def save_user(user_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,)); conn.commit(); conn.close()

def save_group(chat_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("INSERT OR IGNORE INTO groups VALUES (?)", (chat_id,)); conn.commit(); conn.close()

def get_welcome():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("SELECT text FROM welcome_msg LIMIT 1"); result = c.fetchone(); conn.close()
    return result[0] if result else DEV_DATA["welcome"]

# ====== 2. دالة التحقق من تفعيل الجروب ======
def check_group_status(message):
    if message.chat.type in ["group", "supergroup"]:
        if str(message.from_user.id)!= str(OWNER_ID):
            if not check_group(message.chat.id): # وغيرت الاسم هنا
                bot.reply_to(message, "🔴 البوت معطل في هذه المجموعة\nفعلني من لوحة المطور")
                return False
    return True
# ============================================

init_db()

@bot.message_handler(commands=['start'])
def cmd_start(message):
    save_user(message.from_user.id)
    if message.chat.type in ["group", "supergroup"]:
        save_group(message.chat.id)

    welcome_text = get_welcome()

    if str(message.from_user.id) == str(OWNER_ID) and message.chat.type == "private":
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_dev_keyboard())
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("الاوامر"))
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "الاوامر")
def show_commands_btn(m):
    if not check_group_status(m): return
    text, markup = main_menu.create_main_menu(1)
    bot.send_message(m.chat.id, text, reply_markup=markup)

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    if message.chat.type in ["group", "supergroup"]:
        save_group(message.chat.id)

dev_panel.register_handlers(bot)
main_menu.register_menu_handlers(bot)

print(f"✅ البوت {DEV_DATA['bot_name']} شغال")
bot.infinity_polling(skip_pending=True)
