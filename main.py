from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from utils.database import db

app = Client(
    "protection_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins") # يشغل كل شي داخل plugins تلقائي
)

if __name__ == "__main__":
    print("=================================")
    print("✅ البوت الاحترافي شغال الان")
    print("=================================")
    app.run()
