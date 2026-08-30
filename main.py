import os
import telebot
import main_menu
import m1  # اوامر الادمنيه
import m2  # اوامر الاعدادات  
import m3  # اوامر القفل
import m4  # اوامر التسليه
import m5  # اوامر Dev
import m6  # الاوامر الخدميه
import dev_panel  # لوحة المطور

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID") # <-- حط رقمك في Railway

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN غير موجود")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# نفعل لوحة المطور مرة وحدة عند التشغيل
dev_panel.register_handlers(bot, OWNER_ID)

# ========== اوامر القائمة ==========
@bot.message_handler(commands=['اوامر', 'start'])
def start(m):
    # القائمة للقروبات فقط
    if m.chat.type == 'private':
        return bot.send_message(m.chat.id, "⚠️ القائمة تشتغل في القروبات فقط\nاكتب /المطور في الخاص")
    main_menu.show_main_menu(bot, m, page=1)

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "الاوامر", chat_types=['group','supergroup'])
def show_menu_text(m):
    main_menu.show_main_menu(bot, m, page=1)

# ========== لوحة المطور ==========
@bot.message_handler(commands=['المطور'])
def dev_cmd(m):
    if m.chat.type == 'private' and str(m.from_user.id) == OWNER_ID:
        bot.send_message(m.chat.id, "لوحة المطور 👑", reply_markup=dev_panel.get_dev_keyboard())
    else:
        bot.send_message(m.chat.id, "❌ امر المطور للخاص فقط للمطور الاساسي")

# ========== هذا اهم شي عشان الازرار تشتغل ==========
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    main_menu.handle_callbacks(bot, c)

# ========== تشغيل البوت ==========
print("البوت Tia شغال...")
bot.infinity_polling(none_stop=True, interval=0)
