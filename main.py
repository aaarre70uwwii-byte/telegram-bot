import os
from pyrogram import Client, filters
from pyrogram.types import Message

# 1. نجيب المتغيرات من Railway
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

# 2. نشغل البوت
app = Client(
    "telegram_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 3. امر /start
@app.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    await message.reply("مرحبا! البوت شغال ✅")

# 4. الدالة الرئيسية
async def main():
    await app.start()
    print("✅ البوت اشتغل")
    # نرسل لك ان البوت اشتغل
    if ADMIN_ID != 0:
        await app.send_message(ADMIN_ID, "✅ تم تشغيل البوت بنجاح")
    await idle()

# 5. نشغل
if __name__ == "__main__":
    from pyrogram import idle
    app.run(main())
