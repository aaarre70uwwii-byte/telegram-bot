import os
from pyrogram import Client

app = Client(
    "ProtectionBot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# استيراد الموديولات
from modules import locks, admin, start, fun

if __name__ == "__main__":
    print("• البوت شغال بنجاح ✅")
    app.run()
