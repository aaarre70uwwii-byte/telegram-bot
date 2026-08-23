import telebot
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.keyboards import *
from cogs import menu, locks

# ========== قراءة المتغيرات ==========
TOKEN = os.getenv("TOKEN") 
if not TOKEN:
    raise ValueError("خطأ: التوكن TOKEN مش موجود في المتغيرات")

المطور_الاساسي = int(os.getenv("DEVELOPER_ID", "7488375443"))
admins = [المطور_الاساسي]

# ========== تشغيل البوت ==========
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# استدعاء كل الملفات وتمرير المتغيرات
menu.setup_menu(bot, المطور_الاساسي, admins)
locks.setup_locks(bot)

print("="*50)
print(f"✅ بوت 𝐓𝐢𝐚 شغال")
print(f"✅ المطور: {المطور_الاساسي}")
print("="*50)

bot.infinity_polling(none_stop=True, timeout=60)
