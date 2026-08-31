import telebot
import os
import sqlite3
from flask import Flask

# استدعاء كل الملفات
import m1
import m2
import m3
import m4
import m5
import m6
import menu

# التوكن حقك
TOKEN = "ضع_التوكن_هنا"
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Tia is Running ✅"

# تفعيل كل الاوامر
m1.register_handlers(bot)
m2.register_handlers(bot)
m3.register_handlers(bot)
m4.register_handlers(bot)
m5.register_handlers(bot)
m6.register_handlers(bot)
menu.register_handlers(bot)

@bot.message_handler(commands=['start'], chat_types=['private'])
def start(m):
    bot.reply_to(m, f"{m5.DEV_DATA['welcome']}\n\nاكتب /القائمة لعرض القائمة الرئيسية")

# حماية عامة: حظر وكتم عام
@bot.message_handler(func=lambda m: True, chat_types=['group','supergroup'])
def check_gban_gmute(m):
    if not m.from_user: return
    user_id = m.from_user.id
    conn = sqlite3.connect("dev_data.db"); cursor = conn.cursor()
    
    # تشييك الحظر العام
    cursor.execute("SELECT user_id FROM gban WHERE user_id =?", (user_id,))
    if cursor.fetchone():
        try: bot.delete_message(m.chat.id, m.message_id); bot.ban_chat_member(m.chat.id, user_id)
        except: pass
        conn.close(); return
    
    # تشييك الكتم العام  
    cursor.execute("SELECT user_id FROM gmute WHERE user_id =?", (user_id,))
    if cursor.fetchone():
        try: bot.delete_message(m.chat.id, m.message_id)
        except: pass
    conn.close()

# تشغيل البوت
if __name__ == "__main__":
    print("Bot Tia Started...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
