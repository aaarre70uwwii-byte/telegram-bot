from telebot import types

def لوحة_الاوامر_الرئيسية():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    
    btn1 = types.KeyboardButton("1")
    btn2 = types.KeyboardButton("2")
    btn3 = types.KeyboardButton("3")
    btn4 = types.KeyboardButton("4")
    btn5 = types.KeyboardButton("5")
    btn6 = types.KeyboardButton("6")
    
    btn_lock = types.KeyboardButton("🔒 القفل والفتح")
    btn_set = types.KeyboardButton("⚙️ التفعيل والتعطيل")
    btn_update = types.KeyboardButton("🦋 تحديثات البوت")
    
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    markup.add(btn_lock, btn_set)
    markup.add(btn_update)
    
    return markup


def لوحة_م1():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("حظر", "طرد")
    markup.add("كتم", "الغاء كتم")
    markup.add("مسح", "معلومات")
    markup.add("رجوع")
    return markup


def لوحة_م2():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("تفعيل الردود", "تعطيل الردود")
    markup.add("تفعيل الترحيب", "تعطيل الترحيب")
    markup.add("رجوع")
    return markup


def لوحة_م3():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("قفل الروابط", "فتح الروابط")
    markup.add("قفل الصور", "فتح الصور")
    markup.add("قفل الكلايش", "فتح الكلايش")
    markup.add("رجوع")
    return markup


def لوحة_م4():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("رفع هطف", "تنزيل هطف")
    markup.add("زواج", "طلاق")
    markup.add("اكتموه")
    markup.add("رجوع")
    return markup


def لوحة_م5():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("حظر عام", "الغاء حظر عام")
    markup.add("ذيع", "الردود العامة")
    markup.add("اعادة تشغيل")
    markup.add("رجوع")
    return markup


def لوحة_م6():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("نسبه الحب", "تحبه")
    markup.add("قوقل", "ترجم عربي")
    markup.add("قران", "اذكار")
    markup.add("رجوع")
    return markup
