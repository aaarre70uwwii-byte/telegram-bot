from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatPermissions
from database import is_dev, conn, cursor
from modules.utils import admin_keyboard, is_admin
import time

def setup(app: Client):
    @app.on_message(filters.text & filters.private)
    async def private_admin(_, message: Message):
        if not is_dev(message.from_user.id): return
        if message.text == "👮 الادمنية":
            await message.reply("استخدم الازرار في المجموعة بالرد", reply_markup=admin_keyboard())
        elif message.text == "رجوع":
            from modules.utils import dev_keyboard
            await message.reply("رجعنا", reply_markup=dev_keyboard())

    @app.on_message(filters.group & filters.text)
    async def group_commands(_, message: Message):
        text = message.text; chat_id = message.chat.id; user_id = message.from_user.id

        if text in ["ايدي", "/id", "🆔 ايدي"]:
            await message.reply(f"🆔 ايديك: `{user_id}`\n👤 {message.from_user.first_name}")

        if text.startswith("همسه") or text.startswith(".همسه"):
            parts = text.split(" ", 2)
            if len(parts) < 3: return await message.reply("الاستخدام: `همسه @username النص`")
            try:
                to_user = await app.get_users(parts[1].replace("@",""))
                cursor.execute("INSERT INTO whispers (to_id, from_id, text) VALUES (?,?,?)", (to_user.id, user_id, parts[2]))
                conn.commit()
                await message.reply(f"✅ تم ارسال همسة سرية لـ {to_user.first_name}")
            except: await message.reply("❌ المستخدم غير موجود")
            return

        if not message.reply_to_message: return
        if not await is_admin(app, chat_id, user_id) and not is_dev(user_id): return
        target = message.reply_to_message.from_user.id

        if text in ["حظر", "🚫 حظر"]: await app.ban_chat_member(chat_id, target); await message.reply("✅ تم الحظر")
        elif text in ["الغاء الحظر", "✅ فك حظر"]: await app.unban_chat_member(chat_id, target); await message.reply("✅ تم فك الحظر")
        elif text in ["كتم", "🔇 كتم"]: await app.restrict_chat_member(chat_id, target, ChatPermissions()); await message.reply("✅ تم الكتم")
        elif text in ["الغاء الكتم", "🔊 فك كتم"]: await app.restrict_chat_member(chat_id, target, ChatPermissions(can_send_messages=True)); await message.reply("✅ تم فك الكتم")
        elif text in ["طرد", "👢 طرد"]: await app.ban_chat_member(chat_id, target); await app.unban_chat_member(chat_id, target); await message.reply("✅ تم الطرد")

    @app.on_message(filters.command("همستي") & filters.private)
    async def my_whisper(_, message: Message):
        r = cursor.execute("SELECT text, from_id FROM whispers WHERE to_id=? ORDER BY id DESC LIMIT 1", (message.from_user.id,)).fetchone()
        if r:
            from_user = await app.get_users(r[1])
            await message.reply(f"📩 همسة من {from_user.first_name}:\n`{r[0]}`")
            cursor.execute("DELETE FROM whispers WHERE to_id=?", (message.from_user.id,)); conn.commit()
        else: await message.reply("❌ لا توجد همسات")
