from pyrogram import Client, filters
from pyrogram.types import Message
from main import app

@app.on_message(filters.group & filters.text)
async def echo(client, message: Message):
    if message.text == "بوت":
        await message.reply("ايوة انا هنا ✅")
