from pyrogram import Client
from pyrogram.types import Message

app = Client.get_client("ProtectionBot")

@app.on_message(commands=["ping"])
async def ping_cmd(client, message: Message):
    await message.reply("pong 🏓")
