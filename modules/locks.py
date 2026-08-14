from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions # التعديل 1

app = Client.get_client("ProtectionBot")

@app.on_message(filters.command("قفل")) # التعديل 2
async def lock_cmd(client, message: Message):
    await app.set_chat_permissions(
        message.chat.id,
        ChatPermissions(can_send_messages=False)
    )
    await message.reply("تم قفل الدردشة 🔒")

@app.on_message(filters.command("فتح")) # التعديل 2
async def unlock_cmd(client, message: Message):
    await app.set_chat_permissions(
        message.chat.id,
        ChatPermissions(can_send_messages=True)
    )
    await message.reply("تم فتح الدردشة 🔓")
