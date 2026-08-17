from pyrogram import Client, filters
from utils import db, is_admin, get_target_user, log_action
from config import MAX_WARNS

@Client.on_message(filters.command("ban") & filters.group)
async def ban_cmd(client, message):
    if not is_admin(message.from_user.id): return
    user_id, name = await get_target_user(message)
    if not user_id: return await message.reply("❌ رد على رسالة العضو")
    
    await client.ban_chat_member(message.chat.id, user_id)
    db.update(user_id, message.chat.id, "banned", 1)
    await log_action("BAN", message.from_user.id, user_id, message.chat.id)
    await message.reply(f"✅ تم حظر {name}")

@Client.on_message(filters.command("unban") & filters.group)
async def unban_cmd(client, message):
    if not is_admin(message.from_user.id): return
    user_id, name = await get_target_user(message)
    if not user_id: return await message.reply("❌ رد على رسالة العضو")

    await client.unban_chat_member(message.chat.id, user_id)
    db.update(user_id, message.chat.id, "banned", 0)
    await log_action("UNBAN", message.from_user.id, user_id, message.chat.id)
    await message.reply(f"✅ تم فك الحظر عن {name}")

@Client.on_message(filters.command("mute") & filters.group)
async def mute_cmd(client, message):
    if not is_admin(message.from_user.id): return
    user_id, name = await get_target_user(message)
    if not user_id: return await message.reply("❌ رد على رسالة العضو")

    db.update(user_id, message.chat.id, "muted", 1)
    await log_action("MUTE", message.from_user.id, user_id, message.chat.id)
    await message.reply(f"🔇 تم كتم {name}")

@Client.on_message(filters.command("unmute") & filters.group)
async def unmute_cmd(client, message):
    if not is_admin(message.from_user.id): return
    user_id, name = await get_target_user(message)
    if not user_id: return await message.reply("❌ رد على رسالة العضو")

    db.update(user_id, message.chat.id, "muted", 0)
    await log_action("UNMUTE", message.from_user.id, user_id, message.chat.id)
    await message.reply(f"🔊 تم فك الكتم عن {name}")
