import os
import sqlite3
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# استدعاء الملفات
from menu import menu, button
from m1 import m1_commands
from m2 import m2_commands

# قراءة المتغيرات من Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# انشاء قاعدة البيانات
conn = sqlite3.connect("/tmp/bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS group_settings
             (group_id INTEGER PRIMARY KEY, link TEXT, active INTEGER DEFAULT 0)''')

cur.execute('''CREATE TABLE IF NOT EXISTS ranks_admin
             (group_id INTEGER, user_id INTEGER, rank TEXT,
              PRIMARY KEY (group_id, user_id, rank))''')

cur.execute('''CREATE TABLE IF NOT EXISTS replies
             (group_id INTEGER, word TEXT, reply TEXT,
              PRIMARY KEY (group_id, word))''')
conn.commit()

# دالة للتحقق اذا القروب مفعل
def is_group_active(group_id):
    cur.execute("SELECT active FROM group_settings WHERE group_id =?", (group_id,))
    result = cur.fetchone()
    return result and result[0] == 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("• البوت شغال ✅\n• اكتب /menu لعرض الاوامر")

async def activate_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # للجروبات فقط
    if update.effective_chat.type == 'private':
        return

    # لازم الادمن هو اللي يفعله
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if member.status not in ['administrator', 'creator']:
        await update.message.reply_text("• هذا الامر للادمنية فقط ❌")
        return

    chat_id = update.effective_chat.id
    cur.execute("INSERT OR REPLACE INTO group_settings (group_id, active) VALUES (?, 1)", (chat_id,))
    conn.commit()

    await update.message.reply_text("• تم تفعيل المجموعة بنجاح ✅")

async def menu_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_group_active(update.effective_chat.id):
        await update.message.reply_text("• القروب غير مفعل\n• اكتب `تفعيل` اول", parse_mode="Markdown")
        return
    await menu(update, context)

async def m1_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_group_active(update.effective_chat.id):
        return
    await m1_commands(update, context)

async def m2_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_group_active(update.effective_chat.id):
        return
    await m2_commands(update, context)

def main():
    if not BOT_TOKEN:
        print("خطأ: BOT_TOKEN غير موجود")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # الهاندلرات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_wrapper))
    app.add_handler(MessageHandler(filters.Regex("^تفعيل$") & filters.ChatType.GROUPS, activate_group))

    app.add_handler(CallbackQueryHandler(button))

    # نستخدم الـ wrapper عشان نفحص التفعيل قبل
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, m1_wrapper))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, m2_wrapper))

    print("البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
