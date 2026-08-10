 import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "𝐓𝐢𝐚"

COMMANDS = [
"/start - تشغيل البوت",
"/help - المساعدة", 
"/id - معرفك",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = "مرحبا انا **" + BOT_NAME + "** \n\n**اوامر " + BOT_NAME + ":**\n" + "\n".join(COMMANDS)
await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = "**اوامر " + BOT_NAME + ":**\n" + "\n".join(COMMANDS)
await update.message.reply_text(text, parse_mode="Markdown")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
await update.message.reply_text("معرفك هو: `" + str(user_id) + "`", parse_mode="Markdown")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = update.message.text.lower()
if "مرحبا" in text or "هلا" in text:
await update.message.reply_text("هلا والله انا " + BOT_NAME)
else:
await update.message.reply_text("ما فهمتك. ارسل /help")

def main():
if not BOT_TOKEN:
print("خطأ: BOT_TOKEN غير موجود")
return

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("id", id_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print(BOT_NAME + " شغال...")
app.run_polling()

if __name__ == "__main__":
main()
