from pyrogram import filters
from bot import app
from modules.database import get_lock

@app.on_message(filters.group & ~filters.service)
async def check_locks(client, message):
    if not message.from_user: return
    chat_id = message.chat.id

    # لو الادمن ما نحذف
    member = await client.get_chat_member(chat_id, message.from_user.id)
    if member.status in ["owner", "administrator"]: return

    # فحص قفل الروابط
    if get_lock(chat_id, "روابط") == "قفله" and message.text and ("http://" in message.text or "https://" in message.text or "t.me/" in message.text):
        await message.delete()
        await message.reply(f"{message.from_user.mention} ممنوع نشر الروابط هنا! ❌")

    # فحص قفل الصور
    if get_lock(chat_id, "صور") == "قفله" and message.photo:
        await message.delete()
        await message.reply(f"{message.from_user.mention} ممنوع الصور هنا! ❌")
