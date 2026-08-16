from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import asyncio
from config import DOWNLOAD_DIR, MAX_SONG_DURATION, MESSAGES, admin_filter

# قائمة التشغيل
QUEUE = {}

# نتاكد ان المجلد موجود
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

async def download_song(url):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = f"{DOWNLOAD_DIR}/{info['id']}.{info['ext']}"
        return filepath, info['title'], info['duration']

# ===== 1. امر البحث والتحميل =====
@Client.on_message(filters.command(["اغنية", "song", "play"]))
async def play_song(c: Client, m):
    if len(m.command) < 2:
        return await m.reply("اكتب: `/اغنية اسم الاغنية`")
    
    query = " ".join(m.command[1:])
    msg = await m.reply(MESSAGES["downloading"])

    try:
        # البحث في يوتيوب
        search_url = f"ytsearch1:{query}"
        filepath, title, duration = await asyncio.to_thread(download_song, search_url)
        
        if duration > MAX_SONG_DURATION * 60:
            os.remove(filepath)
            return await msg.edit(f"❌ الاغنية اطول من {MAX_SONG_DURATION} دقايق")
        
        # ارسال الصوت
        await c.send_audio(
            chat_id=m.chat.id,
            audio=filepath,
            title=title,
            caption=f"🎵 **{title}**\nطلب بواسطة: {m.from_user.mention}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏭️ تخطي", callback_data="skip")]
            ])
        )
        await msg.delete()
        os.remove(filepath) # نمسح الملف بعد الارسال
        
    except Exception as e:
        await msg.edit(f"{MESSAGES['song_not_found']}\nالخطأ: {e}")

# ===== 2. امر الايقاف - حاليا بس يمسح =====
@Client.on_message(filters.command(["ايقاف", "stop"]))
async def stop_song(c: Client, m):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        QUEUE[chat_id] = []
    await m.reply("⏹️ تم ايقاف التشغيل")

# ===== 3. زر التخطي =====
@Client.on_callback_query(filters.regex("skip"))
async def skip_callback(c, callback_query):
    await callback_query.answer("⏭️ تم التخطي")
    await callback_query.message.delete()

print("✅ تم تحميل ملف الموسيقى music.py")
