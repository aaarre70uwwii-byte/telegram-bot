import os
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioStream  # تم استخدام النوع الحديث لتوافق النسخة
from pytgcalls.exceptions import NoActiveGroupCall

pytgcalls_client = None

def init_pytgcalls(client):
    global pytgcalls_client
    pytgcalls_client = PyTgCalls(client)
    # ملاحظة: في الجيل الثالث تبدأ المكتبة تلقائياً مع البوت ولا تحتاج .start() هنا

def get_audio_url(query: str):
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'default_search': 'ytsearch'}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info: 
                info = info['entries']
            return info['url'], info['title']
        except Exception as e:
            return None, str(e)

@Client.on_message(filters.command("play") & filters.group)
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ اكتب اسم الأغنية بعد الأمر، مثل: /play faded")
    query = " ".join(message.command[1:])
    status = await message.reply_text("🔍 جاري البحث...")
    url, title = get_audio_url(query)
    if not url: 
        return await status.edit_text(f"❌ خطأ: {title}")
    try:
        if pytgcalls_client:
            # استخدام النمط المحدث للجيل الثالث
            await pytgcalls_client.join_group_call(message.chat.id, AudioStream(url))
            await status.edit_text(f"🎶 تم التشغيل بنجاح:\n{title}")
    except NoActiveGroupCall:
        await status.edit_text("❌ افتح المكالمة الصوتية في المجموعة أولاً!")
    except Exception as e:
        await status.edit_text(f"❌ خطأ بالاتصال: {e}")
