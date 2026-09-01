from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import menu

# ===== 1. قائمة القروب: ازرار انلاين =====
def show_dev_menu(bot, chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📢 اذاعة", callback_data="dev_broadcast"),
        InlineKeyboardButton("📊 احصائيات", callback_data="dev_stats"),
        InlineKeyboardButton("🧹 تنظيف", callback_data="dev_clean")
    )
    markup.add(
        InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    )
    bot.send_message(chat_id, "🔧 **اوامر المطور Dev**\nاختار الامر من الازرار:", reply_markup=markup, parse_mode="Markdown")

# ===== 2. كيبورد الخاص: كتابة =====
def show_dev_keyboard(bot, chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("📢 اذاعة"), KeyboardButton("📊 احصائيات"))
    markup.add(KeyboardButton("🧹 تنظيف"), KeyboardButton("🔙 رجوع"))
    bot.send_message(chat_id, "🔧 **لوحة المطور**\nاكتب الامر من الكيبورد:", reply_markup=markup, parse_mode="Markdown")

# ===== 3. تشغيل كل اوامر m5 =====
def register_handlers(bot):

    # --- اوامر الكيبورد حق الخاص ---
    @bot.message_handler(func=lambda m: m.text == "📢 اذاعة" and m.chat.type == 'private')
    def broadcast_text(m):
        bot.send_message(m.chat.id, "ارسل نص الاذاعة وبرسلها لكل القروبات")
    
    @bot.message_handler(func=lambda m: m.text == "📊 احصائيات" and m.chat.type == 'private')
    def stats_text(m):
        bot.send_message(m.chat.id, "جاري جلب الاحصائيات...")
    
    @bot.message_handler(func=lambda m: m.text == "🧹 تنظيف" and m.chat.type == 'private')
    def clean_text(m):
        bot.send_message(m.chat.id, "تم تنظيف ...")
    
    @bot.message_handler(func=lambda m: m.text == "🔙 رجوع" and m.chat.type == 'private')
    def back_text(m):
        menu.show_menu(bot, m.chat.id)

    # --- اوامر الازرار حق القروب ---
    @bot.callback_query_handler(func=lambda call: call.data == "dev_broadcast")
    def cb_broadcast(call):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "ارسل نص الاذاعة")

    @bot.callback_query_handler(func=lambda call: call.data == "dev_stats")
    def cb_stats(call):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "احصائيات البوت: ...")

    @bot.callback_query_handler(func=lambda call: call.data == "dev_clean")
    def cb_clean(call):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "تم التنظيف")
