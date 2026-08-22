import telebot
import sqlite3
import os
import sys
import random
from telebot import types
from datetime import datetime

# ====== الاعدادات الاساسية ======
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
ID_المطور_اساسي = 7488375443 # غيره لايديك
DB = "bot.db"

القاب_التسليه = {
    "هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب",
    "كلبه": "الكلبات", "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج",
    "لحجيه": "اللحجيات", "خروف": "الخرفان", "خفيف": "الخفيفين", "خفيفه": "الخفاف"
}

# ====== قاعدة البيانات ======
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS ranks (chat_id, user_id, role)")
    conn.execute("CREATE TABLE IF NOT EXISTS locks (chat_id, lock_name, status)")
    conn.execute("CREATE TABLE IF NOT EXISTS global_ranks (user_id, role)")
    conn.execute("CREATE TABLE IF NOT EXISTS global_bans (user_id)")
    conn.execute("CREATE TABLE IF NOT EXISTS fun_ranks (chat_id, user_id, title)")
    conn.execute("CREATE TABLE IF NOT EXISTS whispers (id INTEGER PRIMARY KEY, from_id, to_id, chat_id, text, read_status)")
    conn.commit(); conn.close()
init_db()

def هو_قروب_او_قناة(chat_id):
    try:
        chat = bot.get_chat(chat_id)
        return chat.type in ['group', 'supergroup', 'channel']
    except:
        return False

def جيب_الرتبة(chat_id, user_id):
    if user_id == ID_المطور_اساسي: return "مطور_اساسي"
    conn = sqlite3.connect(DB); result = conn.execute("SELECT role FROM global_ranks WHERE user_id =?", (user_id,)).fetchone(); conn.close()
    if result: return result[0]
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status == "creator": return "مالك_اساسي"
        if member.status == "administrator": return "ادمن"
    except: pass
    conn = sqlite3.connect(DB); result = conn.execute("SELECT role FROM ranks WHERE chat_id =? AND user_id =?",(chat_id, user_id)).fetchone(); conn.close()
    return result[0] if result else "عضو"

# ====== لوحات الازرار ======
def لوحة_التحكم_الرئيسية():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🛡️ الادمنية", callback_data="menu_admin"),
        types.InlineKeyboardButton("🔒 القفل", callback_data="menu_locks"),
        types.InlineKeyboardButton("👑 المطور", callback_data="menu_dev"),
        types.InlineKeyboardButton("😂 التسليه", callback_data="menu_fun"),
        types.InlineKeyboardButton("📡 الخدميه", callback_data="menu_service"),
        types.InlineKeyboardButton("❌ اغلاق", callback_data="close_menu")
    )
    return markup

def لوحة_الادمنية():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("طرد", callback_data="cmd_طرد"),
        types.InlineKeyboardButton("حظر", callback_data="cmd_حظر"),
        types.InlineKeyboardButton("كتم", callback_data="cmd_كتم"),
        types.InlineKeyboardButton("رفع ادمن", callback_data="cmd_رفع_ادمن"),
        types.InlineKeyboardButton("تنزيل ادمن", callback_data="cmd_تنزيل_ادمن"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def لوحة_القفل():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("قفل الروابط", callback_data="lock_الروابط"),
        types.InlineKeyboardButton("فتح الروابط", callback_data="unlock_الروابط"),
        types.InlineKeyboardButton("قفل الصور", callback_data="lock_الصور"),
        types.InlineKeyboardButton("فتح الصور", callback_data="unlock_الصور"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def لوحة_التسليه():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for لقب in ["هطف", "كلب", "بثر", "خروف"]:
        buttons.append(types.InlineKeyboardButton(f"رفع {لقب}", callback_data=f"fun_رفع_{لقب}"))
    buttons.append(types.InlineKeyboardButton("رفع بقلبي", callback_data="fun_رفع_بقلبي"))
    buttons.append(types.InlineKeyboardButton("رتب التسليه", callback_data="cmd_رتب_التسليه"))
    buttons.append(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    markup.add(*buttons)
    return markup

def لوحة_المطور(user_id):
    if user_id!= ID_المطور_اساسي: return None
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("رفع Dev", callback_data="dev_رفع_Dev"),
        types.InlineKeyboardButton("حظر عام", callback_data="dev_حظر_عام"),
        types.InlineKeyboardButton("اذاعة", callback_data="dev_ذيع"),
        types.InlineKeyboardButton("اعادة تشغيل", callback_data="dev_اعاده_تشغيل"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def لوحة_الخدميه():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("نسبة الحب", callback_data="ser_نسبه_الحب"),
        types.InlineKeyboardButton("نسبة الغباء", callback_data="ser_نسبه_الغباء"),
        types.InlineKeyboardButton("قوقل", callback_data="ser_قوقل"),
        types.InlineKeyboardButton("زخرف", callback_data="ser_زخرف"),
        types.InlineKeyboardButton("قران", callback_data="ser_قران"),
        types.InlineKeyboardButton("همسه", callback_data="ser_همسه"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

# ====== الامر الرئيسي ======
@bot.message_handler(commands=['الاوامر', 'menu'])
def امر_الاوامر(message):
    if not هو_قروب_او_قناة(message.chat.id):
        return bot.reply_to(message, "❌ اللوحة تشتغل في القروبات والقنوات فقط")
    نص = f"""👋 **اهلا بك في لوحة تحكم البوت**
مرحبا {message.from_user.first_name}
اختر القسم من الازرار بالاسفل"""
    bot.reply_to(message, نص, reply_markup=لوحة_التحكم_الرئيسية(), parse_mode="Markdown")

# ====== نظام الازرار ======
@bot.callback_query_handler(func=lambda call: True)
def التعامل_مع_الازرار(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    message_id = call.message_id # صلحناها

    if not هو_قروب_او_قناة(chat_id):
        return bot.answer_callback_query(call.id, "❌ تشتغل بالقروبات فقط", show_alert=True)

    try:
        if data == "back_main":
            bot.edit_message_text("👋 القائمة الرئيسية", chat_id, message_id, reply_markup=لوحة_التحكم_الرئيسية())
        elif data == "close_menu":
            bot.delete_message(chat_id, message_id)
        elif data == "menu_admin":
            bot.edit_message_text("🛡️ **قسم الادمنية**\nرد على الشخص ثم اضغط الامر", chat_id, message_id, reply_markup=لوحة_الادمنية())
        elif data == "menu_locks":
            bot.edit_message_text("🔒 **قسم القفل والفتح**", chat_id, message_id, reply_markup=لوحة_القفل())
        elif data == "menu_fun":
            bot.edit_message_text("😂 **قسم التسليه**\nرد على الشخص ثم اضغط", chat_id, message_id, reply_markup=لوحة_التسليه())
        elif data == "menu_dev":
            panel = لوحة_المطور(user_id)
            if panel: bot.edit_message_text("👑 **قسم المطور الاساسي فقط**", chat_id, message_id, reply_markup=panel)
            else: bot.answer_callback_query(call.id, "❌ للمطور الاساسي فقط", show_alert=True)
        elif data == "menu_service":
            bot.edit_message_text("📡 **قسم الخدميه**", chat_id, message_id, reply_markup=لوحة_الخدميه())

        # تنفيذ الاوامر
        elif data.startswith("cmd_"):
            if not call.message.reply_to_message: return bot.answer_callback_query(call.id, "⚠️ لازم ترد على شخص اول", show_alert=True)
            target_id = call.message.reply_to_message.from_user.id
            cmd = data.replace("cmd_", "")
            if cmd == "طرد": bot.ban_chat_member(chat_id, target_id); bot.unban_chat_member(chat_id, target_id); bot.answer_callback_query(call.id, "✅ تم الطرد")
            elif cmd == "حظر": bot.ban_chat_member(chat_id, target_id); bot.answer_callback_query(call.id, "✅ تم الحظر")
            elif cmd == "كتم": bot.restrict_chat_member(chat_id, target_id, can_send_messages=False); bot.answer_callback_query(call.id, "✅ تم الكتم")
            elif cmd == "رفع_ادمن":
                conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO ranks VALUES (?,?,?)", (chat_id, target_id, "ادمن")); conn.commit(); conn.close()
                bot.answer_callback_query(call.id, "✅ تم رفع ادمن")
            elif cmd == "تنزيل_ادمن":
                conn = sqlite3.connect(DB); conn.execute("DELETE FROM ranks WHERE chat_id =? AND user_id =?", (chat_id, target_id)); conn.commit(); conn.close()
                bot.answer_callback_query(call.id, "✅ تم تنزيل ادمن")
            elif cmd == "رتب_التسليه":
                conn = sqlite3.connect(DB); results = conn.execute("SELECT user_id, title FROM fun_ranks WHERE chat_id =?", (chat_id,)).fetchall(); conn.close()
                نص = "📋 **رتب التسليه:**\n"
                for uid, title in results: نص += f"- {bot.get_chat_member(chat_id, uid).user.first_name} : {title}\n"
                bot.answer_callback_query(call.id, نص if results else "مافي رتب", show_alert=True)

        elif data.startswith("lock_"):
            if جيب_الرتبة(chat_id, user_id) in ["عضو"]: return bot.answer_callback_query(call.id, "❌ ماعندك صلاحية", show_alert=True)
            الشيء = data.replace("lock_", "")
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO locks VALUES (?,?,?)", (chat_id, الشيء, "قفل")); conn.commit(); conn.close()
            bot.answer_callback_query(call.id, f"✅ تم قفل {الشيء}")

        elif data.startswith("unlock_"):
            if جيب_الرتبة(chat_id, user_id) in ["عضو"]: return bot.answer_callback_query(call.id, "❌ ماعندك صلاحية", show_alert=True)
            الشيء = data.replace("unlock_", "")
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO locks VALUES (?,?,?)", (chat_id, الشيء, "فتح")); conn.commit(); conn.close()
            bot.answer_callback_query(call.id, f"✅ تم فتح {الشيء}")

        elif data.startswith("fun_"):
            if not call.message.reply_to_message: return bot.answer_callback_query(call.id, "⚠️ لازم ترد على شخص اول", show_alert=True)
            target_id = call.message.reply_to_message.from_user.id
            اللقب = data.replace("fun_رفع_", "")
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?)", (chat_id, target_id, اللقب)); conn.commit(); conn.close()
            لقب_كامل = القاب_التسليه.get(اللقب, اللقب)
            bot.answer_callback_query(call.id, f"✅ تم رفع {call.message.reply_to_message.from_user.first_name} {لقب_كامل}")

        elif data.startswith("ser_"):
            الامر = data.replace("ser_", "")
            if الامر == "نسبه_الحب": bot.answer_callback_query(call.id, f"💕 النسبة: {random.randint(0,100)}%", show_alert=True)
            elif الامر == "نسبه_الغباء": bot.answer_callback_query(call.id, f"🧠 النسبة: {random.randint(0,100)}%", show_alert=True)
            elif الامر == "قران": bot.answer_callback_query(call.id, "📖 بسم الله الرحمن الرحيم", show_alert=True)
            elif الامر == "همسه": bot.answer_callback_query(call.id, "استخدم: /همسه النص بالرد", show_alert=True)
            else: bot.answer_callback_query(call.id, f"✅ تم تنفيذ /{الامر}")

        elif data.startswith("dev_"):
            if user_id!= ID_المطور_اساسي: return bot.answer_callback_query(call.id, "❌ للمطور فقط", show_alert=True)
            if data == "dev_اعاده_تشغيل":
                bot.answer_callback_query(call.id, "🔄 جاري اعادة التشغيل")
                os.execv(sys.executable, ['python'] + sys.argv)
            else: bot.answer_callback_query(call.id, "✅ تم تنفيذ الامر")

    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ خطأ: {e}", show_alert=True)

# ====== الهمسات ======
@bot.message_handler(commands=['همسه'])
def همسه(message):
    if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
    try: النص = message.text.split(" ", 1)[1]
    except: return bot.reply_to(message, "⚠️ اكتب: /همسه النص")
    from_id = message.from_user.id; to_id = message.reply_to_message.from_user.id; chat_id = message.chat.id
    conn = sqlite3.connect(DB); conn.execute("INSERT INTO whispers (from_id, to_id, chat_id, text, read_status) VALUES (?,?,?,?,?)", (from_id, to_id, chat_id, النص, "غير_مقروء")); conn.commit(); conn.close()
    markup = types.InlineKeyboardMarkup(); markup.add(types.InlineKeyboardButton("📩 عرض الهمسة", callback_data=f"read_whisper_{from_id}_{to_id}"))
    bot.reply_to(message.reply_to_message, f"🔒 لديك همسة جديدة من {message.from_user.first_name}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('read_whisper_'))
def قراءة_الهمسه(call):
    _, from_id, to_id = call.data.split("_")
    if str(call.from_user.id)!= to_id: return bot.answer_callback_query(call.id, "❌ ليست لك", show_alert=True)
    conn = sqlite3.connect(DB); result = conn.execute("SELECT text FROM whispers WHERE from_id =? AND to_id =? ORDER BY id DESC LIMIT 1", (from_id, to_id)).fetchone()
    if result: bot.answer_callback_query(call.id, f"الهمسة: {result[0]}", show_alert=True)
    else: bot.answer_callback_query(call.id, "❌ لا توجد همسة", show_alert=True)
    conn.close()

# ====== ترحيب المطور الاساسي ======
@bot.message_handler(content_types=['new_chat_members'])
def ترحيب_المطور(message):
    chat_id = message.chat.id
    if not هو_قروب_او_قناة(chat_id): return
    for member in message.new_chat_members:
        if member.id == ID_المطور_اساسي:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📋 فتح لوحة التحكم", callback_data="back_main"))
            نص = f"""👑 **اهلا وسهلا عزي المطور**
شرفتني بحضورك في {message.chat.title} ❤️"""
            bot.send_message(chat_id, نص, reply_markup=markup, parse_mode="Markdown") # قفلنا القوس

print("✅ البوت main.py شغال...")
bot.polling(none_stop=True)
