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
        text = """<b>◄ أهلاً بك عزي في قائمة الاوامر ►</b>
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
            types.InlineKeyboardButton("التالي »", callback_data="page_2")
        )
    
    elif page == 2:
        text = """<b>◄ أهلاً بك عزي في قائمة الاوامر ►</b>
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
            types.InlineKeyboardButton("« السابق", callback_data="page_1")
        )
    
    keyboard.add(types.InlineKeyboardButton("❌ اخفاء الاوامر", callback_data="hide"))

    if edit:
        bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode="HTML")

def handle_callbacks(bot, call):
    bot.answer_callback_query(call.id)
    
    if call.data == "page_2":
        show_main_menu(bot, call.message, page=2, edit=True)
        
    elif call.data == "page_1":
        show_main_menu(bot, call.message, page=1, edit=True)
        
    elif call.data.startswith("m"):
        pages = {
            "m1": "✅ <b>قائمة اوامر الادمنيه</b>\nاستخدمها بالرد على العضو:\nرفع - تنزيل - حظر - طرد - كتم\nمسح 10 - رتبتي - تنزيل الكل",
            "m2": "✅ <b>قائمة اوامر الاعدادات</b>\nاهم الاوامر:\nالاعدادات - الرابط - معلوماتي - المجموعه\nضع الترحيب - ضع قوانين - انشاء رابط\nهمس @username النص",
            "m3": "✅ <b>قائمة اوامر القفل - الفتح</b>\nارسل: الحماية\nلرؤية كل اوامر القفل",
            "m4": "✅ <b>قائمة اوامر التسليه</b>\nارسل: التسلية\nلرؤية كل الاوامر",
            "m5": "✅ <b>قائمة اوامر Dev</b>\nارسل: المطور2\nلعرض قائمة المطور",
            "m6": "✅ <b>قائمة الاوامر الخدميه</b>\nارسل: الخدميه\nلعرض كل الاوامر"
        }
        bot.edit_message_text(pages[call.data], call.message.chat.id, call.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("« رجوع", callback_data="main")), parse_mode="HTML")
        
    elif call.data == "hide":
        bot.delete_message(call.message.chat.id, call.message_id)
    elif call.data == "main":
        show_main_menu(bot, call.message, page=1, edit=True)
