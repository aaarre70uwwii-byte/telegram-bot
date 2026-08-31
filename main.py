import os
import json
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ========== ملف حفظ القروبات المفعلة ==========
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

# ========== دالة القائمة 6 ازرار ==========
def show_main_menu(chat_id):
    text = """- أهلاً بك عزي في قائمة الاوامر :

1م ◀ : اوامر الادمنيه
2م ◀ : اوامر الاعدادات
3م ◀ : اوامر القفل - الفتح
4م ◀ : اوامر التسليه
5م ◀ : Dev اوامر
6م ◀ : الاوامر الخدميه
"""

    keyboard = types.InlineKeyboardMarkup(row_width=3)

    btn1 = types.InlineKeyboardButton("1", callback_data="menu_1")
    btn2 = types.InlineKeyboardButton("2", callback_data="menu_2")
    btn3 = types.InlineKeyboardButton("3", callback_data="menu_3")
    btn4 = types.InlineKeyboardButton("4", callback_data="menu_4")
    btn5 = types.InlineKeyboardButton("5", callback_data="menu_5")
    btn6 = types.InlineKeyboardButton("6", callback_data="menu_6")

    keyboard.row(btn3, btn2, btn1)  # الصف الاول
    keyboard.row(btn4, btn5, btn6)  # الصف الثاني

    bot.send_message(chat_id, text, reply_markup=keyboard)

# ========== امر التفعيل ==========
@bot.message_handler(commands=['تفعيل'], chat_types=['group','supergroup'])
def activate_group(m):
    chat_id = m.chat.id
    if chat_id not in active_groups:
        active_groups.append(chat_id)
        save_groups(active_groups)
        bot.reply_to(m, "✅ تم التفعيل بنجاح\nالان تقدر تستخدم `الاوامر`")
    else:
        bot.reply_to(m, "⚠️ البوت مفعل مسبقاً في هذا القروب")

# ========== الاوامر تشتغل بس لو مفعل ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "الاوامر", chat_types=['group','supergroup'])
def menu_text(m):
    if m.chat.id in active_groups:
        show_main_menu(m.chat.id)
    else:
        bot.reply_to(m, "❌ البوت غير مفعل هنا\nاكتب /تفعيل لتفعيله")

@bot.message_handler(commands=['اوامر', 'start'])
def menu_cmd(m):
    if m.chat.type == 'private':
        return bot.send_message(m.chat.id, "⚠️ القائمة تشتغل في القروبات فقط")
    if m.chat.id in active_groups:
        show_main_menu(m.chat.id)
    else:
        bot.reply_to(m, "❌ البوت غير مفعل هنا\nاكتب /تفعيل لتفعيله")

# ========== معالجة الازرار بدون تعليق ==========
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    chat_id = c.message.chat.id
    
    if chat_id not in active_groups:
        return bot.answer_callback_query(c.id, "❌ القروب غير مفعل", show_alert=True)
    
    # نرد على الزر عشان ما يعلق
    if c.data == "menu_1":
        bot.answer_callback_query(c.id, "قائمة الادمنيه")
    elif c.data == "menu_2":
        bot.answer_callback_query(c.id, "قائمة الاعدادات")
    elif c.data == "menu_3":
        bot.answer_callback_query(c.id, "قائمة القفل")
    elif c.data == "menu_4":
        bot.answer_callback_query(c.id, "قائمة التسليه")
    elif c.data == "menu_5":
        bot.answer_callback_query(c.id, "قائمة المطور")
    elif c.data == "menu_6":
        bot.answer_callback_query(c.id, "القائمة الخدمية")

print("✅ البوت شغال...")
bot.infinity_polling(none_stop=True)
