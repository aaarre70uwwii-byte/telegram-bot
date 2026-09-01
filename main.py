import telebot
import os
import menu
import m1
import m2
import m3
import m4

TOKEN = os.environ.get('TOKEN') # حطه في Railway Variables
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# تسجيل كل الهاندلرز
menu.register_handlers(bot)
m1.register_m1_handlers(bot)
m2.register_m2_handlers(bot)
m3.register_m3_handlers(bot)
m4.register_m4_handlers(bot)

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.type == 'private':
        menu.show_menu(bot, m.chat.id)
    else:
        bot.reply_to(m, "ارسل /start في الخاص لعرض الاوامر")

@bot.message_handler(commands=['اوامر'])
def commands(m):
    menu.show_menu(bot, m.chat.id)

print("Bot is running...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
