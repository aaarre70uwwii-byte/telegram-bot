import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pyrogram import Client, filters

pytgcalls = None

def init_pytgcalls(bot: Client):
    global pytgcalls
    pytgcalls = PyTgCalls(bot)
    pytgcalls.start()
    print("✅ تم تشغيل pytgcalls بنجاح")

# مثال امر تشغيل اغنية
@bot.on_message(filters.command("play") & filters.group)
async def play(_, message):
    chat_id = message.chat.id
    await pytgcalls.join_group_call(
        chat_id,
        AudioPiped("https://link-to-audio.mp3")
    )
    await message.reply("🎵 جاري التشغيل")
