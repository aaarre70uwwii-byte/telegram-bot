import os
import telebot
import menu
import m1
import m2

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# تسجيل كل الملفات
menu.register(bot)
m1.register_admin_handlers(bot, menu.active_groups)
m2.register_settings_handlers(bot, menu.active_groups)

print("✅ البوت Tia شغال...")
bot.remove_webhook()
bot.infinity_polling(none_stop=True, interval=0, timeout=20)
