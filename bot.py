import telebot
import os

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# امر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "هلا والله 👋\nانا بوتك شغال 24 ساعة على Railway\nاكتب /help عشان تشوف الاوامر")

# امر /help  
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "الاوامر المتاحة:\n/start - ترحيب\n/help - المساعدة\n/echo - عيد الكلام")

# امر /echo
@bot.message_handler(commands=['echo'])
def send_echo(message):
    txt = message.text.replace('/echo ', '')
    bot.reply_to(message, f"انت قلت: {txt}")

# يرد على اي رسالة عادية
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"وصلني: {message.text}")

print("Bot is running...")
bot.polling()
