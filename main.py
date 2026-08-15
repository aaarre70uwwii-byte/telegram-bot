import os, asyncio, yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream import InputAudioStream, InputStream

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("MyBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app)

# قاموس عشان نحفظ التشغيل
QUEUE = {}

def download_song(query):
    ydl_opts = {'format': 'bestaudio', 'outtmpl': 'downloads/%(id)s.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        file = ydl.prepare_filename(info['entries'][0])
    return file, info['entries'][0]['title']

# اوامر الحماية
@app.on_message(filters.command("ban") & filters.group)
async def ban(c, m: Message):
    if m.from_user.id!= OWNER_ID: return
    await c.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    await m.reply("✅ تم حظر العضو")

@app.on_message(filters.command("mute") & filters.group)
async def mute(c, m: Message):
    if m.from_user.id!= OWNER_ID: return
    await c.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    await m.reply("🔇 تم كتم العضو")

# اوامر الاغاني
@app.on_message(filters.command("play") & filters.group)
async def play(c, m: Message):
    if len(m.command) < 2: return await m.reply("ارسل: /play اسم الاغنية")
    msg = await m.reply("جاري التحميل...")
    try:
        file, title = download_song(" ".join(m.command[1:]))
        await pytgcalls.join_group_call(
            m.chat.id,
            AudioPiped(file)
        )
        await msg.edit(f"🎵 يتم تشغيل الان: {title}")
    except Exception as e:
        await msg.edit(f"خطأ: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(c, m: Message):
    await pytgcalls.leave_group_call(m.chat.id)
    await m.reply("⏹️ تم ايقاف التشغيل")

@app.on_message(filters.command("start"))
async def start(c, m: Message):
    await m.reply(f"مرحبا انا {os.getenv('BOT_NAME')}\n\nاوامر:\n/play اسم الاغنية\n/ban /mute رد\n/stop")

pytgcalls.start()
app.run()
