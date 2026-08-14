from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from bot import app # اهم سطر

# ذاكرة مؤقتة بسيطة لحالة الأقسام في المجموعات
locked_groups = {}

# دالة مساعدة للتحقق من أن المستخدم إداري
async def is_admin(client, message: Message) -> bool:
    if not message.from_user:
        return False
    if message.chat.type == "private":
        return True
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]

# أمر قفل أو فتح ميزة
@app.on_message(filters.command(["قفل", "فتح"]) & filters.group)
async def toggle_protection(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("❌ هذا الأمر للإداريين فقط.")

    command = message.command[0] # قفل أو فتح
    target = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    chat_id = message.chat.id

    if chat_id not in locked_groups:
        locked_groups[chat_id] = {"روابط": False, "توجيه": False, "صور": False}

    status = True if command == "قفل" else False

    if target in ["روابط", "توجيه", "صور"]:
        locked_groups[chat_id][target] = status
        action_text = "تم قفله بنجاح 🔒" if status else "تم فتحه بنجاح 🔓"
        await message.reply(f"▫️ قسم ال{target} {action_text}")
    else:
        await message.reply("⚠️ استعمل: `قفل روابط` أو `قفل توجيه` أو `قفل صور`")

# مراقبة وحذف الرسائل المخالفة
@app.on_message(filters.group & ~filters.service)
async def check_locks(client, message: Message):
    if not message.chat or not message.from_user:
        return

    if await is_admin(client, message): # استثناء الأدمن
        return

    chat_id = message.chat.id
    if chat_id in locked_groups:
        # فحص قفل الروابط
        if locked_groups[chat_id].get("روابط", False) and message.text and ("http://" in message.text or "https://" in message.text or "t.me/" in message.text):
            await message.delete()
            await message.reply(f"👤 {message.from_user.mention} ممنوع نشر الروابط هنا! ❌", disable_web_page_preview=True)

        # فحص قفل التوجيه
        elif locked_groups[chat_id].get("توجيه", False) and message.forward_from:
            await message.delete()
            await message.reply(f"👤 {message.from_user.mention} ممنوع إعادة التوجيه هنا! ❌")

        # فحص قفل الصور
        elif locked_groups[chat_id].get("صور", False) and message.photo:
            await message.delete()
            await message.reply(f"👤 {message.from_user.mention} ممنوع إرسال الصور هنا! ❌")
