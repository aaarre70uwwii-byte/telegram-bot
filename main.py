import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.idle import idle

# جيب المتغيرات من Railway
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# شغل البوت
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply("
أهلاً 👋
البوت شغال 100%
ارسل /help عشان تشوف الأوامر
")


@app.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    await message.reply("
**الأوامر المتاحة:**
/start - تشغيل البوت
/help - عرض المساعدة
")


@app.on_message(filters.text & filters.private)
async def echo(client: Client, message: Message):
    await message.reply(f"استلمت: {message.text}")


async def main():
    await app.start()
    print("✅ البوت اشتغل بنجاح")
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
