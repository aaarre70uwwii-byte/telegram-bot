from telebot import types
import m1  # <-- اوامر الادمنيه
import m2  # <-- اوامر الاعدادات
import m3  # <-- اوامر القفل
import m4  # <-- اوامر التسليه
import m5  # <-- اوامر المطور
import m6  # <-- الاوامر الخدميه

def show_main_menu(bot, message, page=1, edit=False):
    """تظهر القائمة بصفحات"""
    
    if page == 1:
        نص = """- أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━
م1 : اوامر الادمنيه ◀
م2 : اوامر الاعدادات ◀
م3 : اوامر القفل - الفتح ◀
━━━━━━━━━━
الصفحة 1/2
💛 تحديثات : Tia 💛"""
        
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            types.InlineKeyboardButton("1", callback_data="m1"),
            types.InlineKeyboardButton("2", callback_data="m2"),
            types.InlineKeyboardButton("3", callback_data="m3")
        )
        keyboard.add(
            types.InlineKeyboardButton("التالي »", callback_data="page_2"),
            types.InlineKeyboardButton("القائمه الرئيسيه", callback_data="main")
        )
    
    elif page == 2:
        نص = """- أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━
م4 : اوامر التسليه ◀
م5 : اوامر Dev ◀
م6 : الاوامر الخدميه ◀
━━━━━━━━━━
الصفحة 2/2
💛 تحديثات : Tia 💛"""
        
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            types.InlineKeyboardButton("4", callback_data="m4"),
            types.InlineKeyboardButton("5", callback_data="m5"),
            types.InlineKeyboardButton("6", callback_data="m6")
        )
        keyboard.add(
            types.InlineKeyboardButton("« السابق", callback_data="page_1"),
            types.InlineKeyboardButton("القائمه الرئيسيه", callback_data="main")
        )
    
    keyboard.add(types.InlineKeyboardButton("اخفاء الاوامر", callback_data="hide"))

    if edit:
        bot.edit_message_text(نص, message.chat.id, message.message_id, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, نص, reply_markup=keyboard)

def handle_callbacks(bot, call):
    bot.answer_callback_query(call.id)
    
    if call.data == "page_2":
        show_main_menu(bot, call.message, page=2, edit=True)
        
    elif call.data == "page_1":
        show_main_menu(bot, call.message, page=1, edit=True)
        
    elif call.data == "main":
        show_main_menu(bot, call.message, page=1, edit=True)
        
    elif call.data == "m1":
        نص = """✅ قائمة اوامر الادمنيه
استخدمها بالرد على العضو:
رفع - تنزيل - حظر - طرد - كتم
مسح 10 - رتبتي - تنزيل الكل"""
        bot.edit_message_text(نص, call.message.chat.id, call.message_id)
        
    elif call.data == "m2":
        نص = """✅ قائمة اوامر الاعدادات
اهم الاوامر:
الاعدادات - الرابط - معلوماتي - المجموعه
ضع الترحيب - ضع قوانين - انشاء رابط
همس @username النص"""
        bot.edit_message_text(نص, call.message.chat.id, call.message_id)

    elif call.data == "m3":
        نص = """✅ قائمة اوامر القفل - الفتح
ارسل: الحماية
لرؤية كل اوامر القفل"""
        bot.edit_message_text(نص, call.message.chat.id, call.message_id)

    elif call.data == "m4":
        نص = """✅ قائمة اوامر التسليه
ارسل: التسلية
لرؤية كل الاوامر"""
        bot.edit_message_text(نص, call.message.chat.id, call.message_id)
        
    elif call.data == "m5":
        نص = """✅ قائمة اوامر Dev
ارسل: المطور2
لعرض قائمة المطور"""
        bot.edit_message_text(نص, call.message.chat.id, call.message_id)
        
    elif call.data == "m6":
        نص = """✅ قائمة الاوامر الخدميه
ارسل: الخدميه
لعرض كل الاوامر"""
        bot.edit_message_text(نص, call.message.chat.id, call.message_id)
        
    elif call.data == "hide":
        bot.delete_message(call.message.chat.id, call.message_id)
