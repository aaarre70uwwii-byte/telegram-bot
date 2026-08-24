from telebot import types

# ========== لوحة الاوامر الرئيسية ==========
def لوحة_الاوامر_الرئيسية():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("1", "2", "3")
    markup.add("4", "5", "6")
    markup.add("🔒 القفل والفتح", "⚙️ التفعيل والتعطيل")
    markup.add("🦋 تحديثات البوت")
    return markup

# ========== لوحات الاقسام ==========
def لوحة_م1(): # الادمنية
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("حظر", "طرد")
    markup.add("كتم", "الغاء كتم")
    markup.add("مسح", "معلومات")
    markup.add("رجوع")
    return markup

def لوحة_م2(): # الاعدادات
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("تفعيل الردود", "تعطيل الردود")
    markup.add("تفعيل الترحيب", "تعطيل الترحيب")
    markup.add("رجوع")
    return markup

def لوحة_م3(): # القفل
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("قفل الروابط", "فتح الروابط")
    markup.add("قفل الصور", "فتح الصور")
    markup.add("قفل الكلايش", "فتح الكلايش")
    markup.add("رجوع")
    return markup

def لوحة_م4(): # التسلية
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("رفع هطف", "تنزيل هطف")
    markup.add("زواج", "طلاق")
    markup.add("اكتموه")
    markup.add("رجوع")
    return markup

def لوحة_م5(): # Dev
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("حظر عام", "الغاء حظر عام")
    markup.add("ذيع", "الردود العامة")
    markup.add("اعادة تشغيل")
    markup.add("رجوع")
    return markup

def لوحة_م6(): # الخدمية
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("نسبه الحب", "تحبه")
    markup.add("قوقل", "ترجم عربي")
    markup.add("قران", "اذكار")
    markup.add("رجوع")
    return markup

# ========== لوحة المطور ==========
def dev_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(types.KeyboardButton("📊 الاحصائيات"), types.KeyboardButton("💾 نسخة احتياطية"))
    markup.row(types.KeyboardButton("🔒 صيانة"), types.KeyboardButton("⚙️ الاعدادات"))
    markup.row(types.KeyboardButton("❌ اغلاق"))
    return markup
