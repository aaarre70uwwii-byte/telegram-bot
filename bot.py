import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبا انا 𝐓𝐢𝐚 \n\nاوامري:\n/start\n/help\n/id")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - تشغيل البوت\n/help - المساعدة\n/id - معرفك")

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"معرفك: {update.effective_user.id}")

def main():
    if not TOKEN:
        print("حط BOT_TOKEN في Variables")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    print("Tia شغال")
    app.run_polling()

if __name__ == "__main__":
    main()
