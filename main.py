import telebot
import os
import sys
import importlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import * # يقرأ الايدي والاسم من هنا
from utils.keyboards import *

BOT_TOKEN = os.getenv("BOT_TOKEN") # يقرأ التوكن من Railway

if BOT_TOKEN is None:
    print("❌ خطأ: ما لقى BOT_TOKEN في المتغيرات")
    sys.exit()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

cogs_list = ["menu", "locks"]

for cog in cogs_list:
    module = importlib.import_module(f"cogs.{cog}")
    if hasattr(module, "setup"):
        module.setup(bot, المطور_الاساسي, admins)
    print(f"✅ تم تحميل: {cog}.py")

print("="*50)
print(f"✅ بوت {اسم_البوت} شغال الان")
print(f"✅ المطور: {المطور_الاساسي}")
print("="*50)
bot.infinity_polling(none_stop=True, timeout=60)
