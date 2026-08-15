from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
import re

# الاعدادات
BANNED_WORDS = ["كلمة1", "كلمة2", "سب", "شرموط"]
BANNED_LINKS = True  # True = يحذف الروابط | False = يسمح
LOCK_USERNAME = True # منع @يوزرات

# 1. حذف الروابط
@Client.on_message(filters.group & filters.regex(r"(https?://|t\.me/|telegram\.me/)") & BANNED_LINKS)
async def delete_links(client, message):
    try:
        await message.delete()
        warn = await message.reply_text(f"🚫 {message.from_user.mention} ممنوع نشر الروابط")
        await warn.delete(5) # يحذف التحذير بعد 5 ثواني
    except: pass

# 2. منع اليوزرات @
@Client.on_message(filters.group & filters.regex(r"@") & LOCK_USERNAME)
async def delete_mention(client, message):
    try:
        await message.delete()
        warn = await message.reply_text(f"🚫 {message.from_user.mention} ممنوع المنشن")
        await warn.delete(5)
    except: pass

# 3. حذف السب والكلمات الممنوعة
@Client.on_message(filters.group & filters.text)
async def filter_words(client, message):
    text = message.text.lower()
    for word in BANNED_WORDS:
        if word in text:
            try:
                await message.delete()
                warn = await message.reply_text(f"🚫 {message.from_user.mention} ممنوع السب")
                await warn.delete(5)
            except: pass
            break

# 4. أوامر الادمن
def admin_only(func):
    async def wrapper(client, message):
        if not message.from_user: return
        member = await message.chat.get_member(message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            return await message.reply_text("هذا الامر للمشرفين فقط")
        return await func(client, message)
    return wrapper

@Client.on_message(filters.command("ban") & filters.group)
@admin_only
