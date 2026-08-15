import os
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# تهيئة مشغل الصوتيات بالطريقة الحديثة المتوافقة مع الجيل الثالث
def init_pytgcalls(app: Client):
    pytgcalls_client = PyTgCalls(app)
    return pytgcalls_client

# دالة لتشغيل الصوت في المكالمة كمثال بدون أخطاء
async def play_audio(pytgcalls_client: PyTgCalls, chat_id: int, audio_path: str):
    await pytgcalls_client.connect(chat_id)
    await pytgcalls_client.play(
        chat_id,
        MediaStream(audio_path)
    )
