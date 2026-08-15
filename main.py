import asyncio
from pyrogram import Client
from plugins.music import init_pytgcalls
from dotenv import load_dotenv
import os

# شحن المتغيرات من ملف الـ .env
load_dotenv()

# إعداد عميل التليجرام (Pyrogram)
app = Client(
    "music_bot",
    api_id=int(os.getenv("API_ID", 12345)),
    api_hash=os.getenv("API_HASH", "your_api_hash"),
    bot_token=os.getenv("BOT_TOKEN", "your_bot_token")
)

# ربط وتفعيل مكتبة الصوت مع البوت
pytgcalls_client = init_pytgcalls(app)

async def main():
    print("جاري تشغيل بوت الأغاني...")
    await app.start()
    await pytgcalls_client.start()
    print("البوت يعمل الآن بنجاح وبدون أخطاء!")
    await asyncio.Event().wait()

if name == "main":
    asyncio.run(main())
