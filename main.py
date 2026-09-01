import telebot
import os
import menu
import m5  # استدعاء ملف المطور
import m6  # استدعاء ملف الخدمات

TOKEN = os.getenv("TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID", "0")) # لو فاضي ما يطيح

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
activated_groups = set()

def is_owner(user_id):
    return user_id == OWNER_ID

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() == "تفعيل", chat_types=['group','supergroup'])
def activate_group(m):
    if not is_owner(m.from_user.id):
        return bot.reply_to(m, "⛔ هذا الامر للمالك فقط")
    activated_groups.add(m.chat.id)
    bot.reply_to(m, "✅ تم تفعيل المجموعه بنجاح\nالان تقدر تستخدم /اوامر")

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() == "تعطيل", chat_types=['group','supergroup'])
def deactivate_group(m):
    if not is_owner(m.from_user.id):
        return bot.reply_to(m, "⛔ هذا الامر للمالك فقط")
    activated_groups.discard(m.chat.id)
    bot.reply_to(m, "❌ تم تعطيل المجموعه")

@bot.message_handler(func=lambda m: m.chat.id not in activated_groups and m.chat.type in ['group','supergroup'])
def not_activated(m):
    if m.text and m.text.lower().strip() in ['الاوامر', '/اوامر', '1م', '2م', '3م', '4م', '5م', '6م']:
        bot.reply_to(m, "⚠️ المجموعه غير مفعله\nالمالك لازم يكتب `تفعيل` اول")

# تفعيل كل الهاندلرات
menu.register_handlers(bot)
m5.register_m5_handlers(bot)
m6.register_m6_handlers(bot)

print("Bot is running...")
print(f"Owner ID: {OWNER_ID}")
bot.infinity_polling()
