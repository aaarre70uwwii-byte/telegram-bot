import os
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from pytgcalls import GroupCallFactory  # التحديث الصحيح للجيل الثالث
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall

pytgcalls_client = None
group_call_factory = None

def init_pytgcalls(client):
    global pytgcalls_client, group_call_factory
    # استخدام معمل الاتصال الصوتي الحديث للجيل الثالث
    group_call_factory = GroupCallFactory(client)
    pytgcalls_client = group_call_factory.get_group_call()

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
            # طريقة التشغيل المحدثة للجيل الثالث
            await pytgcalls_client.join_group_call(message.chat.id, AudioPiped(url))
            await status.edit_text(f"🎶 تم التشغيل بنجاح:\n{title}")
    except NoActiveGroupCall:
        await status.edit_text("❌ افتح المكالمة الصوتية في المجموعة أولاً!")
    except Exception as e:
        await status.edit_text(f"❌ خطأ بالاتصال: {e}")

@Client.on_message(filters.command("stop") & filters.group)
async def stop_music(client: Client, message: Message):
    try:
        if pytgcalls_client:
            await pytgcalls_client.leave_group_call(message.chat.id)
            await message.reply_text("⏹ تم إيقاف وتشغيل الأغنية ومغادرة المكالمة.")
    except Exception as e:
        await message.reply_text(f"❌ خطأ أثناء الإيقاف: {e}")
