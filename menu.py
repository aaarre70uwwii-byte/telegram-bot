from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_empty_menu():
    markup = InlineKeyboardMarkup(row_width=3)
    # الصف الاول 1 2 3
    markup.add(
        InlineKeyboardButton("🛡️ 1", callback_data="ignore"),
        InlineKeyboardButton("⚙️ 2", callback_data="ignore"),
        InlineKeyboardButton("🔧 3", callback_data="ignore")
    )
    # الصف الثاني 4 5 6
    markup.add(
        InlineKeyboardButton("📢 4", callback_data="ignore"),
        InlineKeyboardButton("🤖 5", callback_data="ignore"),
        InlineKeyboardButton("✨ 6", callback_data="ignore")
    )
    # الصف الثالث
    markup.add(
        InlineKeyboardButton("🔐 القفل والفتح", callback_data="ignore"),
        InlineKeyboardButton("📊 التفعيل والتعطيل", callback_data="ignore")
    )
    # الصف الرابع
    markup.add(
        InlineKeyboardButton("⬅️ اخفاء الاوامر", callback_data="close_menu")
    )
    return markup

def show_menu(bot, chat_id):
    text = """- أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━━━
◀️ 1م : اوامر الادمنيه
◀️ 2م : اوامر الاعدادات
◀️ 3م : اوامر القفل - الفتح
◀️ 4م : اوامر التسلية
◀️ 5م : اوامر Dev
◀️ 6م : الاوامر الخدميه
━━━━━━━━━━━━"""
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_empty_menu())

def register_handlers(bot):

    # لما يكتب الاوامر في قروب او قناة
    @bot.message_handler(func=lambda m: m.text and m.text.lower() == 'الاوامر', chat_types=['group','supergroup','channel'])
    def show_menu_text(m):
        show_menu(bot, m.chat.id)

    # عشان الازرار ما تعلق
    @bot.callback_query_handler(func=lambda call: True)
    def menu_callback(call):
        if call.data == "close_menu":
            try: 
                bot.delete_message(call.message.chat.id, call.message_id)
            except: pass
        else:
            # اي زر ثاني نسوي له ignore عشان ما يعلق
            bot.answer_callback_query(call.id, "هذي لوحة عرض فقط", show_alert=False)
