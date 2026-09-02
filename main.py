# main.py
import os
import telebot
import time
import json

# استدعاء كل الملفات
from menu import register_menu_handlers
from m1 import register_m1_handlers
from m2 import register_m2_handlers
from m3 import register_m3_handlers, set_feature
from m4 import register_m4_handlers # 1. اضفنا m4

TOKEN = os.environ.get("TOKEN")  # حط التوكن في Railway Variables

if not TOKEN:
    print("❌ خطأ: ضع التوكن في متغير TOKEN")
    exit()

bot = telebot.TeleBot(TOKEN, parse_mode="HTML", num_threads=4)
bot.delete_webhook(drop_pending_updates=True)

# امر التفعيل للجروبات
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'] and m.text == "تفعيل")
def activate_group(m):
    chat_id = m.chat.id
    try:
        member = bot.get_chat_member(chat_id, m.from_user.id)
        if member.status in ['creator', 'administrator']:
            set_feature(chat_id, "مفعلة", True)
            bot.send_message(chat_id, "✅ تم تفعيل المجموعة بنجاح\nالان تقدر تستخدم اوامر البوت")
        else:
            bot.send_message(chat_id, "❌ هذا الامر للادمنيه فقط")
    except:
        pass

# تسجيل كل الهاندلرز - الترتيب مهم
print("جاري تشغيل البوت...")
register_menu_handlers(bot)  # 1. القائمة الاساسية
register_m1_handlers(bot)    # 2. اوامر الادمنية
register_m2_handlers(bot)    # 3. اوامر الاعدادات  
register_m3_handlers(bot)    # 4. اوامر القفل
register_m4_handlers(bot)    # 5. اوامر التسليه m4 # 2. سجلنا m4

print("✅ البوت شغال 100%")
print("✅ تم اضافة امر التفعيل")
print("✅ تم اضافة اوامر التسليه m4") # 3. رسالة تاكيد

while True:
    try:
        bot.infinity_polling(skip_pending=True, non_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ خطأ: {e}")
        time.sleep(5)
