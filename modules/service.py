from pyrogram import filters
from pyrogram.types import Message
from bot import app
import random, yt_dlp, os, asyncio

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)

def download_media(url, type="video"):
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
    }
    if type == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if type == "audio": filename = filename.rsplit(".", 1)[0] + ".mp3"
        return filename, info.get('title', 'بدون عنوان')

# ========== اوامر نسب وتسليه ==========
@app.on_message(filters.group & filters.text & filters.reply)
async def service_reply(_, m: Message):
    text = m.text.strip()
    target = m.reply_to_message.from_user

    if text == "نسبه الحب":
        per = random.randint(1, 100)
        await m.reply(f"نسبه حب {target.first_name} لك هي {per}% ❤️")
    elif text == "نسبه الغباء":
        per = random.randint(1, 100)
        await m.reply(f"نسبه غباء {target.first_name} هي {per}% 😂")

# ========== اوامر خدميه عامه ==========
@app.on_message(filters.group & filters.text)
async def service_group(_, m: Message):
    text = m.text.strip()
    if text.startswith("قوقل "):
        query = text.split("قوقل ")[1]
        await m.reply(f"🔍 ابحث في قوقل: https://www.google.com/search?q={query}")
    elif text.startswith("زخرف "):
        name = text.split("زخرف ")[1]
        fonts = [f"『{name}』", f"〲{name}〲", f"✧ {name} ✧"]
        await m.reply(f"زخرفه اسمك:\n" + "\n".join(fonts))

# ========== اوامر اسلاميه ==========
@app.on_message(filters.group & filters.text)
async def islamic(_, m: Message):
    text = m.text.strip()
    if text == "قران":
        await m.reply(f"📖 {random.choice(['الفاتحة', 'البقرة', 'الاخلاص'])}")

# ========== اوامر التحميل الحقيقي ==========
@app.on_message(filters.group & filters.text)
async def download_cmd(_, m: Message):
    text = m.text.strip()
    chat_id = m.chat.id
    if text.startswith("ساوند ") or text.startswith("تيك ") or text.startswith("تويتر "):
        msg = await m.reply("⏳ جاري التحميل انتظر...")
        try:
            if text.startswith("ساوند "):
                url = text.split("ساوند ")[1]
                file, title = await asyncio.to_thread(download_media, url, "audio")
                await app.send_audio(chat_id, file, caption=f"🎵 {title}")
            elif text.startswith("تيك "):
                url = text.split("تيك ")[1]
                file, title = await asyncio.to_thread(download_media, url, "video")
                await app.send_video(chat_id, file, caption=f"📱 {title}")
            os.remove(file)
            await msg.delete()
        except Exception as e:
            await msg.edit(f"❌ فشل التحميل: `{e}`")
