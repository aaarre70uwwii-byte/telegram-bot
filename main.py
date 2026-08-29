import os
import sqlite3
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ====== هنا الاستدعاء للملفين ======
from dev_commands import register_handlers as register_dev_handlers, DEV_DATA, get_dev_keyboard # << عدلنا الاسم
from main_menu import register_menu_handlers
# =====================================

BOT_TOKEN = os.getenv("BOT_TOKEN") # "حط_التوكن_هنا"
OWNER_ID = 7488375443 # << ايديك

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
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
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("SELECT text FROM welcome_msg"); result = c.fetchone(); conn.close()
    return result[0] if result else DEV_DATA["welcome"]

init_db()

@bot.message_handler(commands=['start'])
def cmd_start(message):
    save_user(message.from_user.id)
    if message.chat.type in ["group", "supergroup"]:
        save_group(message.chat.id)

    welcome_text = get_welcome()

    if str(message.from_user.id) == str(OWNER_ID) and message.chat.type == "private":
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_dev_keyboard())
    elif message.chat.type == "private":
        bot.send_message(message.chat.id, welcome_text)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("الاوامر"))
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    if message.chat.type in ["group", "supergroup"]:
        save_group(message.chat.id)

# ====== هنا تشغيل الهاندلرات من الملفين ======
register_dev_handlers(bot) # يشغل dev_commands.py
register_menu_handlers(bot) # يشغل main_menu.py
# =============================================

if __name__ == "__main__":
    print(f"البوت {DEV_DATA['bot_name']} شغال ✅")
    bot.infinity_polling(skip_pending=True)
