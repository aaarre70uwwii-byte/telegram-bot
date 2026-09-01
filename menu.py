from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import m1
import m2
import m3
import m4
import m5  # استدعاء ملف المطور
import m6  # استدعاء ملف الخدمات

def get_empty_menu():
    markup = InlineKeyboardMarkup(row_width=3)
    # الصف الاول 1 2 3
    markup.add(
        InlineKeyboardButton("🛡️ 1", callback_data="menu_1"),
        InlineKeyboardButton("⚙️ 2", callback_data="menu_2"),
        InlineKeyboardButton("🔧 3", callback_data="menu_3")
    )
    # الصف الثاني 4 5 6
    markup.add(
        InlineKeyboardButton("📊 4", callback_data="menu_4"),
        InlineKeyboardButton("🤖 5", callback_data="menu_5"),
        InlineKeyboardButton("✨ 6", callback_data="menu_6")
    )
    # الصف الثالث
    markup.add(
        InlineKeyboardButton("🔐 القفل والفتح", callback_data="menu_3"),
        InlineKeyboardButton("📊 التفعيل والتعطيل", callback_data="menu_4")
    )
    # الصف الرابع
    markup.add(
        InlineKeyboardButton("❌ اخفاء الاوامر", callback_data="close_menu")
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
━━━━━━━━━━━━
ارسل رقم الامر او اضغط الزر 👇"""
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_empty_menu())

def register_handlers(bot):

    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['الاوامر', '/اوامر', 'اوامر'], content_types=['text'])
    def show_menu_text(m):
        show_menu(bot, m.chat.id)

    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['1م', '1', '/1'])
    def cmd_1(m): m1.show_admin_menu(bot, m.chat.id)
    
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['2م', '2', '/2'])
    def cmd_2(m): m2.show_settings_menu(bot, m.chat.id)
    
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['3م', '3', '/3'])
    def cmd_3(m): m3.show_lock_menu(bot, m.chat.id)
    
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['4م', '4', '/4'])
    def cmd_4(m): m4.show_fun_menu(bot, m.chat.id)

    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['5م', '5', '/5'])
    def cmd_5(m): 
        if m5.is_dev(m.from_user.id):
            m5.show_dev_menu(bot, m.chat.id)
        else:
            bot.reply_to(m, "❌ هذا الامر للمطور فقط")

    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['6م', '6', '/6'])
    def cmd_6(m): m6.show_service_menu(bot, m.chat.id)

    @bot.message_handler(commands=['start'])
    def start_private(m):
        if m.chat.type == 'private':
            show_menu(bot, m.chat.id)

    @bot.callback_query_handler(func=lambda call: True)
    def menu_callback(call):
        chat_id = call.message.chat.id
        message_id = call.message_id

        bot.answer_callback_query(call.id) # هنا كان ناقص

        try:
            if call.data == "close_menu":
                bot.delete_message(chat_id, message_id)

            elif call.data == "back_to_main":
                bot.delete_message(chat_id, message_id)
                show_menu(bot, chat_id)

            elif call.data == "menu_1":
                bot.delete_message(chat_id, message_id)
                m1.show_admin_menu(bot, chat_id)

            elif call.data == "menu_2":
                bot.delete_message(chat_id, message_id)
                m2.show_settings_menu(bot, chat_id)

            elif call.data == "menu_3":
                bot.delete_message(chat_id, message_id)
                m3.show_lock_menu(bot, chat_id)

            elif call.data == "menu_4":
                bot.delete_message(chat_id, message_id)
                m4.show_fun_menu(bot, chat_id)
            
            elif call.data == "menu_5":
                bot.delete_message(chat_id, message_id)
                if m5.is_dev(call.from_user.id):
                    m5.show_dev_menu(bot, chat_id)
                else:
                    bot.answer_callback_query(call.id, "هذا للمطور فقط", show_alert=True)

            elif call.data == "menu_6":
                bot.delete_message(chat_id, message_id)
                m6.show_service_menu(bot, chat_id)
                
        except:
            pass # لو انحذفت الرسالة
