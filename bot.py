import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "Tia"

# حط معرفك هنا عشان تكون ادمن. جيبه من /id
ADMIN_IDS = [] 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        text = f"مرحبا انا {BOT_NAME} 💜\n\nضفني لجروب وخليني مشرف\nالاوامر:\n/start\n/help\n/id\n/mention"
    else:
        text = f"هلا بالجميع انا {BOT_NAME} 💜\nارسل /help عشان تشوف اوامري"
    await update.message.reply_text(text)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""**اوامر {BOT_NAME}:**
/start - تشغيل البوت
/help - المساعدة
/id - معرفك + معرف الجروب
/mention - يمنشن الكل
/kick - طرد عضو "للادمن فقط"
/ban - حظر عضو "للادمن فقط"
"""
    await update.message.reply_text(text, parse_mode="Markdown")

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"معرفك: `{user_id}`\nمعرف الجروب: `{chat_id}`", parse_mode="Markdown")

async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    text = "منشن للكل 📢\n"
    async for member in chat.get_members():
        user = member.user
        if not user.is_bot:
            text += f"[{user.first_name}](tg://user?id={user.id}) "
    await update.message.reply_text(text, parse_mode="Markdown")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS and user_id != (await context.bot.get_chat(update.effective_chat.id)).owner.id:
        await update.message.reply_text("هذا الامر للادمن فقط")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("رد على رسالة الشخص اللي تريد تطرده")
        return
    target_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=target_id)
    await update.message.reply_text("تم الطرد ✅")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS and user_id != (await context.bot.get_chat(update.effective_chat.id)).owner.id:
        await update.message.reply_text("هذا الامر للادمن فقط")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("رد على رسالة الشخص اللي تريد تحظره")
        return
    target_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=target_id)
    await update.message.reply_text("تم الحظر ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "مرحبا" in text or "هلا" in text:
        await update.message.reply_text(f"هلا والله 👋")

def main():
    if not TOKEN:
        print("حط BOT_TOKEN في Variables")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("mention", mention_all)) # غيرنا منشن ل mention
    app.add_handler(CommandHandler("kick", kick)) # غيرنا طرد ل kick
    app.add_handler(CommandHandler("ban", ban)) # غيرنا حظر ل ban
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print(f"{BOT_NAME} شغال في الجروبات")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
