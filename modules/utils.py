from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from pyrogram.enums import ChatMemberStatus

def dev_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📊 الاحصائيات")],
        [KeyboardButton("✅ تفعيل الخدمي"), KeyboardButton("❌ تعطيل الخدمي")],
        [KeyboardButton("🛡️ الحماية"), KeyboardButton("📋 الخدمي")],
        [KeyboardButton("👮 الادمنية"), KeyboardButton("📢 اذاعة")],
        [KeyboardButton("🗑️ اخفاء")]
    ], resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("⬆️ رفع ادمن"), KeyboardButton("⬇️ تنزيل ادمن")],
        [KeyboardButton("🚫 حظر"), KeyboardButton("✅ فك حظر")],
        [KeyboardButton("🔇 كتم"), KeyboardButton("🔊 فك كتم")],
        [KeyboardButton("👢 طرد"), KeyboardButton("⛔ تقييد")],
        [KeyboardButton("🆔 ايدي"), KeyboardButton("📩 همسة")],
        [KeyboardButton("رجوع")]
    ], resize_keyboard=True)

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False
