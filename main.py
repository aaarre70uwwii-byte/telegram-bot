from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.music import download_and_send
from plugins.security import check_user

app = Client("music_bot")

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    if not await check_user(client, message): return
    await message.reply_text(
        "مرحبا 👋\nارسل لي رابط يوتيوب / تيك توك / ساوندكلاود\nاقصى مدة: 60 دقيقة 🎵"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def get_url(client: Client, message: Message):
    if not await check_user(client, message): return

    url = message.text
    if "http" in url:
        await download_and_send(client, message, url)

app.run()
