import os
from pyrogram import Client, filters
from pyrogram.types import Message

# جلب البيانات من متغيرات البيئة لتأمينها في Railway
API_ID = int(os.environ.get("API_ID", 1234567))  # سيتم جلبها من المنصة
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

app = Client("RailwayBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
  await message.reply(
      "🚀 أهلاً بك! البوت يعمل بنجاح ومستضاف على منصة Railway."
  )


# أوامر الحماية والبحث الوهمية كمثال
@app.on_message(filters.command("كتم") & filters.group)
async def mute_cmd(client: Client, message: Message):
  await message.reply("⚙️ أمر الحماية قيد التطوير.")


print("⚡ البوت بدأ العمل على Railway...")
app.run()
