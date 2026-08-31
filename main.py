import telebot
import os
import threading
from flask import Flask

# استدعاء كل ملفات البوت
import m1  # الادمنيه
import m2  # الاعدادات 
import m3  # الحماية
import m4  # التسليه
import menu # القائمة

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("لازم تحط التوكن في BOT_TOKEN في Railway")

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
active_groups = set() # القروبات المفعله

app = Flask('')

@app.route('/')
def home():
    return "البوت شغال 24 ساعه ✅"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ===== اوامر التفعيل العامة =====
@bot.message_handler(content_types=['text'], chat_types=['group','supergroup'])
def activate_group(m):
    global active_groups
    chat_id = m.chat.id
    text = m.text.strip()
    
    if text == "تفعيل":
        active_groups.add(chat_id)
        bot.reply_to(m, "✅ تم تفعيل البوت في القروب\nاكتب `الاوامر` عشان تشوف كل الاوامر")
    
    elif text == "تعطيل":
        if chat_id in active_groups: 
            active_groups.remove(chat_id)
        bot.reply_to(m, "❌ تم تعطيل البوت في القروب")

# ===== تسجيل كل الهاندلرات من الملفات =====
m1.register_admin_handlers(bot, active_groups)
m2.register_settings_handlers(bot, active_groups)
m3.register_lock_handlers(bot, active_groups)
m4.register_fun_handlers(bot, active_groups)
menu.register_menu_handler(bot, active_groups)

print("البوت اشتغل بنجاح...")

if __name__ == "__main__":
    # نشغل السيرفر الوهمي عشان Railway ما يطفيه
    threading.Thread(target=run_flask).start()
    # نشغل البوت
    bot.infinity_polling(none_stop=True, timeout=60)
