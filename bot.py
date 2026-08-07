import os
import telebot

# يقرأ التوكن من Railway Variables
TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "اهلا! البوت اشتغل بنجاح ✅")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "انت قلت: " + message.text)

print("Bot is running...")
bot.infinity_polling()
