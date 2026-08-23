from telebot import types

def لوحة_الاوامر_الرئيسية():
    """القائمة الرئيسية اللي بتظهر في القروبات والقنوات فقط"""
    markup = types.InlineKeyboardMarkup(row_width=5)
    
    # الصف الاول: زر 1
    markup.add(
        types.InlineKeyboardButton("1", callback_data="menu_1")
    )
    
    # الصف الثاني: 2 3 4 5 6
    markup.add(
        types.InlineKeyboardButton("2", callback_data="menu_2"),
        types.InlineKeyboardButton("3", callback_data="menu_3"),
        types.InlineKeyboardButton("4", callback_data="menu_4"),
        types.InlineKeyboardButton("5", callback_data="menu_5"),
        types.InlineKeyboardButton("6", callback_data="menu_6")
    )
    
    # الصف الثالث: القفل والفتح + التفعيل والتعطيل
    markup.add(
        types.InlineKeyboardButton("🔒 القفل والفتح", callback_data="menu_locks"),
        types.InlineKeyboardButton("🟢 التفعيل والتعطيل", callback_data="menu_toggle")
    )
    
    # الصف الرابع: تحديثات
    markup.add(
        types.InlineKeyboardButton("تحديثات 𝐓𝐢𝐚 ; @eeccvu", url="https://t.me/eeccvu")
    )
    
    return markup
