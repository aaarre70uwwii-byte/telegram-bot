import os
import telebot
import main_menu
import m1
import m2
import m3
import m4
import m5
import m6 # <-- مهم يكون موجود
import dev_panel # <-- لوحة المطور

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['اوامر', 'start'])
def start(m):
    main_menu.show_main_menu(bot, m)

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "الاوامر", chat_types=['group','supergroup','private'])
def show_menu_text(m):
    main_menu.show_main_menu(bot, m)

# ===== لوحة المطور =====
@bot.message_handler(commands=['المطور'])
def dev_cmd(m):
    if m.chat.type == 'private' and str(m.from_user.id) == OWNER_ID:
        bot.send_message(m.chat.id, "لوحة المطور 👑", reply_markup=dev_panel.get_dev_keyboard())
        dev_panel.register_handlers(bot, OWNER_ID) # نمرر الOWNER_ID
    else:
        bot.send_message(m.chat.id, "❌ امر المطور للخاص فقط")

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    main_menu.handle_callbacks(bot, c)

print("البوت Tia شغال...")
bot.infinity_polling()
