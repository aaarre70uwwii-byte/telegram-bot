import os
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH") 
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("tia_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply("✅ البوت اشتغل اخيرا")

@app.on_message(filters.command("الاوامر"))
async def help_cmd(client, message):
    await message.reply("الاوامر: /ban /mute /id")

print("Tia Bot Started ✅")
app.run()
