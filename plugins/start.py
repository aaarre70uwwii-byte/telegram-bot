from pyrogram import Client, filters
import config

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await message.reply_text(
        f"مرحباً بك {message.from_user.mention} في بوت الحماية والأغاني!\n"
        "أرسل /help لرؤية الأوامر."
    )
