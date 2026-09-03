from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def remove_menu():
    return ReplyKeyboardRemove()

MAIN_KEYBOARD = [
    [KeyboardButton("①"), KeyboardButton("②")],
    [KeyboardButton("③"), KeyboardButton("④")],
    [KeyboardButton("⑤"), KeyboardButton("⑥")],
    [KeyboardButton("اخفاء الاوامر")]
]
MAIN_MARKUP = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

ADMIN_KEYBOARD = [
    [KeyboardButton("رفع ادمن"), KeyboardButton("تنزيل ادمن")],
    [KeyboardButton("رفع مشرف"), KeyboardButton("تنزيل مشرف")],
    [KeyboardButton("رجوع")]
]
ADMIN_MARKUP = ReplyKeyboardMarkup(ADMIN_KEYBOARD, resize_keyboard=True)

SETTINGS_KEYBOARD = [
    [KeyboardButton("وضع ترحيب"), KeyboardButton("مسح ترحيب")],
    [KeyboardButton("وضع رابط"), KeyboardButton("الرابط")],
    [KeyboardButton("رجوع")]
]
SETTINGS_MARKUP = ReplyKeyboardMarkup(SETTINGS_KEYBOARD, resize_keyboard=True)

LOCK_KEYBOARD = [
    [KeyboardButton("قفل الروابط"), KeyboardButton("فتح الروابط")],
    [KeyboardButton("قفل الصور"), KeyboardButton("فتح الصور")],
    [KeyboardButton("رجوع")]
]
LOCK_MARKUP = ReplyKeyboardMarkup(LOCK_KEYBOARD, resize_keyboard=True)

FUN_KEYBOARD = [
    [KeyboardButton("رفع بقلبي"), KeyboardButton("تنزيل من قلبي")],
    [KeyboardButton("رفع خروف"), KeyboardButton("تنزيل خروف")],
    [KeyboardButton("رفع حمار"), KeyboardButton("تنزيل حمار")],
    [KeyboardButton("رتب التسليه"), KeyboardButton("مسح رتب التسليه")],
    [KeyboardButton("زواج"), KeyboardButton("طلاق")],
    [KeyboardButton("اكتموه")],
    [KeyboardButton("رجوع")]
]
FUN_MARKUP = ReplyKeyboardMarkup(FUN_KEYBOARD, resize_keyboard=True)

DEV_KEYBOARD = [
    [KeyboardButton("رفع Dev"), KeyboardButton("تنزيل Dev")],
    [KeyboardButton("قائمه الرتب العامه")],
    [KeyboardButton("حظر عام"), KeyboardButton("الغاء حظر عام")],
    [KeyboardButton("تحديث"), KeyboardButton("غادر"), KeyboardButton("رجوع")]
]
DEV_MARKUP = ReplyKeyboardMarkup(DEV_KEYBOARD, resize_keyboard=True)

SERVICE_KEYBOARD = [
    [KeyboardButton("نسبه الحب"), KeyboardButton("نسبه الغباء")],
    [KeyboardButton("تحبه"), KeyboardButton("صيح")],
    [KeyboardButton("شبيهي"), KeyboardButton("شبيهتي")],
    [KeyboardButton("اهديني"), KeyboardButton("اهديه")],
    [KeyboardButton("شرايك في افتاري"), KeyboardButton("افتاره")],
    [KeyboardButton("البايو")],
    [KeyboardButton("نادي المطور"), KeyboardButton("من ضافني")],
    [KeyboardButton("رجوع")]
]
SERVICE_MARKUP = ReplyKeyboardMarkup(SERVICE_KEYBOARD, resize_keyboard=True)

def get_main_markup(): return MAIN_MARKUP
def get_admin_markup(): return ADMIN_MARKUP
def get_settings_markup(): return SETTINGS_MARKUP
def get_lock_markup(): return LOCK_MARKUP
def get_fun_markup(): return FUN_MARKUP
def get_dev_markup(): return DEV_MARKUP
def get_service_markup(): return SERVICE_MARKUP

def get_menu_text(): return "اهلا بك في قائمة البوت\nاختر القسم:"
def get_lock_text(): return "قائمة القفل والفتح:"
def get_fun_text(): return "قائمة اوامر التسليه:"
def get_dev_text(): return "اهلا بك عزي Dev\nصلاحيات المطور الكاملة"
def get_service_text(): return "اهلا بك عزي\n- اوامر الخدميه :\n━━━━━━━━━━━━"
