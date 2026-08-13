import os
from pyrogram import Client

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH") 
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("tia_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

import modules.start
import modules.admin
import modules.service
import modules.utils
import modules.locks

print("Tia Bot Started ✅ All modules loaded")
app.run()
