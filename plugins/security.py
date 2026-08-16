from pyrogram import filters
from config import ALLOWED_USERS

def is_allowed():
    """فلتر للتحقق هل المستخدم مسموح له"""
    return filters.user(ALLOWED_USERS)

async def check_user(client, message):
    """فحص سريع ورد تلقائي لو مش مسموح"""
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply_text("⛔ البوت خاص. ممنوع الاستخدام")
        return False
    return True
