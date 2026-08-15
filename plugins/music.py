from pytgcalls import PyTgCalls
from pyrogram import Client

pytgcalls = None

def init_pytgcalls(bot: Client):
    global pytgcalls
    pytgcalls = PyTgCalls(bot)
    pytgcalls.start()
    print("✅ تم تشغيل pytgcalls بنجاح")
