from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio, time

app = Client.get_client("ProtectionBot")

# عشان يشتغل لازم نسوي ملف database.py و utils.py
# مؤقتا حطينا دوال وهمية عشان البوت يشتغل
def get_rank(chat_id, user_id): return "member"
def set_rank(chat_id, user_id, rank): pass
async def has_permission(app, chat_id, user_id, rank): return True
async def can_action(app, chat_id, user_id, target_id): return True
class cursor:
    def execute(*args): pass
class conn:
    def commit(): pass

# ========== اوامر الرفع والتنزيل ==========
@app.on_message(filters.group & filters.text & filters.reply)
async def admin_commands(_, m: Message):
    text = m.text.strip()
    chat_id = m.chat.id
    user_id = m.from_user.id
    target = m.reply_to_message.from_user
    target_id = target.id

    if target_id == (await app.get_me()).id: return

    if text.startswith("رفع "):
        rank_name = text.split("رفع ")[1]
        rank_map = {"مالك": "owner", "منشئ": "creator", "ادمن": "admin"}
        if rank_name not in rank_map: return await m.reply("❌ الرتب المتاحة: مالك, منشئ, ادمن")

        set_rank(chat_id, target_id, rank_map[rank_name])
        await m.reply(f"✅ تم رفع {target.first_name} الى {rank_name}")

    elif text == "تنزيل":
        set_rank(chat_id, target_id, "member")
        await m.reply(f"✅ تم تنزيل {target.first_name}")

    elif text == "تنزيل الكل":
        cursor.execute("DELETE FROM admins WHERE chat_id=?", (chat_id,))
        conn.commit()
        await m.reply("✅ تم تنزيل جميع الرتب")

    # ========== اوامر الحظر والط
