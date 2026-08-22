import os
import sys
import re
import sqlite3
import asyncio
import random
from datetime import timedelta
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CommandHandler
from telegram.constants import ChatMemberStatus

# --- 1. قراءة البيانات من.env للامان ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEVELOPER_ID = int(os.getenv("DEVELOPER_ID", "7488375443")) # حطه في.env افضل
# ----------------------------------------

DB_FILE = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_roles (chat_id INTEGER, user_id INTEGER, role TEXT, PRIMARY KEY(chat_id, user_id, role))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS locks (chat_id INTEGER, item TEXT, status INTEGER, PRIMARY KEY(chat_id, item))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS features (chat_id INTEGER, item TEXT, status INTEGER, PRIMARY KEY(chat_id, item))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS replies (chat_id INTEGER, type TEXT, keyword TEXT, response TEXT, PRIMARY KEY(chat_id, type, keyword))''')
    conn.commit()
    conn.close()

init_db()

# دوال DB باستخدام with للامان
def set_role(chat_id, user_id, role):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT OR REPLACE INTO users_roles VALUES (?,?,?)", (chat_id, user_id, role))

def check_role(chat_id, user_id, role):
    with sqlite3.connect(DB_FILE) as conn:
        res = conn.execute("SELECT 1 FROM users_roles WHERE chat_id=? AND user_id=? AND role=?", (chat_id, user_id, role)).fetchone()
        return bool(res)

def set_lock(chat_id, item, status):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT OR REPLACE INTO locks VALUES (?,?,?)", (chat_id, item, 1 if status else 0))

def get_lock(chat_id, item):
    with sqlite3.connect(DB_FILE) as conn:
        res = conn.execute("SELECT status FROM locks WHERE chat_id=? AND item=?", (chat_id, item)).fetchone()
        return bool(res) if res else False

#... باقي دوال DB نفس الفكرة

# نصوص القوائم
menu_main_text = "🎀 *AISED PANEL* 🎀\n━━━━━━━━━━━━━━━━━━━━\n👋 *أهلاً بك عزي في قائمة الأوامر الرئيسية:*"
cliche_m1 = "🛠️ *قائمة أوامر الإدارة (م1):*\nحظر | طرد | كتم | رفع ادمن"
cliche_m2 = "⚙️ *قائمة الإعدادات (م2):*\nالرابط | القوانين | معلوماتي"
cliche_m3 = "🔒 *قائمة الأقفال (م3):*\nقفل الروابط | قفل الصور | قفل الكل"
cliche_m4 = "🎭 *قائمة التسلية (م4):*\nزواج | طلاق | العاب"
cliche_m5 = "👑 *قائمة Dev (م5):*\nحظر عام | اذاعة | اعادة تشغيل"
cliche_m6 = "🌿 *قائمة الخدمية (م6):*\nقوقل | ترجم | تحميل"

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("➊ الادارة", callback_data="btn_m1"), InlineKeyboardButton("➋ الاعدادات", callback_data="btn_m2"), InlineKeyboardButton("➌ الاقفال", callback_data="btn_m3")],
        [InlineKeyboardButton("➍ التسلية", callback_data="btn_m4"), InlineKeyboardButton("➎ Dev", callback_data="btn_m5")],
        [InlineKeyboardButton("➏ الخدمية", callback_data="btn_m6")],
        [InlineKeyboardButton("القفل والفتح", callback_data="btn_m3"), InlineKeyboardButton("التفعيل", callback_data="btn_features")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="btn_back")]]
    return InlineKeyboardMarkup(keyboard)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    if not chat or chat.type not in ["group", "supergroup"]: return False
    user_id = update.effective_user.id
    if user_id == DEVELOPER_ID: return True
    try:
        member = await context.bot.get_chat_member(chat.id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

# --- 2. الاوامر الاساسية ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(menu_main_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# --- 3. التعامل مع الازرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    texts = {
        "btn_m1": cliche_m1, "btn_m2": cliche_m2, "btn_m3": cliche_m3,
        "btn_m4": cliche_m4, "btn_m5": cliche_m5, "btn_m6": cliche_m6,
        "btn_back": menu_main_text
    }

    if data in texts:
        reply_markup = get_back_keyboard() if data!= "btn_back" else get_main_keyboard()
        await query.edit_message_text(texts[data], reply_markup=reply_markup, parse_mode="Markdown")

# --- 4. تشغيل البوت ---
def main():
    if not TOKEN:
        print("خطأ: حط TOKEN في متغير البيئة TELEGRAM_BOT_TOKEN")
        sys.exit(1)

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
