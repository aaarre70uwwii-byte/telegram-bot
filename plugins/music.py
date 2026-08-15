import asyncio
from pytgcalls import PyTgCalls  # مهم: بدون _
from pytgcalls.types import StreamType
from pytgcalls.types.input_stream import AudioPiped
from pyrogram import filters, Client
import yt_dlp

pytgcalls = None

def init_pytgcalls(bot: Client):
    global pytgcalls
    pytgcalls = PyTgCalls(bot)
    pytgcalls.start()
    print("✅ تم تشغيل pytgcalls بنجاح")
