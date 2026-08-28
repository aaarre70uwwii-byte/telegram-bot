from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

MAIN_MENU_TEXT = """- ‌‌‏أهلاً بك عزيزي في قائمة الاوامر :
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه 
━━━━━━━━━━━━"""

PAGES_TEXT = {
    "1": "◂ **اوامر الادمنيه:**\n\nهنا تضع أوامر الإدارة (طرد، حظر، كتم...)",
    "2": "◂ **اوامر الاعدادات:**\n\nهنا تضع أوامر إعدادات المجموعة أو البوت",
    "3": "◂ **اوامر القفل - الفتح:**\n\nهنا تضع أوامر قفل وفتح الميديا، الروابط الخ...",
    "4": "◂ **اوامر التسليه:**\n\nهنا تضع ألعاب وأوامر التسلية والترفيه",
    "5": "◂ **اوامر Dev:**\n\nأوامر خاصة بمطور البوت فقط وموجودة بملف المطور",
    "6": "◂ **الاوامر الخدميه:**\n\nهنا تضع الأوامر العامة والخدمية للمستخدمين"
}

def create_keyboard(current_page=None):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("1", callback_data="page_1")
    btn2 = InlineKeyboardButton("2", callback_data="page_2")
    btn3 = InlineKeyboardButton("3", callback_data="page_3")
    btn4 = InlineKeyboardButton("4", callback_data="page_4")
    btn5 = InlineKeyboardButton("5", callback_data="page_5")
    btn6 = InlineKeyboardButton("6", callback_data="page_6")
    
    markup.row(btn1)
    markup.row(btn2, btn3, btn4, btn5, btn6)
    
    if current_page:
        try:
            current_num = int(current_page)
            prev_num = 6 if current_num == 1 else current_num - 1
            next_num = 1 if current_num == 6 else current_num + 1
            
            btn_prev = InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{prev_num}")
            btn_main = InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")
            btn_next = InlineKeyboardButton("التالي ➡️", callback_data=f"page_{next_num}")
            markup.row(btn_prev, btn_main, btn_next)
        except ValueError:
            pass
            
    btn_channel = InlineKeyboardButton("تحديثات 𝐓𝐢𝐚", url="https://t.me")
    markup.row(btn_channel)
    
    btn_empty1 = InlineKeyboardButton(" 🔘 ", callback_data="empty")
    btn_empty2 = InlineKeyboardButton(" 🔘 ", callback_data="empty")
    markup.row(btn_empty1, btn_empty2)
    return markup

def register_handlers(bot):
    
    @bot.message_handler(func=lambda message: message.text == "الاوامر" and message.chat.type in ["group", "supergroup"])
    def send_commands_group(message):
        bot.reply_to(message, MAIN_MENU_TEXT, reply_markup=create_keyboard(), parse_mode="Markdown")

    @bot.channel_post_handler(func=lambda message: message.text == "الاوامر")
    def send_commands_channel(message):
        bot.send_message(message.chat.id, MAIN_MENU_TEXT, reply_markup=create_keyboard(), parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text == "تفعيل")
    @bot.channel_post_handler(func=lambda message: message.text == "تفعيل")
    def activate_cmd(message):
        try: bot.reply_to(message, "تم تفعيل بنجاح")
        except Exception:
            try: bot.send_message(message.chat.id, "تم تفعيل بنجاح")
            except Exception: pass

    @bot.message_handler(func=lambda message: message.text == "اخفاء الاوامر")
    @bot.channel_post_handler(func=lambda message: message.text == "اخفاء الاوامر")
    def hide_commands(message):
        try:
            if message.reply_to_message:
                bot.delete_message(message.chat.id, message.reply_to_message.message_id)
            bot.delete_message(message.chat.id, message.message_id)
        except Exception: pass

    @bot.callback_query_handler(func=lambda call: call.data in ["main_menu", "empty"] or call.data.startswith("page_"))
    def callback_listener(call):
        try:
            if call.data == "main_menu":
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                      text=MAIN_MENU_TEXT, reply_markup=create_keyboard(), parse_mode="Markdown")
                bot.answer_callback_query(call.id)
            elif call.data.startswith("page_"):
                # تم التصحيح: استخراج الرقم الفعلي عبر إضافة [1] ليعود بنص مثل "1" أو "5"
                page_num = call.data.split("_")[1]
                page_text = PAGES_TEXT.get(page_num, "قسم فارغ")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                      text=page_text, reply_markup=create_keyboard(current_page=page_num), parse_mode="Markdown")
                bot.answer_callback_query(call.id)
            elif call.data == "empty":
                bot.answer_callback_query(call.id, text="هذا الزر فارغ مخصص للتصميم فقط!", show_alert=False)
        except Exception as e:
            print(f"Error in main_menu callback: {e}")
