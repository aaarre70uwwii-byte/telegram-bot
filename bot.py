import os
from pyrogram import Client

# يقرأ من متغيرات Railway
app = Client(
    "ProtectionBot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

import modules.database
import modules.locks
import modules.protection
import modules.settings
import modules.services
import modules.games
import modules.dev

print("• البوت شغال بنجاح ✅")
app.run()
