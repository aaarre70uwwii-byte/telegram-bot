import os
import json
import telebot
from telebot import types
import m1 # استدعاء ملف الادمنيه
import m2 # استدعاء ملف الاعدادات
import m3 # استدعاء ملف الحماية

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

FILE = "active_groups.json"

def load_groups():
    if os.path.exists(FILE):
        with open(FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_groups(groups):
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(groups, f)

active_groups = load_groups()

# مرر active_groups للملفات عشان يتأكدوا من التفعيل
m1.active_groups = active_groups
m2.register_settings_handlers(bot, active_groups)
m3.register_lock_handlers(bot, active_groups) # <-- ربط m3

# ========== دالة توليد القائمة حسب الصفحة ==========
def get_menu(page=1):
    text = ""
    keyboard = types.InlineKeyboardMarkup(row_width=3)

    if page == 1:
        text = """- أهلاً بك عزي في قائمة الاوامر - الصفحة 1 :

1م ◀ : اوامر الادمنيه
2م ◀ : اوامر الاعدادات
3م ◀ : اوامر القفل - الفتح
4م ◀ : اوامر التسليه
5م ◀ : Dev اوامر
6م ◀ : الاوامر الخدميه
"""
        btn1 = types.InlineKeyboardButton("1", callback_data="menu_1")
        btn2 = types.InlineKeyboardButton("2", callback_data="menu_2")
        btn3 = types.InlineKeyboardButton("3", callback_data="menu_3")
        btn4 = types.InlineKeyboardButton("4", callback_data="menu_4")
        btn5 = types.InlineKeyboardButton("5", callback_data="menu_5")
        btn6 = types.InlineKeyboardButton("6", callback_data="menu_6")
        keyboard.row(btn1, btn2, btn3)
        keyboard.row(btn4, btn5, btn6)

    elif page == 2:
        text = """- أهلاً بك عزي في قائمة الاوامر - الصفحة 2 :

7م ◀ : اوامر الحماية
8م ◀ : اوامر الترحيب
9م ◀ : اوامر الردود
10م ◀ : اوامر الالعاب
11م ◀ : اوامر التحميل
12م ◀ : اوامر اخرى
"""
        btn1 = types.InlineKeyboardButton("7", callback_data="menu_7")
        btn2 = types.InlineKeyboardButton("8", callback_data="menu_8")
        btn3 = types.InlineKeyboardButton("9", callback_data="menu_9")
        btn4 = types.InlineKeyboardButton("10", callback_data="menu_10")
        btn5 = types.InlineKeyboardButton("11", callback_data="menu_11")
        btn6 = types.InlineKeyboardButton("12", callback_data="menu_12")
        keyboard.row(btn1, btn2, btn3)
        keyboard.row(btn4, btn5, btn6)

    btn_prev = types.InlineKeyboardButton("◀️ السابق", callback_data=f"page_{page-1}")
    btn_update = types.InlineKeyboardButton("🔄 تحديثات بوت Tia", callback_data="update")
    btn_next = types.InlineKeyboardButton("التالي ▶️", callback_data=f"page_{page+1}")
    btn_hide = types.InlineKeyboardButton("🗑️ اخفا الاوامر", callback_data="hide")

    if page == 1:
        keyboard.row(btn_update, btn_next)
    elif page == 2:
        keyboard.row(btn_prev, btn_update)

    keyboard.row(btn_hide)

    return text, keyboard

# ========== امر التفعيل بدون / ==========
@bot.message_handler(content_types=['text'], func=lambda m: m.text and m.text.strip() == "تفعيل", chat_types=['group','supergroup'])
def activate_group(m):
    chat_id = m.chat.id
    if chat_id not in active_groups:
        active_groups.append(chat_id)
        save_groups(active_groups)
        m1.active_groups = active_groups # تحديث القائمة في m1
        bot.reply_to(m, "✅ تم التفعيل بنجاح\nالان تقدر تستخدم `الاوامر`")
    else:
        bot.reply_to(m, "⚠️ البوت مفعل مسبقاً في هذا القروب")

# ========== امر الاوامر بدون / ==========
@bot.message_handler(content_types=['text'], func=lambda m: m.text and m.text.strip() == "الاوامر", chat_types=['group','supergroup'])
def menu_text(m):
    if m.chat.id in active_groups:
        text, kb = get_menu(1)
        bot.send_message(m.chat.id, text, reply_markup=kb)
    else:
        bot.reply_to(m, "❌ البوت غير مفعل هنا\nاكتب تفعيل لتفعيله")

# ========== معالجة الازرار ==========
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    chat_id = c.message.chat.id

    if chat_id not in active_groups:
        return bot.answer_callback_query(c.id, "❌ القروب غير مفعل", show_alert=True)

    if c.data.startswith("page_"):
        page = int(c.data.split("_")[1])
        if page < 1 or page > 2:
            return bot.answer_callback_query(c.id, "مافي صفحات اكثر")
        text, kb = get_menu(page)
        try:
            bot.edit_message_text(text, chat_id, c.message_id, reply_markup=kb)
        except:
            pass
        bot.answer_callback_query(c.id)

    elif c.data == "menu_1":
        bot.answer_callback_query(c.id, "✅ تم تفعيل اوامر الادمنيه")
        bot.send_message(chat_id, """**تم تفعيل اوامر الادمنيه** 🛡️
تقدر الحين تستخدم الاوامر التالية:

• `رفع` - بالرد على العضو
• `تنزيل` - بالرد على العضو
• `تنزيل الكل`
• `مسح 10` - امسح رسائل
• `حظر` - بالرد
• `طرد` - بالرد
• `كتم` - بالرد
• `الغاء الكتم` - بالرد
• `الغاء الحظر` - بالرد
• `رتبتي`""", parse_mode="Markdown")

    elif c.data == "menu_2": # زر الاعدادات
        bot.answer_callback_query(c.id, "✅ تم تفعيل اوامر الاعدادات")
        bot.send_message(chat_id, """**تم تفعيل اوامر الاعدادات** ⚙️
تقدر الحين تستخدم الاوامر التالية:

• `الاعدادات` - عرض كل الاوامر
• `الرابط` • `القوانين` • `معلوماتي`
• `ضع الترحيب` • `انشاء رابط`
• `همس` - بالرد على العضو + النص
• `الاعدادات خاص`""", parse_mode="Markdown")

    elif c.data == "menu_3": # <-- زر الحماية الجديد
        bot.answer_callback_query(c.id, "✅ تم تفعيل اوامر الحماية")
        bot.send_message(chat_id, """**تم تفعيل اوامر الحماية** 🔒
تقدر الحين تستخدم:

• `الحماية` - لفتح قائمة الاقفال
• تقدر تقفل: الروابط, الصور, الفيديو, السب, التكرار...الخ""", parse_mode="Markdown")

    elif c.data.startswith("menu_"):
        num = c.data.split("_")[1]
        bot.answer_callback_query(c.id, f"قريباً: قائمة {num}")

    elif c.data == "update":
        bot.answer_callback_query(c.id, "🔄 اخر تحديث: v1.0 بوت Tia", show_alert=True)

    elif c.data == "hide":
        try:
            bot.delete_message(chat_id, c.message_id)
        except:
            pass
        bot.answer_callback_query(c.id, "تم اخفاء القائمة")

print("✅ البوت شغال...")
bot.infinity_polling(none_stop=True, interval=0, timeout=20)
