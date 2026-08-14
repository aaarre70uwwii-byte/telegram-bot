from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio, time

app = Client.get_client("ProtectionBot")

# قاعدة بيانات مؤقتة لحد ما نسوي database.py
admins_db = {}

def get_rank(chat_id, user_id):
    return admins_db.get(chat_id, {}).get(user_id, "member")

def set_rank(chat_id, user_id, rank):
    admins_db.setdefault(chat_id, {})[user_id] = rank

async def has_permission(app, chat_id, user_id, rank):
    return True # مؤقتا الكل يقدر

async def can_action(app, chat_id, user_id, target_id):
    return True # مؤقتا الكل يقدر

class cursor:
    @staticmethod
    def execute(*args):
        if "DELETE" in args[0]:
            chat_id = args[1][0]
            admins_db[chat_id] = {}

class conn:
    @staticmethod
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

    # ========== اوامر الحظر والطرد ==========
    elif text == "حظر":
        await app.ban_chat_member(chat_id, target_id)
        await m.reply(f"🚫 تم حظر {target.first_name}")

    elif text == "الغاء الحظر":
        await app.unban_chat_member(chat_id, target_id)
        await m.reply(f"✅ تم فك الحظر عن {target.first_name}")

    elif text == "طرد":
        await app.ban_chat_member(chat_id, target_id)
        await app.unban_chat_member(chat_id, target_id)
        await m.reply(f"👢 تم طرد {target.first_name}")

    # ========== اوامر الكتم ==========
    elif text == "كتم":
        await app.restrict_chat_member(chat_id, target_id, ChatPermissions())
        await m.reply(f"🔇 تم كتم {target.first_name}")

    elif text == "الغاء الكتم":
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        await app.restrict_chat_member(chat_id, target_id, perms)
        await m.reply(f"🔊 تم فك الكتم عن {target.first_name}")
