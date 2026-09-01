import os
import telebot
import menu
import m1
import m2
import m3
import m4
import m5

TOKEN = os.environ.get("TOKEN")  # <-- هذا اسم المتغير عندك في Railway
if not TOKEN:
    print("❌ خطأ: ما لقيت TOKEN في المتغيرات")
    exit()

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# تشغيل كل الاوامر
menu.register_all(bot)
m1.register_handlers(bot)
m2.register_handlers(bot)
m3.register_handlers(bot)
m4.register_handlers(bot)
m5.register_handlers(bot)

# ===== مهم للاذاعة: حفظ القروبات تلقائي =====
@bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'])
def save_group(m):
    from m5 import broadcast_status, save_dev_data
    chat_id = str(m.chat.id)
    if chat_id not in broadcast_status.get('groups', []):
        broadcast_status.setdefault('groups', []).append(chat_id)
        save_dev_data()

# ===== منع المحظورين عام =====
@bot.message_handler(func=lambda m: True, content_types=['text','photo','video','document','sticker','voice','audio'])
def check_gban(m):
    from m5 import gban_list
    if str(m.from_user.id) in gban_list:
        try:
            bot.delete_message(m.chat.id, m.message_id)
        except: pass

print("✅ البوت شغال 100%")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
