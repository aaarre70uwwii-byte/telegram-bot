import os
import sqlite3
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

# تعديل: حطينا قاعدة البيانات في /tmp عشان Railway
conn = sqlite3.connect("/tmp/bot.db", check_same_thread=False)
cur = conn.cursor()
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# ===== الجداول =====
cur.execute("CREATE TABLE IF NOT EXISTS ranks_admin (group_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY(group_id,user_id,rank))")
cur.execute("CREATE TABLE IF NOT EXISTS banned (group_id INTEGER, user_id INTEGER, PRIMARY KEY(group_id,user_id))")
cur.execute("CREATE TABLE IF NOT EXISTS muted (group_id INTEGER, user_id INTEGER, PRIMARY KEY(group_id,user_id))")
cur.execute("CREATE TABLE IF NOT EXISTS replies (group_id INTEGER, word TEXT, reply TEXT, PRIMARY KEY(group_id,word))")
cur.execute("CREATE TABLE IF NOT EXISTS group_settings (group_id INTEGER PRIMARY KEY, link TEXT)")
conn.commit()

RANKS_ADMIN = {
    "مالك اساسي": "owner_basic",
    "مالك": "owner",
    "مدير": "manager",
    "ادمن": "admin"
}

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID: return True
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return m.status in ['creator','administrator']
    except: return False

async def get_target(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id
    parts = update.message.text.split()
    if len(parts) > 1 and parts[1].isdigit():
        return int(parts[1])
    return None

async def m1_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'private': return
    if not await is_admin(update, context):
        return

    msg = update.message
    text = msg.text.strip()
    chat_id = msg.chat.id
    target = await get_target(update)

    # ===== 1. اوامر الرفع والتنزيل =====
    for name, rank in RANKS_ADMIN.items():
        if text == f"رفع {name}" and target:
            cur.execute("INSERT OR IGNORE INTO ranks_admin VALUES (?,?,?)",(chat_id,target,rank))
            conn.commit()
            return await msg.reply_text(f"• تم رفع العضو الى {name} ✅")
        if text == f"تنزيل {name}" and target:
            cur.execute("DELETE FROM ranks_admin WHERE group_id=? AND user_id=? AND rank=?",(chat_id,target,rank))
            conn.commit()
            return await msg.reply_text(f"• تم تنزيل العضو من {name} ✅")

    if text == "تنزيل الكل" and target:
        cur.execute("DELETE FROM ranks_admin WHERE group_id=? AND user_id=?",(chat_id,target))
        conn.commit()
        return await msg.reply_text("• تم ازالة جميع رتب العضو ✅")

    # ===== 2. اوامر المسح =====
    if text == "مسح الكل":
        cur.execute("DELETE FROM ranks_admin WHERE group_id=?",(chat_id,))
        cur.execute("DELETE FROM banned WHERE group_id=?",(chat_id,))
        cur.execute("DELETE FROM muted WHERE group_id=?",(chat_id,))
        cur.execute("DELETE FROM replies WHERE group_id=?",(chat_id,))
        conn.commit()
        return await msg.reply_text("• تم مسح الكل: الرتب + المحظورين + المكتومين + الردود ✅")

    if text == "مسح المالكين":
        cur.execute("DELETE FROM ranks_admin WHERE group_id=? AND rank IN ('owner','owner_basic')",(chat_id,))
        conn.commit()
        return await msg.reply_text("• تم مسح المالكين ✅")

    if text == "مسح المحظورين":
        cur.execute("DELETE FROM banned WHERE group_id=?",(chat_id,))
        conn.commit()
        return await msg.reply_text("• تم مسح قائمة المحظورين ✅")

    if text == "مسح المكتومين":
        cur.execute("DELETE FROM muted WHERE group_id=?",(chat_id,))
        conn.commit()
        return await msg.reply_text("• تم مسح قائمة المكتومين ✅")

    if text == "مسح الردود":
        cur.execute("DELETE FROM replies WHERE group_id=?",(chat_id,))
        conn.commit()
        return await msg.reply_text("• تم مسح جميع الردود ✅")

    if text.startswith("مسح ") and text[4:].isdigit():
        count = int(text[4:])
        if count > 100: return await msg.reply_text("• اقصى شي 100 رسالة")
        try:
            await context.bot.delete_messages(chat_id, list(range(msg.message_id - count, msg.message_id + 1)))
            return await msg.reply_text(f"• تم مسح {count} رسالة ✅")
        except: return await msg.reply_text("• مقدر امسح الرسائل")

    if text == "مسح الايدي":
        cur.execute("DELETE FROM group_settings WHERE group_id=?",(chat_id,))
        conn.commit()
        return await msg.reply_text("• تم مسح الايدي ✅")

    if text == "مسح الرابط":
        cur.execute("UPDATE group_settings SET link=NULL WHERE group_id=?",(chat_id,))
        conn.commit()
        return await msg.reply_text("• تم مسح الرابط ✅")

    # ===== 3. اوامر الطرد والحظر =====
    if text == "حظر" and target:
        await context.bot.ban_chat_member(chat_id, target)
        cur.execute("INSERT OR IGNORE INTO banned VALUES (?,?)",(chat_id,target))
        conn.commit()
        return await msg.reply_text("• تم حظر العضو ✅")

    if text == "طرد" and target:
        await context.bot.ban_chat_member(chat_id, target)
        await context.bot.unban_chat_member(chat_id, target)
        return await msg.reply_text("• تم طرد العضو ✅")

    if text == "كتم" and target:
        await context.bot.restrict_chat_member(chat_id, target, ChatPermissions())
        cur.execute("INSERT OR IGNORE INTO muted VALUES (?,?)",(chat_id,target))
        conn.commit()
        return await msg.reply_text("• تم كتم العضو ✅")

    if text == "تقييد" and target:
        await context.bot.restrict_chat_member(chat_id, target, ChatPermissions(can_send_messages=True, can_send_media_messages=False, can_send_other_messages=False))
        return await msg.reply_text("• تم تقييد العضو ✅")

    if text == "الغاء الحظر" and target:
        await context.bot.unban_chat_member(chat_id, target)
        cur.execute("DELETE FROM banned WHERE group_id=? AND user_id=?",(chat_id,target))
        conn.commit()
        return await msg.reply_text("• تم الغاء حظر العضو ✅")

    if text == "الغاء الكتم" and target:
        await context.bot.restrict_chat_member(chat_id, target, ChatPermissions(
            can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True
        ))
        cur.execute("DELETE FROM muted WHERE group_id=? AND user_id=?",(chat_id,target))
        conn.commit()
        return await msg.reply_text("• تم الغاء كتم العضو ✅")

    if text == "رفع القيود" and target:
        await context.bot.restrict_chat_member(chat_id, target, ChatPermissions(
            can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True,
            can_send_polls=True, can_add_web_page_previews=True
        ))
        cur.execute("DELETE FROM muted WHERE group_id=? AND user_id=?",(chat_id,target))
        conn.commit()
        return await msg.reply_text("• تم رفع جميع القيود عن العضو ✅")
