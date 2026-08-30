import os
import telebot
import main_menu
import m1
import m2
import m3
import m4
import m5
import m6
import dev_panel

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN غير موجود")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# نفعل الكل
dev_panel.register_handlers(bot, OWNER_ID)
m1.register_admin_handlers(bot)
m2.register_settings_handlers(bot)
m3.register_lock_handlers(bot)
m4.register_fun_handlers(bot)
m5.register_handlers(bot)
m6.register_service_handlers(bot)

# ========== 1. قائمة الاوامر للقروبات فقط ==========
@bot.message_handler(commands=['اوامر', 'start'])
def start(m):
    if m.chat.type == 'private': # لو خاص ارفض
        return bot.send_message(m.chat.id, "⚠️ القائمة تشتغل في القروبات فقط\nاكتب /المطور في الخاص")
    main_menu.show_main_menu(bot, m, page=1) # لو قروب افتح القائمة

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "الاوامر", chat_types=['group','supergroup'])
def show_menu_text(m):
    main_menu.show_main_menu(bot, m, page=1)

# ========== 2. كيبورد المطور للخاص فقط ==========
@bot.message_handler(commands=['المطور'])
def dev_cmd(m):
    if m.chat.type == 'private' and str(m.from_user.id) == OWNER_ID: # خاص + انت
        bot.send_message(m.chat.id, "لوحة المطور 👑", reply_markup=dev_panel.get_dev_keyboard())
    else:
        bot.send_message(m.chat.id, "❌ امر المطور للخاص فقط للمطور الاساسي")

# ========== الازرار حق القائمة ==========
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    main_menu.handle_callbacks(bot, c)

# ========== تشغيل البوت ==========
print("✅ البوت Tia شغال...")
bot.infinity_polling(none_stop=True, interval=0)
