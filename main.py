import telebot
import os
import config
import importlib

# فحص التوكن قبل التشغيل
if not config.BOT_TOKEN:
    print("❌ خطا: BOT_TOKEN فاضي. روح Railway Variables وحطه")
    exit()

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="Markdown")

# ========== استدعاء تلقائي لكل ملفات cog1 الى cog6 ==========
print("🔄 جاري تحميل ملفات الحماية...")
for i in range(1, 7):
    try:
        cog_module = importlib.import_module(f"cogs.cog{i}")
        cog_module.setup(bot, config.المطور_الاساسي, config.admins)
        print(f"✅ تم تحميل: cog{i}.py")
    except Exception as e:
        print(f"⚠️ لم يتم تحميل cog{i}.py : {e}")

# ========== تشغيل ملف القائمة والكيبورد ==========
from cogs.menu import setup as menu_setup
menu_setup(bot, config.المطور_الاساسي, config.admins)
print("✅ تم تحميل: menu.py - لوحة المطور")

print(f"-----------------------------------")
print(f"✅ بوت {config.اسم_البوت} الان شغال 100%")
print(f"✅ المطور: {config.المطور_الاساسي}")
print(f"-----------------------------------")

# تشغيل البوت
bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=60)
