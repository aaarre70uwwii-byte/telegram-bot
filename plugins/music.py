import os
import yt_dlp
from pyrogram import Client
from pyrogram.types import Message
from config import DOWNLOAD_DIR, MAX_SONG_DURATION, MESSAGE_DUPLICATE_LIMIT

downloaded_cache = []

def get_ydl_opts():
    return {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
    }

async def download_and_send(client: Client, message: Message, url: str):
    # منع التكرار
    if url in downloaded_cache:
        if len(downloaded_cache) >= MESSAGE_DUPLICATE_LIMIT:
            downloaded_cache.clear()
        return await message.reply_text("⚠️ تم ارسال هذا الرابط من قبل")

    downloaded_cache.append(url)
    msg = await message.reply_text("جاري التحميل... ⏳")

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

        if info.get('duration', 0) > MAX_SONG_DURATION * 60:
            await msg.edit_text(f"❌ الاغنية اطول من {MAX_SONG_DURATION} دقيقة")
            os.remove(file_path)
            return

        await msg.delete()
        await message.reply_audio(
            audio=file_path,
            title=info.get('title'),
            performer=info.get('uploader'),
            duration=info.get('duration')
        )
        os.remove(file_path)

    except Exception as e:
        await msg.edit_text(f"صار خطأ: `{e}`")
