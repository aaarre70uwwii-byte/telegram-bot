import os
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH") 
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("tia_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply("✅ البوت شغال")

@app.on_message(filters.command("الاوامر"))
async def help_cmd(client, message):
    await message.reply("**الاوامر:**\n/ban - حظر\n/mute - كتم\n/id - ايديك")

@app.on_message(filters.command("ban") & filters.group)
async def ban_cmd(client, message):
    if not message.reply_to_message: return
    await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.reply("✅ تم الحظر")

@app.on_message(filters.command("mute") & filters.group)
async def mute_cmd(client, message):
    if not message.reply_to_message: return
    await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.reply("🔇 تم الكتم")

print("Tia Bot Started ✅")
app.run()
