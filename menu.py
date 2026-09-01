from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import m1
import m2
import m3
import m4

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
        InlineKeyboardButton("🤖 5", callback_data="ignore"),
        InlineKeyboardButton("✨ 6", callback_data="ignore")
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

    # 1. لما يكتب الاوامر في قروب او قناة او خاص
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['الاوامر', '/اوامر', 'اوامر'], content_types=['text'])
    def show_menu_text(m):
        show_menu(bot, m.chat.id)

    # 2. اوامر الكتابة 1م 2م 3م 4م
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['1م', '1', '/1'])
    def cmd_1(m): m1.show_admin_menu(bot, m.chat.id)
    
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['2م', '2', '/2'])
    def cmd_2(m): m2.show_settings_menu(bot, m.chat.id)
    
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['3م', '3', '/3'])
    def cmd_3(m): m3.show_lock_menu(bot, m.chat.id)
    
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['4م', '4', '/4'])
    def cmd_4(m): m4.show_fun_menu(bot, m.chat.id)

    # 3. /start في الخاص
    @bot.message_handler(commands=['start'])
    def start_private(m):
        if m.chat.type == 'private':
            show_menu(bot, m.chat.id)

    # 4. هاندلر الازرار - مستحيل يعلق
    @bot.callback_query_handler(func=lambda call: True)
    def menu_callback(call):
        chat_id = call.message.chat.id
        message_id = call.message_id

        bot.answer_callback_query(call.id) # يشيل التحميل فورا

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
                
            elif call.data == "ignore":
                bot.answer_callback_query(call.id, "قريبا", show_alert=True)
        except:
            pass # لو انحذفت الرسالة خلاص
