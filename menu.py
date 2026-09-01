from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import m1
import m2
import m3
import m4
import m5
import m6

# دالة جديدة عشان نشغل اوامر كل الملفات
def register_all(bot):
    m1.register_handlers(bot)
    m2.register_handlers(bot)
    m3.register_handlers(bot)
    m4.register_handlers(bot)
    m5.register_handlers(bot)
    m6.register_handlers(bot)

def get_empty_menu():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("🛡️ 1", callback_data="menu_1"),
        InlineKeyboardButton("⚙️ 2", callback_data="menu_2"),
        InlineKeyboardButton("🔧 3", callback_data="menu_3")
    )
    markup.add(
        InlineKeyboardButton("📊 4", callback_data="menu_4"),
        InlineKeyboardButton("🤖 5", callback_data="menu_5"),
        InlineKeyboardButton("✨ 6", callback_data="menu_6")
    )
    markup.add(
        InlineKeyboardButton("🔐 القفل والفتح", callback_data="menu_lock"),
        InlineKeyboardButton("📊 التفعيل والتعطيل", callback_data="menu_active")
    )
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
        if m.chat.type == 'private':
            m5.show_dev_keyboard(bot, m.chat.id) # كيبورد للخاص
        else:
            m5.show_dev_menu(bot, m.chat.id) # قائمة للقروب
    @bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['6م', '6', '/6'])
    def cmd_6(m): m6.show_service_menu(bot, m.chat.id)

    @bot.callback_query_handler(func=lambda call: True)
