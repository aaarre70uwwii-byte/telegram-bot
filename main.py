from bot import app
from pyrogram import Client

app = Client(
    "ProtectionBot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# استدعاء كل الموديولات
import modules.start
import modules.admin
import modules.locks
import modules.fun

if __name__ == "__main__":
    print("• البوت شغال بنجاح ✅")
    app.run()
