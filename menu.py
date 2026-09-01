from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import m1
import m2
import m3
import m4

def show_menu(bot, chat_id):
    text = """• اهلا بك عزي
انا بوت حماية وتسلية متكامل
اختر القائمة اللي تريدها 👇"""
    markup = get_empty_menu()
    bot.send_message(chat_id, text, reply_markup=markup)

def get_empty_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛡️ 1", callback_data="menu_1"),
        InlineKeyboardButton("⚙️ 2", callback_data="menu_2")
    )
    markup.add(
        InlineKeyboardButton("🔧 3", callback_data="menu_3"),
        InlineKeyboardButton("📊 4", callback_data="menu_4")
    )
    markup.add(InlineKeyboardButton("❌ اخفاء الاوامر", callback_data="close_menu"))
    return markup

def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: True)
    def menu_callback(call):
        chat_id = call.message.chat.id
        message_id = call.message_id  # <-- صلحتها هنا

        bot.answer_callback_query(call.id) # يشيل التحميل

        if call.data == "close_menu":
            try: bot.delete_message(chat_id, message_id)
            except: pass

        elif call.data == "back_to_main":
            try: bot.delete_message(chat_id, message_id)
            except: pass
            show_menu(bot, chat_id)

        elif call.data == "menu_1":
            try: bot.delete_message(chat_id, message_id)
            except: pass
            m1.show_admin_menu(bot, chat_id)

        elif call.data == "menu_2":
            try: bot.delete_message(chat_id, message_id)
            except: pass
            m2.show_settings_menu(bot, chat_id)

        elif call.data == "menu_3":
            try: bot.delete_message(chat_id, message_id)
            except: pass
            m3.show_lock_menu(bot, chat_id)

        elif call.data == "menu_4":
            try: bot.delete_message(chat_id, message_id)
            except: pass
            m4.show_fun_menu(bot, chat_id)
