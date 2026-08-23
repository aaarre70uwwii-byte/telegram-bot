import telebot
import os
import sys
import importlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import * # يقرأ التوكن والايدي من هنا
from utils.keyboards import *

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ========== استدعاء كل ملفات cogs تلقائي ==========
cogs_list = ["menu", "locks"] # ضيف اسم اي ملف جديد هنا

for cog in cogs_list:
    module = importlib.import_module(f"cogs.{cog}")
    if hasattr(module, "setup"):
        module.setup(bot, المطور_الاساسي, admins)
    print(f"✅ تم تحميل: {cog}.py")

# ========== تشغيل البوت ==========
print("="*50)
print(f"✅ بوت {اسم_البوت} شغال الان")
print(f"✅ المطور: {المطور_الاساسي}")
print("="*50)

bot.infinity_polling(none_stop=True, timeout=60)
