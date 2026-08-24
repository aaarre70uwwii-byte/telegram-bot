import telebot
import os
import config
import importlib

# فحص التوكن
if not config.BOT_TOKEN:
    print("❌ خطا: BOT_TOKEN فاضي. روح Railway Variables وحطه")
    exit()

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="Markdown")

# تحميل cog1 الى cog6 تلقائي
print("🔄 جاري تحميل ملفات الحماية...")
for i in range(1, 7):
    try:
        cog_module = importlib.import_module(f"cogs.cog{i}")
        cog_module.setup(bot, config.المطور_الاساسي, config.admins)
        print(f"✅ تم تحميل: cog{i}.py")
    except Exception as e:
        print(f"⚠️ لم يتم تحميل cog{i}.py : {e}")

# تحميل القائمة
from cogs.menu import setup_menu
setup_menu(bot)

print(f"-----------------------------------")
print(f"✅ بوت {config.اسم_البوت} الان شغال 100%")
print(f"✅ المطور: {config.المطور_الاساسي}")
print(f"-----------------------------------")

bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=60)
