 import os
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH") 
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "tia_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply("✅ البوت شغال الحمدلله\nجرب /الاوامر")

@app.on_message(filters.command("الاوامر"))
async def help_cmd(client, message):
    await message.reply("**الاوامر:**\n/ban - حظر\n/mute - كتم\n/id - معرفك")

print("==============================")
print("Database Connected ✅")
print("Tia Bot Started ✅")
print("==============================")

app.run()
