from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from bot import app
from modules.utils import has_permission
from database import cursor, conn

# دوال الحفظ
def lock(chat_id, lock_type):
    cursor.execute("INSERT OR IGNORE INTO locks VALUES (?,?)", (chat_id, lock_type)); conn.commit()

def unlock(chat_id, lock_type):
    cursor.execute("DELETE FROM locks WHERE chat_id=? AND lock_type=?", (chat_id, lock_type)); conn.commit()

def is_locked(chat_id, lock_type):
    cursor.execute("SELECT * FROM locks WHERE chat_id=? AND lock_type=?", (chat_id, lock_type))
    return cursor.fetchone() is not None

# ========== امر القفل والفتح ==========
@app.on_message(filters.group & filters.text)
async def lock_unlock(_, m: Message):
    chat_id = m.chat.id
    user_id = m.from_user.id
    text = m.text.strip()

    if not await has_permission(app, chat_id, user_id, "mod"): return

    lock_map = {
        "الروابط": "link", "الرابط": "link",
        "الصور": "photo", "الصورة": "photo",
        "الفيديو": "video", "الفيديوهات": "video",
        "الملصقات": "sticker", "الملصق": "sticker",
        "المتحركه": "animation", "المتحركة": "animation",
        "الكتابه": "text", "الكتابة": "text",
        "الدردشه": "chat", "الدردشة": "chat",
        "التاك": "mention", "المعرفات": "username", "المعرف": "username",
        "التوجيه": "forward", "البوتات": "bots",
        "الجهات": "contact", "الصوت": "voice", "الفويس": "voice"
    }

    if text.startswith("قفل "):
        item = text.split("قفل ")[1]
        if item == "الكل":
            for i in lock_map.values(): lock(chat_id, i)
            return await m.reply("🔒 تم قفل كل شي")
        if item in lock_map:
            lock(chat_id, lock_map[item])
            await m.reply(f"🔒 تم قفل {item}")

    elif text.startswith("فتح "):
        item = text.split("فتح ")[1]
        if item == "الكل":
            cursor.execute("DELETE FROM locks WHERE chat_id=?", (chat_id,)); conn.commit()
            return await m.reply("🔓 تم فتح كل شي")
        if item in lock_map:
            unlock(chat_id, lock_map[item])
            await m.reply(f"🔓 تم فتح {item}")

    # تفعيل وتعطيل
    elif text.startswith("تفعيل "):
        item = text.split("تفعيل ")[1]
        cursor.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (f"{chat_id}_{item}", "on")); conn.commit()
        await m.reply(f"✅ تم تفعيل {item}")

    elif text.startswith("تعطيل "):
        item = text.split("تعطيل ")[1]
        cursor.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (f"{chat_id}_{item}", "off")); conn.commit()
        await m.reply(f"❌ تم تعطيل {item}")

# ========== فلتر المسح التلقائي ==========
@app.on_message(filters.group)
async def anti_spam(_, m: Message):
    chat_id = m.chat.id

    # قفل الروابط
    if is_locked(chat_id, "link") and (m.entities or m.caption_entities):
        for entity in (m.entities or []) + (m.caption_entities or []):
            if entity.type in ["url", "text_link"]:
                await m.delete()
                return

    # قفل الصور
    if is_locked(chat_id, "photo") and m.photo:
        await m.delete(); return

    # قفل الفيديو
    if is_locked(chat_id, "video") and m.video:
        await m.delete(); return

    # قفل الملصقات
    if is_locked(chat_id, "sticker") and m.sticker:
        await m.delete(); return

    # قفل المتحركة
    if is_locked(chat_id, "animation") and m.animation:
        await m.delete(); return

    # قفل التوجيه
    if is_locked(chat_id, "forward") and m.forward_from:
        await m.delete(); return

    # قفل الجهات
    if is_locked(chat_id, "contact") and m.contact:
        await m.delete(); return

    # قفل الصوت
    if is_locked(chat_id, "voice") and m.voice:
        await m.delete(); return
