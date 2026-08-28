import os
import sqlite3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# استدعاء الملفات
import dev_keyboard
from main_menu import main_menu
import admin_commands
import lock_commands
import fun_commands
import service_commands

# ======== قراءة المتغيرات من Railway ========
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
API_ID = os.getenv("API_ID") # جديد
API_HASH = os.getenv("API_HASH") # جديد

MAIN_DEV_ID = int(OWNER_ID) # حولناه لرقم
bot = telebot.TeleBot(BOT_TOKEN)

# نشغل قاعدة البيانات اول ما يشتغل
dev_keyboard.init_db()

def is_main_dev(u): return u == MAIN_DEV_ID

# امر البداية
@bot.message_handler(commands=['start'])
def start(m):
    if is_main_dev(m.from_user.id):
        c=sqlite3.connect(dev_keyboard.DB_FILE).cursor(); c.execute("SELECT text FROM welcome"); w=c.fetchone(); c.connection.close()
        welcome_text = w[0] if w else f"🙋‍♂️ اهلا بك في بوت {dev_keyboard.bot_name}"
        bot.send_message(m.chat.id, welcome_text, reply_markup=dev_keyboard.kb_private())
    else:
        bot.send_message(m.chat.id, f"اهلا فيك ببوت {dev_keyboard.bot_name}", reply_markup=main_menu())

# معالج رسائل المطور
@bot.message_handler(func=lambda m: m.chat.type == 'private' and is_main_dev(m.from_user.id))
def dev_handler(m):
    if m.from_user.id in dev_keyboard.waiting:
        dev_keyboard.wait_handler(bot, m, MAIN_DEV_ID)
    else:
        dev_keyboard.handle_dev_commands(bot, m, MAIN_DEV_ID)

# معالج رسائل الاعضاء العاديين - ازرار م1 م2 م3 م4
@bot.message_handler(func=lambda m: not is_main_dev(m.from_user.id))
def user_handler(m):
    text = m.text
    if text == "م1": admin_commands.admin_panel(bot, m)
    elif text == "م2": lock_commands.lock_panel(bot, m)
    elif text == "م3": fun_commands.fun_panel(bot, m)
    elif text == "م4": service_commands.service_panel(bot, m)

# معالج القروبات
@bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'])
def group_handler(m):
    c=sqlite3.connect(dev_keyboard.DB_FILE).cursor()
    c.execute("INSERT OR IGNORE INTO groups VALUES (?)",(m.chat.id,))
    c.connection.commit(); c.connection.close()

    # الردود العامة
    if dev_keyboard.bot_status and m.text:
        c=sqlite3.connect(dev_keyboard.DB_FILE).cursor(); c.execute("SELECT reply FROM g_reply WHERE word=?",(m.text,)); r=c.fetchone(); c.connection.close()
        if r: bot.reply_to(m, r[0])

print(f"البوت {dev_keyboard.bot_name} شغال")
print(f"OWNER_ID: {MAIN_DEV_ID}") # عشان تتاكد انه قارئ المتغيرات
bot.polling(none_stop=True)
