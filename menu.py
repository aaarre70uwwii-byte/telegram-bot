# menu.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def group_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton("①"), KeyboardButton("②"))
    markup.row(KeyboardButton("③"), KeyboardButton("④"))
    markup.row(KeyboardButton("⑤"), KeyboardButton("⑥"))
    markup.row(KeyboardButton("اخفاء الاوامر"))
    return markup

def get_m1_commands():
    text = "📋 قائمة اوامر الادمنيه m1\n━━━━━━━━━━━━━━━\nرفع مالك اساسي - تنزيل مالك اساسي\n...الخ"
    return text

def get_m2_commands(): 
    text = "⚙️ اهلا بك في قائمة اوامر الاعدادات m2\n━━━━━━━━━━━━━━━\nالرابط - المالكين الاساسين - الادمنيه\n...الخ"
    return text

def register_menu_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
    def group_handler(m):
        txt = m.text.strip() if m.text else ""
        if not txt: return
        
        # 1. الازرار
        if txt == "①":
            bot.send_message(m.chat.id, get_m1_commands())
        elif txt == "②":
            bot.send_message(m.chat.id, get_m2_commands())
        elif txt == "③": # ربط m3
            try:
                from m3 import get_m3_commands
                bot.send_message(m.chat.id, get_m3_commands())
            except Exception as e:
                bot.send_message(m.chat.id, f"❌ خطأ في ملف m3: {e}")
        elif txt == "④": # ربط m4
            try:
                from m4 import get_m4_commands # 1. استدعينا m4
                bot.send_message(m.chat.id, get_m4_commands())
            except Exception as e:
                bot.send_message(m.chat.id, f"❌ خطأ في ملف m4: {e}")
        elif txt == "⑤":
            bot.send_message(m.chat.id, "👨‍💻 قائمة Dev اوامر\nضع اوامرك هنا")
        elif txt == "⑥":
            bot.send_message(m.chat.id, "🛠 قائمة الاوامر الخدميه\nضع اوامرك هنا")
        elif txt == "اخفاء الاوامر":
            bot.send_message(m.chat.id, "✅ تم اخفاء القائمة", reply_markup=ReplyKeyboardRemove())
        
        # 2. بس لو كتب start او menu نعرض القائمة. منعنا السبام
        elif txt.lower() in ["/start", "/menu", "الاوامر"]:
            text = "- أهلاً بك عزي في قائمة الاوامر :\n"
            text += "━━━━━━━━━━━━━━━\n"
            text += "① : اوامر الادمنيه m1\n"
            text += "② : اوامر الاعدادات m2\n" 
            text += "③ : اوامر القفل - الفتح\n"
            text += "④ : اوامر التسليه m4\n" # 2. عدلنا الاسم
            text += "⑤ : Dev اوامر\n"
            text += "⑥ : الاوامر الخدميه\n"
            text += "━━━━━━━━━━━━━━━"
            bot.send_message(m.chat.id, text, reply_markup=group_menu_keyboard())
