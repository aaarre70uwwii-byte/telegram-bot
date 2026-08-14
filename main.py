import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Define your command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text("Hello! Your containerized bot is running successfully! 🚀")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes incoming text messages."""
    text_received = update.message.text
    
    # Simple reply logic
    if "hello" in text_received.lower():
        await update.message.reply_text("Hi there! How can I help you today?")
    else:
        await update.message.reply_text(f"Echo: {text_received}")

# 2. Main execution block
def main():
    # Best Practice: Get the token from Environment Variables for container security
    # Fallback to a hardcoded string if you haven't set up environment variables yet
    TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_ACTUAL_BOT_TOKEN_HERE")
    
    if TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE" or not TOKEN:
        print("ERROR: Please provide a valid Telegram Token!", file=sys.stderr)
        sys.exit(1)

    print("Initializing bot application...")
    # Build the application locally inside the main block (Prevents circular imports)
    app = Application.builder().token(TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("Bot is successfully polling for messages... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
