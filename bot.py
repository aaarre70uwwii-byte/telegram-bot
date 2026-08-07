import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# تفعيل اللوجز عشان نشوف الاخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("ما لقيت TOKEN. اتأكد انك حطيته في Variables")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبا 👋 البوت شغال الان")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("البوت اشتغل...")
    app.run_polling()

if __name__ == "__main__":
    main()
