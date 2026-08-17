from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
import asyncio

# استدعاء كل الملفات
from commands import *
from buttons import *

app = Client(
    "tia_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def main():
    print("『𝐓𝐢𝐚』 البوت شغال الان ...")
    await app.start()
    print(f"『𝐓𝐢𝐚』 تم تسجيل الدخول: {(await app.get_me()).first_name}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
