import os
import telebot
from telebot import types
import m1
import m2
import m3
import dev_panel # 1. استدعينا ملف المطور

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ خطأ: BOT_TOKEN فاضي. تأكد من Variables في Railway")
    exit()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

active_groups = []

m1.active_groups = active_groups
m2.register_settings_handlers(bot, active_groups)
m3.register_lock_handlers(bot, active_groups)

# 2. حط ايديك هنا حق التليجرام
OWNER_ID = "12345678" # <-- غير هذا لايديك
dev_panel.register_handlers(bot, OWNER_ID) # 3. شغلنا كيبورد المطور

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
        keyboard.row(types.InlineKeyboardButton("1", callback_data="menu_1"), types.InlineKeyboardButton("2", callback_data="menu_2"), types.InlineKeyboardButton("3", callback_data="menu_3"))
        keyboard.row(types.InlineKeyboardButton("4", callback_data="menu_4"), types.InlineKeyboardButton("5", callback_data="menu_5"), types.InlineKeyboardButton("6", callback_data="menu_6"))
    elif page == 2:
        text = """- أهلاً بك عزي في قائمة الاوامر - الصفحة 2 :

7م ◀ : اوامر الحماية
8م ◀ : اوامر الترحيب
9م ◀ : اوامر الردود
10م ◀ : اوامر الالعاب
11م ◀ : اوامر التحميل
12م ◀ : اوامر اخرى
"""
        keyboard.row(types.InlineKeyboardButton("7", callback_data="menu_7"), types.InlineKeyboardButton("8", callback_data="menu_8"), types.InlineKeyboardButton("9", callback_data="menu_9"))
        keyboard.row(types.InlineKeyboardButton("10", callback_data="menu_10"), types.InlineKeyboardButton("11", callback_data="menu_11"), types.InlineKeyboardButton("12", callback_data="menu_12"))

    btn_prev = types.InlineKeyboardButton("◀️ السابق", callback_data=f"page_{page-1}")
    btn_update = types.InlineKeyboardButton("🔄 تحديثات بوت Tia", callback_data="update")
    btn_next = types.InlineKeyboardButton("التالي ▶️", callback_data=f"page_{page+1}")
    btn_hide = types.InlineKeyboardButton("🗑️ اخفا الاوامر", callback_data="hide")
    if page == 1: keyboard.row(btn_update, btn_next)
    elif page == 2: keyboard.row(btn_prev, btn_update)
    keyboard.row(btn_hide)
    return text, keyboard

@bot.message_handler(content_types=['text'], func=lambda m: m.text and m.text.strip() == "تفعيل", chat_types=['group','supergroup'])
def activate_group(m):
    chat_id = m.chat.id
    print(f"[LOG] دخل على دالة تفعيل: {chat_id}")
    if chat_id not in active_groups:
        active_groups.append(chat_id)
        m1.active_groups = active_groups
        bot.reply_to(m, "✅ تم التفعيل بنجاح\nالان تقدر تستخدم الاوامر")
        print("[LOG] تم الرد بنجاح على تفعيل")
    else:
        bot.reply_to(m, "⚠️ البوت مفعل مسبقاً في هذا القروب")

@bot.message_handler(content_types=['text'], func=lambda m: m.text and m.text.strip() == "الاوامر", chat_types=['group','supergroup'])
def menu_text(m):
    print(f"[LOG] دخل على دالة الاوامر: {m.chat.id}")
    if m.chat.id in active_groups:
        text, kb = get_menu(1)
        bot.send_message(m.chat.id, text, reply_markup=kb)
        print("[LOG] تم ارسال القائمة")
    else:
        bot.reply_to(m, "❌ البوت غير مفعل هنا\nاكتب تفعيل لتفعيله")

@bot.message_handler(func=lambda message: True)
def log_all(message):
    print(f"[LOG] وصلت رسالة: {message.text} من {message.chat.id}")

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
        except Exception as e: print(f"خطأ تعديل الرسالة: {e}")
        bot.answer_callback_query(c.id)
    elif c.data == "menu_1": bot.answer_callback_query(c.id, "✅ تم تفعيل اوامر الادمنيه"); bot.send_message(chat_id, "<b>تم تفعيل اوامر الادمنيه</b> 🛡️\n\n- <code>رفع</code> - بالرد\n- <code>تنزيل</code> - بالرد\n- <code>حظر</code> - بالرد")
    elif c.data == "menu_2": bot.answer_callback_query(c.id, "✅ تم تفعيل اوامر الاعدادات"); bot.send_message(chat_id, "<b>تم تفعيل اوامر الاعدادات</b> ⚙️\n\n- <code>الاعدادات</code>\n- <code>الرابط</code>")
    elif c.data == "menu_3": bot.answer_callback_query(c.id, "✅ تم تفعيل اوامر الحماية"); bot.send_message(chat_id, "<b>تم تفعيل اوامر الحماية</b> 🔒\n\n- <code>الحماية</code>")
    elif c.data.startswith("menu_"): bot.answer_callback_query(c.id, f"قريباً: قائمة {c.data.split('_')[1]}")
    elif c.data == "update": bot.answer_callback_query(c.id, "🔄 اخر تحديث: v1.0 بوت Tia", show_alert=True)
    elif c.data == "hide":
        try: bot.delete_message(chat_id, c.message_id)
        except: pass
        bot.answer_callback_query(c.id, "تم اخفاء القائمة")

print("✅ البوت شغال...")
bot.remove_webhook()
bot.delete_webhook(drop_pending_updates=True)
bot.infinity_polling(none_stop=True, interval=0, timeout=20)
