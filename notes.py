from pyrogram import filters, Client
from pyrogram.types import Message
from database import conn, cursor, is_admin, is_dev

def setup(app: Client):
    @app.on_message(filters.group & filters.text)
    async def notes_group(_, message: Message):
        text = message.text; chat_id = message.chat.id
        if not text.startswith("/"): return

        parts = text.split(" ", 1)
        cmd = parts[0].lower()

        # حفظ ملاحظة
        if cmd in ["/حفظ", "/save"]:
            if not await is_admin(app, chat_id, message.from_user.id) and not is_dev(message.from_user.id): return
            if len(parts) < 2 or not message.reply_to_message:
                return await message.reply("الاستخدام: رد على رسالة واكتب `/حفظ اسم_الملاحظة`")
            name = parts[1]
            content = message.reply_to_message.text or message.reply_to_message.caption
            if not content: return await message.reply("❌ لازم ترد على نص او صورة فيها كلام")
            cursor.execute("REPLACE INTO notes (chat_id, name, content) VALUES (?,?,?)", (chat_id, name, content))
            conn.commit()
            await message.reply(f"✅ تم حفظ الملاحظة `{name}`")

        # جلب ملاحظة
        elif cmd == "/ملاحظة":
            if len(parts) < 2: return await message.reply("الاستخدام: `/ملاحظة الاسم`")
            name = parts[1]
            r = cursor.execute("SELECT content FROM notes WHERE chat_id=? AND name=?", (chat_id, name)).fetchone()
            if r: await message.reply(r[0])
            else: await message.reply("❌ الملاحظة غير موجودة")

        # حذف ملاحظة
        elif cmd in ["/حذف_ملاحظة", "/delnote"]:
            if not await is_admin(app, chat_id, message.from_user.id) and not is_dev(message.from_user.id): return
            if len(parts) < 2: return await message.reply("الاستخدام: `/حذف_ملاحظة الاسم`")
            cursor.execute("DELETE FROM notes WHERE chat_id=? AND name=?", (chat_id, parts[1]))
            conn.commit()
            await message.reply(f"🗑️ تم حذف الملاحظة `{parts[1]}`")

        # قائمة الملاحظات
        elif cmd in ["/الملاحظات", "/notes"]:
            notes = cursor.execute("SELECT name FROM notes WHERE chat_id=?", (chat_id,)).fetchall()
            if not notes: return await message.reply("❌ لا توجد ملاحظات")
            txt = "**📝 قائمة الملاحظات:**\n"
            for n in notes: txt += f"- `{n[0]}`\n"
            await message.reply(txt)
