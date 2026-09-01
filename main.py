import os
import threading
import telebot
from flask import Flask

# استدعاء ملف القائمة
import menu

# 1. قراءة المتغيرات من Railway
TOKEN = os.getenv("BOT_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_ID = os.getenv("OWNER_ID")

if not TOKEN:
    print("خطأ: BOT_TOKEN مش موجود")
    exit()

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# 2. سيرفر Flask عشان Railway ما يوقف البوت
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت شغال 24 ساعة ✅"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 3. اوامر اساسية للبوت
@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.type == 'private':
        bot.reply_to(m, f"اهلا {m.from_user.first_name}\nضيفني قروب واكتب الاوامر")

@bot.message_handler(commands=['owner'])
def owner(m):
    bot.reply_to(m, f"المطور: `{OWNER_ID}`")

# 4. امر التفعيل في القروبات
@bot.message_handler(func=lambda m: m.text and m.text == 'تفعيل', chat_types=['group','supergroup'])
def activate_group(m):
    bot.reply_to(m, "✅ تم التفعيل بنجاح")
    print(f"تم تفعيل القروب: {m.chat.title} - {m.chat.id}")

# 5. تشغيل هاندلرات القائمة من ملف menu.py
menu.register_handlers(bot)  # <-- كملت هذا

# 6. تشغيل البوت
def run_bot():
    print("البوت بدأ التشغيل...")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()  # <-- وكملت هذا
    run_bot()
