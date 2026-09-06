import os # اضفناه هنا
import sqlite3
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

conn = sqlite3.connect("/tmp/bot.db", check_same_thread=False)
cur = conn.cursor()

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    if update.effective_user.id == OWNER_ID: return True
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return m.status in ['creator','administrator']
    except: return False

async def get_rank(group_id, user_id):
    cur.execute("SELECT rank FROM ranks_admin WHERE group_id=? AND user_id=?",(group_id, user_id))
    res = cur.fetchall()
    if not res: return "عضو"
    ranks = [r[0] for r in res]
    if "owner_basic" in ranks: return "مالك اساسي"
    if "owner" in ranks: return "مالك"
    if "manager" in ranks: return "مدير"
    if "admin" in ranks: return "ادمن"
    return "عضو"

async def m2_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'private': return
    if not await is_admin(update, context):
        return

    msg = update.message
    text = msg.text.strip()
    chat_id = msg.chat.id

    # ===== 1. امر الرابط =====
    if text == "الرابط":
        cur.execute("SELECT link FROM group_settings WHERE group_id=?",(chat_id,))
        res = cur.fetchone()
        if res and res[0]:
            return await msg.reply_text(f"• رابط المجموعة:\n{res[0]}")
        else:
            return await msg.reply_text("• لا يوجد رابط. استخدم: تعيين الرابط + الرابط")

    if text.startswith("تعيين الرابط "):
        link = text.replace("تعيين الرابط ", "", 1)
        cur.execute("INSERT OR REPLACE INTO group_settings (group_id, link) VALUES (?,?)",(chat_id, link))
        conn.commit()
        return await msg.reply_text("• تم حفظ الرابط ✅")

    # ===== 2. امر الايدي =====
    if text == "الايدي":
        user = msg.from_user
        rank = await get_rank(chat_id, user.id)
        return await msg.reply_text(
            f"• ايديك: `{user.id}`\n"
            f"• اسمك: {user.first_name}\n"
            f"• معرفك: @{user.username if user.username else 'لا يوجد'}\n"
            f"• رتبتك: {rank}",
            parse_mode="Markdown"
        )

    # ===== 3. امر المعلومات =====
    if text == "معلومات":
        if not msg.reply_to_message:
            return await msg.reply_text("• رد على الشخص")
        user = msg.reply_to_message.from_user
        rank = await get_rank(chat_id, user.id)
        return await msg.reply_text(
            f"• المعلومات:\n"
            f"• الاسم: {user.first_name}\n"
            f"• الايدي: `{user.id}`\n"
            f"• المعرف: @{user.username if user.username else 'لا يوجد'}\n"
            f"• الرتبة: {rank}",
            parse_mode="Markdown"
        )

    # ===== 4. امر الرتب =====
    if text == "الرتب":
        if not msg.reply_to_message:
            return await msg.reply_text("• رد على الشخص")
        user_id = msg.reply_to_message.from_user.id
        rank = await get_rank(chat_id, user_id)
        return await msg.reply_text(f"• رتبة العضو: {rank}")

    # ===== 5. امر المشرفين =====
    if text == "المشرفين":
        cur.execute("SELECT user_id, rank FROM ranks_admin WHERE group_id=?",(chat_id,))
        res = cur.fetchall()
        if not res: return await msg.reply_text("• لا يوجد مرفوعين")

        owners = []; managers = []; admins = []
        for user_id, rank in res:
            if rank == "owner_basic": owners.append(f"• مالك اساسي: `{user_id}`")
            elif rank == "owner": owners.append(f"• مالك: `{user_id}`")
            elif rank == "manager": managers.append(f"• مدير: `{user_id}`")
            elif rank == "admin": admins.append(f"• ادمن: `{user_id}`")

        final = "• قائمة المرفوعين:\n\n"
        final += "\n".join(owners + managers + admins)
        return await msg.reply_text(final, parse_mode="Markdown")

    # ===== 6. اوامر التثبيت =====
    if text == "تثبيت":
        if not msg.reply_to_message:
            return await msg.reply_text("• رد على الرسالة")
        await context.bot.pin_chat_message(chat_id, msg.reply_to_message.message_id)
        return await msg.reply_text("• تم تثبيت الرسالة ✅")

    if text == "الغاء التثبيت":
        await context.bot.unpin_chat_message(chat_id)
        return await msg.reply_text("• تم الغاء تثبيت الرسالة ✅")

    # ===== 7. اوامر الردود =====
    if text.startswith("اضف رد "):
        try:
            word, reply = text.replace("اضف رد ", "", 1).split(" - ", 1)
            cur.execute("INSERT OR REPLACE INTO replies VALUES (?,?,?)",(chat_id, word.strip(), reply.strip()))
            conn.commit()
            return await msg.reply_text(f"• تم اضافة رد للكلمة: {word} ✅")
        except:
            return await msg.reply_text("• الصيغة غلط. استخدم: اضف رد الكلمة - الرد")

    if text.startswith("حذف رد "):
        word = text.replace("حذف رد ", "", 1)
        cur.execute("DELETE FROM replies WHERE group_id=? AND word=?",(chat_id, word))
        conn.commit()
        return await msg.reply_text(f"• تم حذف رد {word} ✅")

    # رد تلقائي
    cur.execute("SELECT reply FROM replies WHERE group_id=? AND word=?",(chat_id, text))
    res = cur.fetchone()
    if res:
        return await msg.reply_text(res[0])

    # ===== 8. اوامر القفل والفتح =====
    if text.startswith("قفل "):
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=False if "الصور" in text else True,
            can_add_web_page_previews=False if "الروابط" in text else True,
            can_send_other_messages=False if "الكيبورد" in text else True,
        )
        await context.bot.set_chat_permissions(chat_id, permissions=perms)
        return await msg.reply_text(f"• تم {text} ✅")

    if text.startswith("فتح "):
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_add_web_page_previews=True,
            can_send_other_messages=True,
        )
        await context.bot.set_chat_permissions(chat_id, permissions=perms)
        return await msg.reply_text(f"• تم {text} ✅")

    # ===== 9. عرض الاعدادات =====
    if text == "الاعدادات":
        cur.execute("SELECT link FROM group_settings WHERE group_id=?",(chat_id,))
        link = cur.fetchone()
        link = link[0] if link and link[0] else "لا يوجد"
        return await msg.reply_text(f"• اعدادات المجموعة:\nالرابط: {link}")
