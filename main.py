import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# استدعاء القائمة
from menu import menu, button

TOKEN = os.getenv("TOKEN")

# قاعدة بيانات بسيطة للتفعيل
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS group_settings (group_id INTEGER PRIMARY KEY, active INTEGER DEFAULT 0)''')
conn.commit()

def is_group_active(group_id):
    cur.execute("SELECT active FROM group_settings WHERE group_id =?", (group_id,))
    result = cur.fetchone()
    return result and result[0] == 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("• البوت شغال ✅\n• اكتب /menu لعرض القائمة")

async def activate_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'private': return
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if member.status not in ['administrator', 'creator']:
        await update.message.reply_text("• هذا الامر للادمنية فقط ❌"); return

    cur.execute("INSERT OR REPLACE INTO group_settings (group_id, active) VALUES (?, 1)", (update.effective_chat.id,))
    conn.commit()
    await update.message.reply_text("• تم تفعيل المجموعة بنجاح ✅")

async def menu_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'group' or update.effective_chat.type == 'supergroup':
        if not is_group_active(update.effective_chat.id):
            await update.message.reply_text("• القروب غير مفعل\n• اكتب `تفعيل` اول")
            return
    await menu(update, context) # ← كملت السطر ده

def main():
    if not TOKEN:
        print("خطأ: TOKEN غير موجود")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_wrapper))
    app.add_handler(MessageHandler(filters.Regex("^تفعيل$") & filters.ChatType.GROUPS, activate_group))
    app.add_handler(CallbackQueryHandler(button)) # للازرار

    print("البوت شغال...")
    app.run_polling() # ← مهم عشان يشتغل

if __name__ == "__main__":
    main()
