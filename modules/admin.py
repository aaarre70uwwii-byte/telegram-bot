from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from bot import app
from modules.utils import get_rank, set_rank, has_permission, can_action, rank_names
from database import cursor, conn # <-- ضفت هذا السطر المهم
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
        rank_map = {"مالك": "owner", "منشئ": "owner", "مدير": "mod", "ادمن": "mod", "مشرف": "mod", "مميز": "special"}
        if rank_name not in rank_map: return await m.reply("❌ رتبة غير موجودة")

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
            can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True))
        await m.reply(f"🔊 تم فك كتم {target.first_name}")

    elif text.startswith("تقييد "):
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        try:
            seconds = int(text.split(" ")[1])
            until = int(time.time()) + seconds
            await app.restrict_chat_member(chat_id, target_id, permissions=ChatPermissions(), until_date=until)
            await m.reply(f"⛓️ تم تقييد {target.first_name} لمدة {seconds} ثانية")
        except: await m.reply("❌ استخدم: تقييد 60")

    elif text == "رفع القيود":
        if not await has_permission(app, chat_id, user_id, "mod"):
            return await m.reply("❌ هذا الامر للمدير فما فوق")
        await app.restrict_chat_member(chat_id, target_id, permissions=ChatPermissions(
            can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True))
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

# ========== اوامر المسح ==========
@app.on_message(filters.group & filters.text)
async def delete_commands(_, m: Message):
    chat_id = m.chat.id
    user_id = m.from_user.id
    text = m.text.strip()

    if not await has_permission(app, chat_id, user_id, "mod"): return

    # مسح بالعدد
    if text.startswith("مسح ") and text.split(" ")[1].isdigit():
        count = int(text.split(" ")[1])
        if count > 100: count = 100
        msgs = [i.id for i in await app.get_chat_history(chat_id, limit=count+1)]
        await app.delete_messages(chat_id, msgs)
        msg = await m.reply(f"✅ تم مسح {count} رسالة")
        await asyncio.sleep(3); await msg.delete()

    # مسح بالرد
    elif text == "مسح بالرد" and m.reply_to_message:
        await app.delete_messages(chat_id, m.reply_to_message.id)
        await m.delete()

    # مسح الكل - اخر 100 رسالة
    elif text == "مسح الكل":
        msgs = [i.id for i in await app.get_chat_history(chat_id, limit=100)]
        await app.delete_messages(chat_id, msgs)
        msg = await m.reply("✅ تم مسح اخر 100 رسالة")
        await asyncio.sleep(3); await msg.delete()

    # مسح الرابط
    elif text == "مسح الرابط":
        if not await has_permission(app, chat_id, user_id, "owner"): return
        from modules.settings import save_setting
        save_setting(chat_id, "link", "")
        await m.reply("✅ تم مسح الرابط")

    # مسح الترحيب
    elif text == "مسح الترحيب":
        if not await has_permission(app, chat_id, user_id, "owner"): return
        from modules.settings import save_setting
        save_setting(chat_id, "welcome_text", "")
        save_setting(chat_id, "welcome_photo", "")
        await m.reply("✅ تم مسح الترحيب")

    # مسح الايدي
    elif text == "مسح الايدي":
        if not await has_permission(app, chat_id, user_id, "owner"): return
        from modules.settings import save_setting
        save_setting(chat_id, "id_template", "")
        await m.reply("✅ تم مسح الايدي")

    # مسح الردود
    elif text == "مسح الردود":
        if not await has_permission(app, chat_id, user_id, "owner"): return
        cursor.execute("DELETE FROM replies WHERE chat_id=?", (chat_id,)); conn.commit()
        await m.reply("✅ تم مسح جميع الردود")
