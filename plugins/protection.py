import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions # مهم نضيف ChatPermissions

# قائمة الكلمات المحظورة
BAD_WORDS = ["كس", "خرا", "شرموط", "عاهرة", "كلب", "حمار", "تنزيل وزني", "اضغط على الرابط"]

# فحص الروابط والمعرفات
URL_REGEX = r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|@\w+)"

# تخزين التحذيرات مؤقت - يتمسح لو طفيت البوت
warnings = {}

@Client.on_message(filters.group & ~filters.service, group=1)
async def advanced_protection(client: Client, message: Message):
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # استثناء المشرفين والمالك
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in ["administrator", "creator"]:
            return
    except Exception:
        pass

    text = message.text or message.caption or ""
    
    # 1. فحص الروابط والمعرفات
    if re.search(URL_REGEX, text, re.IGNORECASE):
        await message.delete()
        return await warn_or_punish(client, message, "ممنوع نشر الروابط أو المعرفات هنا! 🚫")

    # 2. فحص الكلمات البذيئة
    if any(word in text.lower() for word in BAD_WORDS):
        await message.delete()
        return await warn_or_punish(client, message, "يرجى احترام الآخرين وعدم استخدام ألفاظ سيئة! ⚠️")

    # 3. فحص الرسائل الطويلة
    if len(text) > 500:
        await message.delete()
        return await warn_or_punish(client, message, "يمنع إرسال رسائل طويلة جداً! ⚠️")

async def warn_or_punish(client: Client, message: Message, reason: str):
    chat_id = message.chat.id
    user = message.from_user
    user_key = f"{chat_id}_{user.id}"
    
    warnings[user_key] = warnings.get(user_key, 0) + 1
    count = warnings[user_key]
    
    if count >= 3:
        # كتم تلقائي بعد 3 تحذيرات
        try:
            await client.restrict_chat_member(
                chat_id=chat_id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False) # استخدمناه من فوق
            )
            warnings[user_key] = 0
            await client.send_message(
                chat_id, 
                f"🔇 العضو {user.mention} تم كتمه تلقائياً لتجاوزه حد التحذيرات (3/3)!"
            )
        except Exception as e:
            await client.send_message(chat_id, f"عجزت عن كتم العضو بسبب نقص الصلاحيات: {e}")
    else:
        # تحذير مؤقت وينحذف بعد 5 ثواني
        warn_msg = await client.send_message(
            chat_id, 
            f"التحذير ({count}/3) | {user.mention}\nالسبب: {reason}"
        )
        await asyncio.sleep(5)
        await warn_msg.delete()
