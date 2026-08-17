from config import ADMIN_ID
from pyrogram.types import Message

def is_admin(user_id: int) -> bool:
    """هل هذا ادمن؟"""
    return user_id == ADMIN_ID

async def get_target_user(message: Message) -> tuple:
    """يجيب ايدي واسم العضو اللي تم الرد عليه"""
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        return user.id, user.first_name
    return None, None

async def delete_msg(message: Message):
    """حذف رسالة مع تجاهل الخطأ"""
    try:
        await message.delete()
    except:
        pass
