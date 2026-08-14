import time
from pyrogram import filters
from pyrogram.types import Message
from bot import app # مهم جدا

# أوامر الخدمات
@app.on_message(filters.command(["ايدي", "id", "الوقت", "الرابط"]) & filters.group)
async def service_commands(client, message: Message):
    cmd = message.command[0] # نجيب اول كلمة بس

    if cmd == "ايدي" or cmd == "id":
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            await message.reply(f"• أيدي المستخدم: `{user.id}`\n• اسم المستخدم: {user.mention}")
        else:
            await message.reply(f"• أيديك أنت: `{message.from_user.id}`\n• اسمك: {message.from_user.mention}")

    elif cmd == "الوقت":
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        await message.reply(f"• وقـت السيرفر الحالي UTC:\n`{current_time}`")

    elif cmd == "الرابط":
        try:
            invite_link = await client.export_chat_invite_link(message.chat.id)
            await message.reply(f"• رابط الدعوة للمجموعة:\n{invite_link}")
        except Exception:
            await message.reply("• عذراً، لازم اكون مشرف + عندي صلاحية اضافة اعضاء عشان اجيب الرابط!")
