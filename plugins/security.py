from pyrogram import Client, filters
from utils import db, has_link, has_banned_word, check_flood, delete_msg, log_action
from config import ADMIN_ID, MAX_WARNS

# 1. منع المحظورين والمكتومين من الكتابة
@Client.on_message(filters.group & ~filters.user(ADMIN_ID))
async def anti_banned_muted(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    user = db.get_user(user_id, chat_id)
    if user[3] == 1: # banned
        await delete_msg(message)
        return
    if user[4] == 1: # muted
        await delete_msg(message)
        await message.reply(f"🔇 {message.from_user.mention} انت مكتوم")
        return

# 2. مضاد الروابط
@Client.on_message(filters.group & ~filters.user(ADMIN_ID))
async def anti_link(client, message):
    if has_link(message.text):
        await delete_msg(message)
        await log_action("DELETE_LINK", 0, message.from_user.id, message.chat.id)
        await message.reply(f"🚫 {message.from_user.mention} ممنوع ارسال الروابط")

# 3. مضاد الكلمات الممنوعة
@Client.on_message(filters.group & ~filters.user(ADMIN_ID))
async def anti_words(client, message):
    found, word = has_banned_word(message.text)
    if found:
        await delete_msg(message)
        await log_action(f"DELETE_WORD:{word}", 0, message.from_user.id, message.chat.id)
        await message.reply(f"🚫 {message.from_user.mention} ممنوع كلمة `{word}`")

# 4. مضاد السبام / التكرار
@Client.on_message(filters.group & ~filters.user(ADMIN_ID))
async def anti_flood(client, message):
    if check_flood(message.from_user.id):
        user_id = message.from_user.id
        chat_id = message.chat.id

        await client.ban_chat_member(chat_id, user_id)
        db.update(user_id, chat_id, "banned", 1)
        await log_action("BAN_FLOOD", 0, user_id, chat_id)
        await message.reply(f"🚫 تم حظر {message.from_user.mention} تلقائي بسبب السبام")

# 5. منع الملصقات والصور لو حبيت تفعله بعدين
@Client.on_message(filters.group & filters.sticker & ~filters.user(ADMIN_ID))
async def anti_sticker(client, message):
    # فعل هذا لو تبي منع الملصقات
    # await delete_msg(message)
    pass
