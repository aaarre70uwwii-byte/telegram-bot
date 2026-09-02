import sqlite3
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# إعداد السجلات لمراقبة العمليات والتحقق من الأخطاء ومنع التعليق
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ----------------- تهيئة قاعدة البيانات للمجموعات -----------------
def init_db():
    conn = sqlite3.connect('group_management.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id INTEGER,
            setting_key TEXT,
            setting_value TEXT,
            PRIMARY KEY (chat_id, setting_key)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_data (
            chat_id INTEGER,
            data_key TEXT,
            data_value TEXT,
            PRIMARY KEY (chat_id, data_key)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# دالة مساعدة لجلب حالة إعداد معين
def get_setting(chat_id, key, default="مفتوح"):
    conn = sqlite3.connect('group_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM group_settings WHERE chat_id=? AND setting_key=?", (chat_id, key))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default

# ----------------- تصميم كيبورد قائمة الأوامر للجروب -----------------
def get_group_keyboard():
    keyboard = [
        [KeyboardButton("①"), KeyboardButton("②")],
        [KeyboardButton("③"), KeyboardButton("④"), KeyboardButton("⑤"), KeyboardButton("⑥")],
        [KeyboardButton("اخفاء الاوامر")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# ----------------- مستقبل كلمة "الاوامر" بالجروب -----------------
async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type in ['group', 'supergroup']:
        menu_text = (
            "➖ أهلاً بك عزي في قائمة اوامر 𝐓𝐢𝐚 :\n"
            "▬▬▬▬▬▬▬▬▬▬\n"
            "🔹 م1 : اوامر الادمنيه\n"
            "🔹 م2 : اوامر الاعدادات\n"
            "🔹 م3 : اوامر القفل - الفتح\n"
            "🔹 م4 : اوامر التسليه\n"
            "🔹 م5 : اوامر Dev\n"
            "🔹 م6 : الاوامر الخدميه\n"
            "▬"
        )
        await update.message.reply_text(menu_text, reply_markup=get_group_keyboard())

# ----------------- معالجة ضغطات الأزرار -----------------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if update.effective_chat.type not in ['group', 'supergroup']:
        return

    text = update.message.text

    if text == "①":
        admin_menu_text = (
            "أهلاً بك عزي في\n"
            " - قائمة اوامر الادمنيه\n"
            "━━━━━━━━━━━━\n"
            "🔻 اوامر الرفع والتنزيل :\n"
            "• رفع - تنزيل مالك اساسي\n• رفع - تنزيل مالك\n• رفع - تنزيل مدير\n• رفع - تنزيل ادمن\n• رفع - تنزيل مميز\n• تنزيل الكل\n"
            "🔻 اوامر المسح :\n"
            "• مسح الكل\n• مسح المدراء\n• مسح المالكين\n• مسح المحظورين\n• مسح المكتومين\n• مسح الردود\n"
            "🔻 اوامر الطرد والحظر :\n"
            "• حظر\n• طرد\n• كتم\n• تقييد\n• الغاء الحظر\n• الغاء الكتم\n• طرد البوتات\n"
            "━━━━━━━━━━━━"
        )
        await update.message.reply_text(admin_menu_text)

    elif text == "②":
        conn = sqlite3.connect('group_management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT data_value FROM group_data WHERE chat_id=? AND data_key='group_link'", (chat_id,))
        g_link_res = cursor.fetchone()
        g_link = g_link_res[0] if g_link_res else "لم يتم تعيين رابط بعد"
        conn.close()

        settings_menu_text = (
            f"- اهلا بك في قائمة اوامر الاعدادات :\n"
            f"━━━━━━━━━━━━\n"
            f"• رابط الجروب: {g_link}\n"
            f"• الحمايه: {get_setting(chat_id, 'protection', '✅ مفعله')}\n"
            f"• نظام التحميل: {get_setting(chat_id, 'download_system', '✅ مفعل')}\n"
            f"• ضع الترحيب\n• ضع قوانين\n• اضف رابط\n"
            f"━━━━━━━━━━━━"
        )
        await update.message.reply_text(settings_menu_text)

    elif text == "③":
        lock_menu_text = (
            "- قائمة القفل - الفتح :\n"
            "━━━━━━━━━━━━\n"
            f"• الروابط: {get_setting(chat_id, 'lock_links', '🔒 مقفل')}\n"
            f"• الصور: {get_setting(chat_id, 'lock_photos', '🔓 مفتوح')}\n"
            f"• الفيديو: {get_setting(chat_id, 'lock_video', '🔓 مفتوح')}\n"
            f"• البوتات: {get_setting(chat_id, 'lock_bots', '🔒 مقفل للطرد')}\n"
            f"• التكرار: {get_setting(chat_id, 'lock_flood', '🔒 مقفل')}\n"
            f"• الدردشه: {get_setting(chat_id, 'lock_chat', '🔓 مفتوح')}\n"
            "━━━━━━━━━━━━"
        )
        await update.message.reply_text(lock_menu_text)

    elif text == "④":
        fun_status = get_setting(chat_id, 'status_fun', '✅ مفعل')
        fun_menu_text = (
            f"• نظام التسلية: {fun_status}\n"
            "━━━━━━━━━━━━\n"
            "• رفع بقلبي\n• رفع خروف\n• رفع حمار\n"
            "• زواج\n• طلاق\n• اكتموه\n"
            "• تعطيل التسليه\n"
            "━━━━━━━━━━━━"
        )
        await update.message.reply_text(fun_menu_text)

    elif text == "⑤":
        dev_menu_text = (
            "💻 **قائمة اوامر Dev**\n"
            "━━━━━━━━━━━━\n"
            "• نسخة احتياطية\n"
            "• تحديث السورس\n"
            "• إذاعة للمجموعات\n"
            "• تنظيف الجروب\n"
            "• فحص البوت\n"
            "━━━━━━━━━━━━"
        )
        await update.message.reply_text(dev_menu_text)

    elif text == "⑥":
        service_menu_text = (
            "🛠️ **الاوامر الخدميه**\n"
            "━━━━━━━━━━━━\n"
            "• ايدي\n"
            "• الرابط\n"
            "• معلوماتي\n"
            "• الوقت\n"
            "• التاريخ\n"
            "• الجو\n"
            "━━━━━━━━━━━━"
        )
        await update.message.reply_text(service_menu_text)

    elif text == "اخفاء الاوامر":
        await update.message.reply_text("🙈 تم إخفاء قائمة الأوامر.", reply_markup=ReplyKeyboardRemove())

# ----------------- دالة الربط للسورس الموحد -----------------
def register_menu_handlers(application: Application):
    application.add_handler(MessageHandler(filters.Text(["الاوامر", "أوامر", "الاوامر ", "اوامر"]), send_menu))
    menu_buttons = filters.Text(["①", "②", "③", "④", "⑤", "⑥", "اخفاء الاوامر"])
    application.add_handler(MessageHandler(menu_buttons, handle_buttons))
