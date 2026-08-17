from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID

# انشاء البوت
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# امر /start
@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text(
        f"مرحبا {message.from_user.first_name} 👋\n"
        f"البوت شغال 100% على Railway"
    )

# امر /ping للتجربة
@app.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    await message.reply_text("pong ✅")

# رسالة للادمن لما يشتغل
@app.on_startup
async def on_startup(client: Client):
    print("=================================")
    print("✅ البوت الاحترافي شغال الان")
    print("=================================")
    try:
        await client.send_message(ADMIN_ID, "✅ البوت اشتغل على Railway")
    except:
        pass

# تشغيل البوت
if __name__ == "__main__":
    app.run()
