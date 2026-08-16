from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
import asyncio
import time
from config import ALL_ADMINS, PROTECTION, BAD_WORDS, MESSAGES

# ذاكرة مؤقتة لمكافحة التكرار
flood_db = {}

def is_admin_filter(_, __, message):
    return message.from_user and message.from_user.id in ALL_ADMINS

admin_filter = filters.create(is_admin_filter)

# ===== 1. اوامر الادارة =====
@Client.on_message(filters.command(["حظر", "ban"]) & admin_filter)
async def ban_user(c: Client, m):
    if not m.reply_to_message:
        return await m.reply("رد على رسالة العضو اللي تريد تحظره")

    user = m.reply_to_message.from_user
    chat_id = m.chat.id

    try:
        await c.ban_chat_member(chat_id, user.id)
        await m.reply(MESSAGES["user_banned"].format(user=user.mention))
    except ChatAdminRequired:
        await m.reply("❌ انا مش ادمن او ما عندي صلاحية الحظر")
    except UserAdminInvalid:
        await m.reply("❌ ما اقدر احظر ادمن")

@Client.on_message(filters.command(["كتم", "mute"]) & admin_filter)
async def mute_user(c: Client, m):
    if not m.reply_to_message:
        return await m.reply("رد على رسالة العضو اللي تريد تكتمه")

    user = m.reply_to_message.from_user
    chat_id = m.chat.id
    time_str = m.command[1] if len(m.command) > 1 else "1h" # افتراضي ساعة

    # تحويل الوقت لثواني
    seconds = 3600
    if "d" in time_str: seconds = int(time_str.replace("d","")) * 86400
    elif "h" in time_str: seconds = int(time_str.replace("h","")) * 3600
    elif "m" in time_str: seconds = int(time_str.replace("m","")) * 60

    until_date = int(time.time() + seconds)

    try:
        await c.restrict_chat_member(chat_id, user.id, ChatPermissions(), until_date=until_date)
        await m.reply(MESSAGES["user_muted"].format(user=user.mention, time=time_str))
    except Exception as e:
        await m.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.command(["فك_كتم", "unmute"]) & admin_filter)
async def unmute_user(c: Client, m):
    if not m.reply_to_message:
        return await m.reply("رد على رسالة العضو")

    user = m.reply_to_message.from_user
    chat_id = m.chat.id

    try:
        await c.restrict_chat_member(chat_id, user.id, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True
        ))
        await m.reply(f"✅ تم فك الكتم عن {user.mention}")
    except Exception as e:
        await m.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.command(["حذف", "del"]) & admin_filter)
async def delete_msgs(c: Client, m):
    count = int(m.command[1]) if len(m.command) > 1 else 1
    try:
        await c.delete_messages(m.chat.id, [m.id + i for i in range(-count, 1)])
    except:
        await m.reply("❌ ما قدرت احذف")

# ===== 2. الحماية التلقائية =====
@Client.on_message(filters.group & ~admin_filter)
async def auto_protect(c: Client, m):
    if not m.from_user: return

    user_id = m.from_user.id
    chat_id = m.chat.id

    # 1. حذف الروابط
    if PROTECTION["delete_links"] and ("http://" in m.text or "https://" in m.text or "t.me/" in m.text):
        await m.delete()
        return

    # 2. حذف السب
    if PROTECTION["delete_bad_words"] and m.text:
        text = m.text.lower()
        for word in BAD_WORDS:
            if word in text:
                await m.delete()
                await c.send_message(chat_id, f"{m.from_user.mention} ممنوع السب ❌")
                return

    # 3. مكافحة التكرار Flood
    if PROTECTION["anti_flood"]:
        key = f"{chat_id}:{user_id}"
        now = time.time()

        if key not in flood_db: flood_db[key] = []
        flood_db[key] = [t for t in flood_db[key] if now - t < 5] # اخر 5 ثواني
        flood_db[key].append(now)

        if len(flood_db[key]) > PROTECTION["flood_limit"]:
            await c.restrict_chat_member(chat_id, user_id, ChatPermissions(), until_date=int(now+300)) # كتم 5 دقايق
            await c.send_message(chat_id, f"{m.from_user.mention} تم كتمك 5 دقايق بسبب التكرار")
            flood_db[key] = []

print("✅ تم تحميل ملف الحماية protect.py")
