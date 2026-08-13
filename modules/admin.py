from pyrogram import filters
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from bot import app
from modules.utils import get_rank, set_rank, has_permission, can_action
from database import cursor, conn
import asyncio, time

# فلتر يمسك كل الاوامر بالرد
@app.on_message(filters.group & filters.text & filters.reply)
async def admin_commands(_, m: Message):
    text = m.text.strip()
    chat_id = m.chat.id
    user_id = m.from_user.id
    target = m.reply_to_message.from_user
    target_id = target.id

    if target_id == (await app.get_me()).id: return

    # ========== اوامر الرفع والتنزيل ==========
    if text.startswith("رفع "):
        rank_name = text.split("رفع ")[1]
        rank_map = {"مالك": "owner", "منشئ": "creator", "ادمن": "admin"}
        if rank_name not in rank_map: return await m.reply("❌ الرتب المتاحة: مالك, منشئ, ادمن")

        if not await has_permission(app, chat_id, user_id, rank_map[rank_name]):
            return await m.reply("❌ هذا الامر للمالك فقط")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر ترفع شخص رتبته اعلى منك")

        set_rank(chat_id, target_id, rank_map[rank_name])
        await m.reply(f"✅ تم رفع {target.first_name} الى {rank_name}")

    elif text == "تنزيل":
        if not await has_permission(app, chat_id, user_id, "owner"):
            return await m.reply("❌ هذا الامر للمالك فقط")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر تنزل شخص رتبته اعلى منك")

        set_rank(chat_id, target_id, "member")
        await m.reply(f"✅ تم تنزيل {target.first_name}")

    elif text == "تنزيل الكل":
        if not await has_permission(app, chat_id, user_id, "owner"):
            return await m.reply("❌ هذا الامر للمالك فقط")
        cursor.execute("DELETE FROM admins WHERE chat_id=?", (chat_id,))
        conn.commit()
        await m.reply("✅ تم تنزيل جميع الرتب")

    # ========== اوامر الحظر والطرد والكتم ==========
    elif text == "حظر":
        if not await has_permission(app, chat_id, user_id, "admin"):
            return await m.reply("❌ هذا الامر للادمن فما فوق")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر تحظر شخص رتبته اعلى منك")
        await app.ban_chat_member(chat_id, target_id)
        await m.reply(f"✅ تم حظر {target.first_name}")

    elif text == "الغاء الحظر":
        if not await has_permission(app, chat_id, user_id, "admin"):
            return await m.reply("❌ هذا الامر للادمن فما فوق")
        await app.unban_chat_member(chat_id, target_id)
        await m.reply(f"✅ تم فك الحظر عن {target.first_name}")

    elif text == "كتم":
        if not await has_permission(app, chat_id, user_id, "admin"):
            return await m.reply("❌ هذا الامر للادمن فما فوق")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر تكتم شخص رتبته اعلى منك")
        await app.restrict_chat_member(chat_id, target_id, ChatPermissions())
        await m.reply(f"🔇 تم كتم {target.first_name}")

    elif text == "الغاء الكتم":
        if not await has_permission(app, chat_id, user_id, "admin"):
            return await m.reply("❌ هذا الامر للادمن فما فوق")
        perms = ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True
        )
        await app.restrict_chat_member(chat_id, target_id, perms)
        await m.reply(f"🔊 تم فك الكتم عن {target.first_name}")

# ========== اوامر بدون رد ==========
@app.on_message(filters.command("id"))
async def id_cmd(client, message):
    user = message.from_user
    await message.reply(f"**👤 اسمك:** {user.first_name}\n**🆔 ايديك:** `{user.id}`")

# لوحة التحكم المدمجة
@app.on_message(filters.command("الاوامر"))
async def control_panel(client, message):
    text = """
**📜 لوحة تحكم المطور Tia**

**كل الاوامر بالرد على الشخص:**
`حظر` `الغاء الحظر` `كتم` `الغاء الكتم`
`رفع مالك` `رفع منشئ` `رفع ادمن` `تنزيل`

اضغط على الازرار تحت للمساعدة:
"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 الرتب", callback_data="ranks"),
         InlineKeyboardButton("🛡️ الحظر", callback_data="ban")],
        [InlineKeyboardButton("🔇 الكتم", callback_data="mute"),
         InlineKeyboardButton("ℹ️ معلومات", callback_data="info")]
    ])
    await message.reply(text, reply_markup=keyboard)
