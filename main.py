import telebot
import os
import sqlite3
from flask import Flask
from threading import Thread

import m1
import m2
import m3
import m4
import m5
import m6
import menu

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Tia is Running ✅"

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

@bot.message_handler(func=lambda m: True, chat_types=['group','supergroup'])
def check_all(m):
    if not m.from_user: return
    user_id = m.from_user.id
    text = m.text.lower() if m.text else ""
    
    conn = sqlite3.connect("dev_data.db"); cursor = conn.cursor()
    
    # فحص الحظر والكتم
    cursor.execute("SELECT user_id FROM gban WHERE user_id =?", (user_id,))
    if cursor.fetchone():
        try: bot.delete_message(m.chat.id, m.message_id); bot.ban_chat_member(m.chat.id, user_id)
        except: pass
        conn.close(); return
    
    cursor.execute("SELECT user_id FROM gmute WHERE user_id =?", (user_id,))
    if cursor.fetchone():
        try: bot.delete_message(m.chat.id, m.message_id)
        except: pass
        conn.close(); return
    
    # اي امر = تظهر القائمة
    if text:
        commands_words = ['حظر', 'كتم', 'الغاء', 'رفع', 'تنزيل', 'معلومات', 'القائمة', 'الاوامر', 'تفعيل', 'ban', 'mute']
        
        if any(word in text for word in commands_words):
            if 'تفعيل' in text:
                bot.reply_to(m, "✅ تم تفعيل البوت")
            
            try:
                menu.show_menu(bot, m.chat.id) # تظهر القائمة
            except: pass
    
    conn.close()

def run_bot():
    print("Bot Tia Started...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
