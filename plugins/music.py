import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall

pytgcalls_client = None

def init_pytgcalls(client):
    global pytgcalls_client
    pytgcalls_client = PyTgCalls(client)

# دالة مساعدة لتحميل واستخراج رابط الصوت المباشر من يوتيوب
def get_audio_url(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            return info['url'], info['title']
        except Exception as e:
            return None, str(e)

@Client.on_message(filters.command("play") & filters.group)
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ يرجى كتابة اسم أو رابط الأغنية بجانب الأمر!\nمثال: /play faded")

    query = " ".join(message.command[1:])
    status_msg = await message.reply_text("🔍 جاري البحث عن الأغنية في يوتيوب...")

    audio_url, title = get_audio_url(query)
    if not audio_url:
        return await status_msg.edit_text(f"❌ حدث خطأ أثناء البحث: {title}")

    chat_id = message.chat.id

    try:
        if pytgcalls_client:
            await pytgcalls_client.join_group_call(
                chat_id,
                AudioPiped(audio_url)
            )
            await status_msg.edit_text(f"🎶 تم بدء التشغيل بنجاح!\n\n📌 الأغنية: {title}")
        else:
            await status_msg.edit_text("⚠️ نظام المكالمات الصوتية غير مفعّل في الملف الرئيسي.")

    except NoActiveGroupCall:
        await status_msg.edit_text("❌ يجب فتح المكالمة الصوتية في المجموعة أولاً!")
    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء الاتصال الصوتي: {e}")

@Client.on_message(filters.command("stop") & filters.group)
async def stop_music(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        if pytgcalls_client:
            await pytgcalls_client.leave_group_call(chat_id)
            await message.reply_text("⏹ تم إيقاف التشغيل ومغادرة المكالمة الصوتية.")
        else:
            await message.reply_text("⚠️ النظام غير مهيأ.")
    except Exception as e:
        await message.reply_text(f"❌ خطأ أثناء الإيقاف: {e}")
