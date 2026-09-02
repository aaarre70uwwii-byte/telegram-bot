import os
import sqlite3
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات لمراقبة العمليات ومنع تعليق البوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ----------------- الإعدادات الأساسية المستدعاة من Railway -----------------
DEVELOPER_ID = int(os.getenv('OWNER_ID', 7488375443))

# ----------------- تهيئة قاعدة البيانات -----------------
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups (group_id INTEGER PRIMARY KEY)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS replies (keyword TEXT PRIMARY KEY, response TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')

    # قيم افتراضية للإعدادات باسم 𝐓𝐢𝐚
    default_settings = [
        ('bot_name', '𝐓𝐢𝐚'),
        ('service_status', '✅ مفعل'),
        ('contact_status', '✅ مفعل'),
        ('updates_channel', 'لا يوجد حالياً (أرسل الرابط لتحديثه)'),
        ('welcome_text', 'أهلاً بك في 𝐓𝐢𝐚! لمتابعة التحديثات اشترك هنا: ')
    ]
    for key, value in default_settings:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", (key, value))

    conn.commit()
    conn.close()

init_db()

# ----------------- كيبورد المطور المخصص -----------------
def get_dev_keyboard():
    keyboard = [
        [KeyboardButton("قائمة ألعاب"), KeyboardButton("أعدادات ألبوت")],
        [KeyboardButton("أضف رد عام"), KeyboardButton("تغير المطور الاساسي")],
        [KeyboardButton("مسح رد عام"), KeyboardButton("تغير أسم البوت")],
        [KeyboardButton("تحديث الملفات"), KeyboardButton("تفعيل ألبوت")],
        [KeyboardButton("جلب ألنسخه ألأحتياطيه"), KeyboardButton("أضف الترحيب نص+بصوره")],
        [KeyboardButton("تفعيل البوت ألخدمي"), KeyboardButton("تعطيل البوت ألخدمي")],
        [KeyboardButton("تفعيل التواصل"), KeyboardButton("تعطيل التواصل")],
        [KeyboardButton("الاذاعه خاص+مجموعات"), KeyboardButton("الاحصايات")],
        [KeyboardButton("تغير قناه البوت"), KeyboardButton("ألمطورين")],
        [KeyboardButton("المساعد"), KeyboardButton("اخفاء قائمة البوت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# ----------------- أمر تشغيل البوت -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    if chat_type in ['group', 'supergroup']:
        cursor.execute("INSERT OR IGNORE INTO groups (group_id) VALUES (?)", (update.effective_chat.id,))
    else:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

    if user_id == DEVELOPER_ID:
        await update.message.reply_text(
            "👋 مرحباً بك يا مطور 𝐓𝐢𝐚! لوحة التحكم مفعّلة 👇",
            reply_markup=get_dev_keyboard()
        )
    else:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='welcome_text'")
        welcome = cursor.fetchone()
        cursor.execute("SELECT value FROM settings WHERE key='updates_channel'")
        channel = cursor.fetchone()
        conn.close()

        full_welcome_msg = f"{welcome[0] if welcome else ''}\n\n📢 قناة التحديثات: {channel[0] if channel else ''}"
        await update.message.reply_text(full_welcome_msg)

# ----------------- معالجة أزرار التحكم -----------------
async def handle_dev_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id!= DEVELOPER_ID: return

    text = update.message.text
    chat_id = update.effective_chat.id
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    if text == "أعدادات ألبوت":
        cursor.execute("SELECT key, value FROM settings")
        all_set = cursor.fetchall()
        msg = "⚙️ **إعدادات 𝐓𝐢𝐚 الحالية:**\n\n" + "\n".join([f"🔹 {k}: {v}" for k,v in all_set])
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == "الاحصايات":
        cursor.execute("SELECT COUNT(*) FROM users"); u_count = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM groups"); g_count = cursor.fetchone()
        await update.message.reply_text(f"📊 **إحصائيات 𝐓𝐢𝐚:**\n\n👤 الخاص: {u_count[0]}\n👥 المجموعات: {g_count[0]}")
    elif text == "جلب ألنسخه ألأحتياطيه":
        await update.message.reply_text("📦 جاري جلب النسخة...")
        try: await context.bot.send_document(chat_id=chat_id, document=open('bot_data.db', 'rb'), filename="backup_Tia.db")
        except Exception as e: await update.message.reply_text(f"❌ فشل: {str(e)}")
    elif text == "اخفاء قائمة البوت":
        await update.message.reply_text("🙈 تم الإخفاء.", reply_markup=ReplyKeyboardRemove())
    elif text in ["أضف رد عام", "مسح رد عام", "تغير أسم البوت", "أضف الترحيب نص+بصوره", "الاذاعه خاص+مجموعات", "تغير قناه البوت", "تغير المطور الاساسي"]:
        actions = {"أضف رد عام": 'add_reply', "مسح رد عام": 'del_reply', "تغير أسم البوت": 'change_name', "أضف الترحيب نص+بصوره": 'change_welcome', "الاذاعه خاص+مجموعات": 'broadcast', "تغير قناه البوت": 'change_updates_channel', "تغير المطور الاساسي": 'change_dev'}
        context.user_data['action'] = actions[text]
        await update.message.reply_text("📝 ارسل المطلوب الآن...")

    conn.commit()
    conn.close()

# ----------------- استقبال المدخلات والردود والإذاعة -----------------
async def handle_inputs_and_replies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    if not text: return

    # 1. اذا كان المطور يعمل عملية
    if user_id == DEVELOPER_ID:
        action = context.user_data.get('action')
        if action:
            conn = sqlite3.connect('bot_data.db')
            cursor = conn.cursor()

            if action == 'add_reply' and '=' in text:
                keyword, response = text.split('=', 1)
                cursor.execute("INSERT OR REPLACE INTO replies (keyword, response) VALUES (?,?)", (keyword.strip(), response.strip()))
                await update.message.reply_text(f"✅ تم اضافة الرد: `{keyword.strip()}`")
            elif action == 'del_reply':
                cursor.execute("DELETE FROM replies WHERE keyword=?", (text,))
                await update.message.reply_text(f"🗑️ تم مسح الرد: `{text}`")
            elif action == 'broadcast':
                cursor.execute("SELECT user_id FROM users"); users = cursor.fetchall()
                cursor.execute("SELECT group_id FROM groups"); groups = cursor.fetchall()
                await update.message.reply_text(f"📢 جاري الاذاعة لـ {len(users)} مستخدم و {len(groups)} مجموعة...")
                for u in users:
                    try: await context.bot.send_message(chat_id=u[0], text=text)
                    except: pass
                for g in groups:
                    try: await context.bot.send_message(chat_id=g[0], text=text)
                    except: pass
                await update.message.reply_text("✅ تمت الاذاعة بنجاح")
            elif action == 'change_dev':
                global DEVELOPER_ID
                DEVELOPER_ID = int(text)
                await update.message.reply_text(f"👑 تم تغيير المطور الى: `{DEVELOPER_ID}`")
            elif action == 'change_name':
                cursor.execute("UPDATE settings SET value=? WHERE key='bot_name'", (text,))
                await update.message.reply_text(f"✏️ تم تغيير اسم 𝐓𝐢𝐚 الى: {text}")
            elif action == 'change_welcome':
                cursor.execute("UPDATE settings SET value=? WHERE key='welcome_text'", (text,))
                await update.message.reply_text("🖼️ تم تغيير نص الترحيب")
            elif action == 'change_updates_channel':
                cursor.execute("UPDATE settings SET value=? WHERE key='updates_channel'", (text,))
                await update.message.reply_text(f"📢 تم تغيير قناة التحديثات")

            context.user_data['action'] = None
            conn.commit()
            conn.close()
            return

    # 2. الردود التلقائية للكل
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM replies WHERE keyword=?", (text,))
    reply = cursor.fetchone()
    conn.close()
    if reply:
        await update.message.reply_text(reply[0])

# ----------------- دالة الربط للسورس الموحد -----------------
def register_dev_handlers(application: Application):
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dev_buttons))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_inputs_and_replies))
