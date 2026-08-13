from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from bot import app
from modules.utils import get_rank, set_rank, has_permission, can_action, rank_names
import asyncio

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
        rank_map = {"مالك": "owner", "منشئ": "owner", "مدير": "mod", "ادمن": "mod", "مشرف": "mod", "مميز": "special"}
        if rank_name not in rank_map: return

        if not await has_permission(app, chat_id, user_id, "owner"):
            return await m.reply("❌ هذا الامر للمالك فقط")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر على شخص رتبته اعلى منك")

        set_rank(chat_id, target_id, rank_map[rank_name])
        await m.reply(f"✅ تم رفع {target.first_name} {rank_name}")

    elif text == "تنزيل":
        if not await has_permission(app, chat_id, user_id, "owner"):
            return await m.reply("❌ هذا الامر للمالك فقط")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر على شخص رتبته اعلى منك")

        set_rank(chat_id, target_id, "member")
        await m.reply(f"✅ تم تنزيل {target.first_name}")

    elif text == "تنزيل الكل":
        if not await has_permission(app, chat_id, user_id, "owner"):
            return await m.reply("❌ هذا الامر للمالك فقط")
        cursor.execute("DELETE FROM admins WHERE chat_id=?", (chat_id,)); conn.commit()
        await m.reply("✅ تم تنزيل جميع الرتب")

    # ========== اوامر الحظر والطرد والكتم ==========
    elif text == "حظر":
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر على شخص رتبته اعلى منك")
        await app.ban_chat_member(chat_id, target_id)
        await m.reply(f"🚫 تم حظر {target.first_name}")

    elif text == "الغاء الحظر":
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        await app.unban_chat_member(chat_id, target_id)
        await m.reply(f"✅ تم فك حظر {target.first_name}")

    elif text == "طرد":
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر على شخص رتبته اعلى منك")
        await app.ban_chat_member(chat_id, target_id)
        await app.unban_chat_member(chat_id, target_id)
        await m.reply(f"👢 تم طرد {target.first_name}")

    elif text == "كتم":
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        if not await can_action(app, chat_id, user_id, target_id):
            return await m.reply("❌ ما تقدر على شخص رتبته اعلى منك")
        await app.restrict_chat_member(chat_id, target_id, permissions=ChatPermissions())
        await m.reply(f"🔇 تم كتم {target.first_name}")

    elif text == "الغاء الكتم":
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        await app.restrict_chat_member(chat_id, target_id, permissions=ChatPermissions(
            can_send_messages=True, can_send_media_messages=True, can_send_polls=True))
        await m.reply(f"🔊 تم فك كتم {target.first_name}")

    elif text.startswith("تقييد "):
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        time = int(text.split(" ")[1])
        await app.restrict_chat_member(chat_id, target_id, permissions=ChatPermissions(), until_date=time)
        await m.reply(f"⛓️ تم تقييد {target.first_name} لمدة {time} ثانية")

    elif text == "رفع القيود":
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        await app.restrict_chat_member(chat_id, target_id, permissions=ChatPermissions(
            can_send_messages=True, can_send_media_messages=True, can_send_polls=True))
        await m.reply(f"✅ تم فك التقييد عن {target.first_name}")

# امر عرض الرتب بدون رد
@app.on_message(filters.group & filters.text & filters.regex(r"^عرض الرتب$"))
async def show_ranks(_, m: Message):
    if not await has_permission(app, m.chat.id, m.from_user.id, "mod"): return
    cursor.execute("SELECT user_id, rank FROM admins WHERE chat_id=?", (m.chat.id,))
    admins = cursor.fetchall()
    if not admins: return await m.reply("لا يوجد رتب")
    txt = "📋 قائمة الرتب:\n"
    for uid, rank in admins:
        txt += f"- {rank_names.get(rank, rank)} : `{uid}`\n"
    await m.reply(txt)
