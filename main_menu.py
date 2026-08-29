from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_main_menu(page=1):
    markup = InlineKeyboardMarkup(row_width=3)
    
    if page == 1:
        text = """- ‌‌‏أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات  
◂ م3 : اوامر القفل - الفتح
━━━━━━━━━━━━"""
        markup.row(
            InlineKeyboardButton("م1 الادمن", callback_data="exec_m1"),
            InlineKeyboardButton("م2 الاعدادات", callback_data="exec_m2"),
            InlineKeyboardButton("م3 الحماية", callback_data="exec_m3"),
        )
    
    elif page == 2:
        text = """- ‌‌‏أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━━━
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه
━━━━━━━━━━━━"""
        markup.row(
            InlineKeyboardButton("م4 التسلية", callback_data="exec_m4"),
            InlineKeyboardButton("م5 المطور", callback_data="exec_m5"),
            InlineKeyboardButton("م6 الخدمية", callback_data="exec_m6"),
        )

    nav = []
    if page == 2: 
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data="page_1"))
    if page == 1: 
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data="page_2"))
    nav.append(InlineKeyboardButton("🗑️ اخفاء", callback_data="hide"))
    markup.row(*nav)
    
    return text, markup

def register_menu_handlers(bot):

    @bot.message_handler(commands=['menu', 'القائمه', 'الاوامر'])
    def show_menu(m):
        text, markup = create_main_menu(1)
        bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: True)
    def menu_callback(call):
        try:
            chat_id = call.message.chat.id
            msg_id = call.message.message_id
            data = call.data

            # ===== التنقل =====
            if data == "page_1":
                text, markup = create_main_menu(1)
                bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")
            
            elif data == "page_2":
                text, markup = create_main_menu(2)
                bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")
            
            # ===== الاخفاء =====
            elif data == "hide":
                bot.delete_message(chat_id, msg_id)

            # ===== استدعاء الملفات مباشرة =====
            elif data == "exec_m1":
                import m1
                m1.register_admin_handlers(bot)
                m1.admin_menu(bot, call.message)
                
            elif data == "exec_m2":
                import m2
                m2.register_settings_handlers(bot)
                m2.settings_menu(bot, call.message)
                
            elif data == "exec_m3":
                import m3
                m3.register_lock_handlers(bot)
                m3.lock_menu(bot, call.message)
                
            elif data == "exec_m4":
                import m4
                m4.register_fun_handlers(bot)
                m4.fun_menu(bot, call.message)
                
            elif data == "exec_m5": # << كود المطور المعدل
                import dev_commands as m5
                m5.register_handlers(bot) # سجل الهاندلر
                bot.send_message(chat_id, "⚙️ اهلا بك في لوحة تحكم المطور", reply_markup=m5.get_dev_keyboard())
                
            elif data == "exec_m6":
                import service_commands as m6
                m6.register_service_handlers(bot)
                m6.service_menu(bot, call.message)
            
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"خطأ في القائمة: {e}")
            bot.answer_callback_query(call.id, "حدث خطأ")
