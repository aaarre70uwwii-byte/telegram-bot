from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatPermissions

app = Client.get_client("ProtectionBot")

@app.on_message(commands=["قفل"])
async def lock_cmd(client, message: Message):
    await message.reply("تم قفل الدردشة 🔒")
    await app.set_chat_permissions(
        message.chat.id,
        ChatPermissions(can_send_messages=False)
    )

@app.on_message(commands=["فتح"])
async def unlock_cmd(client, message: Message):
    await message.reply("تم فتح الدردشة 🔓")
    await app.set_chat_permissions(
        message.chat.id,
        ChatPermissions(can_send_messages=True)
    )
