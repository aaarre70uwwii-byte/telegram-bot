import os, asyncio, yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("MyBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app)

os.makedirs("downloads", exist_ok=True)

def download_song(query):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
        file = ydl.prepare_filename(info)
    return file, info['title']

# اوامر الحماية
@app.on_message(filters.command("ban") & filters.group)
async def ban(c, m: Message):
    if m.from_user.id!= OWNER_ID: return await m.reply("للمالك فقط")
    if not m.reply_to_message: return await m.reply("رد على العضو")
    await c.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    await m.reply("✅ تم حظر العضو")

@app.on_message(filters.command("mute") & filters.group)
async def mute(c,
