from pyrogram import filters
from pyrogram.types import Message
from bot import app
from modules.utils import has_permission
from database import cursor, conn

def save_setting(chat_id, key, value):
    cursor.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (f"{chat_id}_{key}", value)); conn.commit()

def get_setting(chat_id, key):
    cursor.execute("SELECT value FROM settings WHERE key=?", (f"{chat_id}_{key}",))
    r = cursor.fetchone()
    return r[0] if r else None

@app.on_message(filters.group & filters.text)
async def set_settings(_, m: Message):
    chat_id = m.chat.id
    user_id = m.from_user.id
    text = m.text.strip()
    if not await has_permission(app, chat_id, user_id, "owner"): return

    if text.startswith("ضع الرابط "):
        link = text.split("ضع الرابط ")[1]
        save_setting(chat_id, "link", link)
        await m.reply(f"✅ تم حفظ الرابط:\n{link}")
    elif text == "انشاء رابط":
        link = await app.export_chat_invite_link(chat_id)
        save_setting(chat_id, "link", link)
        await m.reply(f"✅ تم انشاء الرابط:\n{link}")

@app.on_message(filters.group & filters.text)
async def get_settings(_, m: Message):
    chat_id = m.chat.id
    text = m.text.strip()
    if text == "الرابط":
        link = get_setting(chat_id, "link")
        if link: await m.reply(f"🔗 رابط المجموعه:\n{link}")
        else: await m.reply("❌ لا يوجد رابط")

@app.on_message(filters.group & filters.new_chat_members)
async def welcome(_, m: Message):
    chat_id = m.chat.id
    welcome_text = get_setting(chat_id, "welcome_text")
    if not welcome_text: return
    for user in m.new_chat_members:
        name = user.first_name
        msg = welcome_text.replace("{name}", name)
        await m.reply(msg)
