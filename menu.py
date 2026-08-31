import os
import json
from telebot import types

FILE = "active_groups.json"

def load_groups():
    if os.path.exists(FILE):
        with open(FILE, 'r') as f:
            return json.load(f)
    return []

def save_groups(groups):
    with open(FILE, 'w') as f:
        json.dump(groups, f)

active_groups = load_groups()

def get_menu(page=1):
    text = ""
    keyboard = types.InlineKeyboardMarkup(row_width=3)

    if page == 1:
        text = """<b>- أهلاً بك عزي في قائمة الاوامر - الصفحة 1 -</b>

1️⃣ ◀ : اوامر الادمنيه
2️⃣ ◀ : اوامر الاعدادات
3️⃣ ◀ : اوامر القفل - الفتح
4️⃣ ◀ : اوامر التسليه
5️⃣ ◀ : Dev اوامر
6️⃣ ◀ : الاوامر الخدميه
"""
        keyboard.row(
            types.InlineKeyboardButton("1", callback_data="menu_1"),
            types.InlineKeyboardButton("2", callback_data="menu_2"),
            types.InlineKeyboardButton("3", callback_data="menu_3")
        )
        keyboard.row(
            types.InlineKeyboardButton("4", callback_data="menu_4"),
            types.InlineKeyboardButton("5", callback_data="menu_5"),
            types.InlineKeyboardButton("6", callback_data="menu_6")
        )

    btn_update = types.InlineKeyboardButton("🔄 تحديثات بوت Tia", callback_data="update")
    btn_next = types.InlineKeyboardButton("التالي ▶️", callback_data=f"page_{page+1}")
    btn_hide = types.InlineKeyboardButton("🗑️ اخفاء الاوامر", callback_data="hide")

    if page == 1: keyboard.row(btn_update, btn_next)
    keyboard.row(btn_hide)
    return text, keyboard

def register(bot):

    @bot.message_handler(func=lambda m: m.text and m.text.strip() == "تفعيل", chat_types=['group','supergroup'])
    def activate_group(m):
        chat_id = m.chat.id
        if chat_id not in active_groups:
            active_groups.append(chat_id)
            save_groups(active_groups)
            bot.reply_to(m, "✅ تم التفعيل بنجاح\nالان تقدر تستخدم `الاوامر`")
        else:
            bot.reply_to(m, "⚠️ البوت مفعل مسبقاً في هذا القروب")

    @bot.message_handler(func=lambda m: m.text and m.text.strip() == "الاوامر", chat_types=['group','supergroup'])
    def menu_text(m):
        if m.chat.id in active_groups:
            text, kb = get_menu(1)
            bot.send_message(m.chat.id, text, reply_markup=kb)
        else:
            bot.reply_to(m, "❌ البوت غير مفعل هنا\nاكتب تفعيل لتفعيله")

    @bot.callback_query_handler(func=lambda c: True)
    def cb(c):
        chat_id = c.message.chat.id
        if chat_id not in active_groups:
            return bot.answer_callback_query(c.id, "❌ القروب غير مفعل", show_alert=True)

        if c.data.startswith("page_"):
            page = int(c.data.split("_")[1])
            if page < 1 or page > 2: return bot.answer_callback_query(c.id, "مافي صفحات اكثر")
            text, kb = get_menu(page)
            try: bot.edit_message_text(text, chat_id, c.message_id, reply_markup=kb)
            except: pass
            bot.answer_callback_query(c.id)

        elif c.data == "menu_1":
            text = """<b>اوامر الادمنيه 🛡️</b>
- `رفع` - بالرد
- `تنزيل` - بالرد
- `تنزيل الكل`
- `حظر` - بالرد
- `طرد` - بالرد
- `كتم` - بالرد
- `الغاء الكتم` - بالرد
- `مسح 10`
- `رتبتي`
"""
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("◀️ رجوع للقائمة", callback_data="page_1"))
            try: bot.edit_message_text(text, chat_id, c.message_id, reply_markup=kb)
            except: pass
            bot.answer_callback_query(c.id)

        elif c.data == "menu_2": # ربط m2
            text = """<b>اوامر الاعدادات ⚙️</b>

- `الاعدادات` - عرض القائمة
- `الاعدادات خاص` - ارسالها لك خاص
- `همس` - بالرد على رسالة
- `ضع قوانين` + النص
- `ضع الترحيب` + النص
- `اضف رابط` + الرابط
"""
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("◀️ رجوع للقائمة", callback_data="page_1"))
            try: bot.edit_message_text(text, chat_id, c.message_id, reply_markup=kb)
            except: pass
            bot.answer_callback_query(c.id)

        elif c.data.startswith("menu_"):
            bot.answer_callback_query(c.id, f"قريباً: قائمة {c.data.split('_')[1]}")
        elif c.data == "update":
            bot.answer_callback_query(c.id, "🔄 اخر تحديث: v1.0 بوت Tia", show_alert=True)
        elif c.data == "hide":
            try: bot.delete_message(chat_id, c.message_id)
            except: pass
            bot.answer_callback_query(c.id, "تم اخفاء القائمة")
