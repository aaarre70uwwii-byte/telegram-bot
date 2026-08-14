from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from main import app  # <-- التعديل المهم

@app.on_message(filters.command("قفل"))
async def lock_cmd(client, message: Message):
    await app.set_chat_permissions(
        message.chat.id,
        ChatPermissions(can_send_messages=False)
    )
    await message.reply("تم قفل الدردشة 🔒")

@app.on_message(filters.command("فتح"))
async def unlock_cmd(client, message: Message):
    await app.set_chat_permissions(
        message.chat.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )
    await message.reply("تم فتح الدردشة 🔓")
