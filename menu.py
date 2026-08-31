import os
import json
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

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

# ========== دالة توليد القائمة حسب الصفحة ==========
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

    elif page == 2:
        text = """<b>- أهلاً بك عزي في قائمة الاوامر - الصفحة 2 -</b>

7️⃣ ◀ : اوامر الحماية
8️⃣ ◀ : اوامر الترحيب
9️⃣ ◀ : اوامر الردود
🔟 ◀ : اوامر الالعاب
1️⃣1️⃣ ◀ : اوامر التحميل
1️⃣2️⃣ ◀ : اوامر اخرى
"""
        keyboard.row(
            types.InlineKeyboardButton("7", callback_data="menu_7"),
            types.InlineKeyboardButton("8", callback_data="menu_8"),
            types.InlineKeyboardButton("9", callback_data="menu_9")
        )
        keyboard.row(
            types.InlineKeyboardButton("10", callback_data="menu_10"),
            types.InlineKeyboardButton("11", callback_data="menu_11"),
            types.InlineKeyboardButton("12", callback_data="menu_12")
        )

    # ازرار التنقل
    btn_prev = types.InlineKeyboardButton("◀️ السابق", callback_data=f"page_{page-1}")
    btn_update = types.InlineKeyboardButton("🔄 تحديثات بوت Tia", callback_data="update")
    btn_next = types.InlineKeyboardButton("التالي ▶️", callback_data=f"page_{page+1}")
    btn_hide = types.InlineKeyboardButton("🗑️ اخفاء الاوامر", callback_data="hide")

    if page == 1:
        keyboard.row(btn_update, btn_next)
    elif page == 2:
        keyboard.row(btn_prev, btn_update)

    keyboard.row(btn_hide) # صف لحاله

    return text, keyboard

# ========== امر التفعيل بدون / ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "تفعيل", chat_types=['group','supergroup'])
def activate_group(m):
    chat_id = m.chat.id
    if chat_id not in active_groups:
        active_groups.append(chat_id)
        save_groups(active_groups)
        bot.reply_to(m, "✅ تم التفعيل بنجاح\nالان تقدر تستخدم `الاوامر`")
    else:
        bot.reply_to(m, "⚠️ البوت مفعل مسبقاً في هذا القروب")

# ========== امر الاوامر بدون / ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "الاوامر", chat_types=['group','supergroup'])
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

    # تبديل الصفحات
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

    # الازرار 1-12
    elif c.data == "menu_1":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>اوامر الادمنيه 🛡️</b>\n\n- <code>رفع</code> - بالرد\n- <code>تنزيل</code> - بالرد\n- <code>حظر</code> - بالرد\n- <code>طرد</code> - بالرد\n- <code>كتم</code> - بالرد")

    elif c.data == "menu_2":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>اوامر الاعدادات ⚙️</b>\n\n- <code>الاعدادات</code>\n- <code>الرابط</code>\n- <code>ضع الرابط</code>")

    elif c.data == "menu_3":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>اوامر القفل 🔒</b>\n\n- <code>قفل الرابط</code>\n- <code>قفل الصور</code>\n- <code>فتح الكل</code>")

    elif c.data == "menu_4":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>اوامر التسليه 😂</b>\n\n- <code>نكته</code>\n- <code>حزوره</code>\n- <code>صراحه</code>")

    elif c.data == "menu_5":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>Dev اوامر 👨‍💻</b>\n\n- <code>تحديث</code>\n- <code>فحص</code>\n- <code>السيرفر</code>")

    elif c.data == "menu_6":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>الاوامر الخدميه 📌</b>\n\n- <code>ايدي</code>\n- <code>معلوماتي</code>\n- <code>احصائيات</code>")

    elif c.data == "menu_7":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>اوامر الحماية 🛡️</b>\n\n- <code>الحماية</code>\n- <code>منع التكرار</code>")

    elif c.data == "menu_8":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>اوامر الترحيب 👋</b>\n\n- <code>ضع ترحيب</code>\n- <code>الترحيب</code>")

    elif c.data == "menu_9":
        bot.answer_callback_query(c.id)
        bot.send_message(chat_id, "<b>اوامر الردود 💬</b>\n\n- <code>اضف رد</code>\n- <code>حذف رد</code>\n- <code>الردود</code>")

    elif c.data.startswith("menu_"):
        bot.answer_callback_query(c.id, "قريباً...")

    # تحديثات
    elif c.data == "update":
        bot.answer_callback_query(c.id, "🔄 اخر تحديث: v1.0 بوت Tia", show_alert=True)

    # اخفا
    elif c.data == "hide":
        try:
            bot.delete_message(chat_id, c.message_id)
        except:
            pass
        bot.answer_callback_query(c.id, "تم اخفاء القائمة")

print("✅ البوت شغال...")
bot.remove_webhook()
bot.infinity_polling(none_stop=True, interval=0, timeout=20)
