import os
import telebot
from flask import Flask

# جيب التوكن من متغيرات البيئة
TOKEN = os.environ.get("TOKEN") 
bot = telebot.TeleBot(TOKEN)

# عشان ما يطفي على Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

# مثال امر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "اهلا! انا بوت 𝐓𝐢𝐚 شغال 24 ساعة 🔥")

# شغل البوت
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"قلت: {message.text}")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
