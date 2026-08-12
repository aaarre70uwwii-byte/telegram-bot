import os
from pyrogram import Client, filters, types
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("RoseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("حظر") & filters.group)
async def ban(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ هذا الامر للمالك فقط")
    if message.reply_to_message:
        await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply(f"✅ تم حظر {message.reply_to_message.from_user.first_name}")

@app.on_message(filters.command("كتم") & filters.group)
async def mute(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ هذا الامر للمالك فقط")
    if message.reply_to_message:
        await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=types.ChatPermissions())
        await message.reply(f"🔇 تم كتم {message.reply_to_message.from_user.first_name}")

@app.on_message(filters.command("الغاء_كتم") & filters.group)
async def unmute(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ هذا الامر للمالك فقط")
    if message.reply_to_message:
        await client.restrict_chat_member(message.chat.id, message.reply_to
