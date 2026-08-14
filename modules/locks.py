from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from bot import app
from modules.database import set_lock, get_lock

# دالة التحقق من الادمن
async def is_admin(client, message):
    if message.chat.type == "private": return True
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]

@app.on_message(filters.command(["قفل", "فتح"]) & filters.group)
async def handle_locks(client, message):
    if not await is_admin(client, message):
        return await message.reply("❌ هذا الأمر للإداريين فقط.")

    action = message.command[0]
    target = " ".join(message.command[1:])
    chat_id = message.chat.id

    # الاشياء اللي نقدر نقفلها
    allowed_locks = ["روابط", "توجيه", "صور", "فيديو", "ملصقات"]
    if target not in allowed_locks:
        return await message.reply(f"⚠️ استخدم: `قفل روابط` او `قفل توجيه` او `قفل صور`\nالمتاح: {', '.join(allowed_locks)}")

    status = "قفله" if action == "قفل" else "فتحه"
    set_lock(chat_id, target, status)

    icon = "🔒" if status == "قفله" else "🔓"
    await message.reply(f"• تم {action} {target} {icon}")
