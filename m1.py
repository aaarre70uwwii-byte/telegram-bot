import sqlite3
from telebot.types import ChatPermissions

DB_FILE = "group_management.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS group_ranks (chat_id INTEGER, user_id INTEGER, rank_name TEXT, PRIMARY KEY (chat_id, user_id))")
conn.commit()

RANK_LEVELS = {
    "مالك اساسي": 6, "مالك": 5, "منشئ": 4, "مدير": 3,
    "ادمن": 2, "مشرف": 2, "مميز": 1, "عضو": 0
}

RANK_ORDER = ["عضو", "مميز", "ادمن", "مدير", "منشئ", "مالك", "مالك اساسي"]

def get_user_rank(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        status = member.status
        if status == "creator": return "مالك اساسي", 6
        elif status == "administrator":
            cursor.execute("SELECT rank_name FROM group_ranks WHERE chat_id =? AND user_id =?", (chat_id, user_id))
            res = cursor.fetchone()
            rank = res[0] if res else "مدير"
            return rank, RANK_LEVELS.get(rank, 3)
    except: pass
    cursor.execute("SELECT rank_name FROM group_ranks WHERE chat_id =? AND user_id =?", (chat_id, user_id))
    res = cursor.fetchone()
    if res: return res[0], RANK_LEVELS.get(res[0], 1)
    return "عضو", 0

def register_admin_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
    def admin_commands(m):
        if not m.text: return
        chat_id = m.chat.id
        sender_id = m.from_user.id
        text = m.text.strip()

        sender_rank, sender_level = get_user_rank(bot, chat_id, sender_id)
        if sender_level < 2 and any(x in text for x in ["رفع", "تنزيل", "حظر", "طرد", "كتم", "مسح"]):
            return bot.reply_to(m, "❌ هذا الامر للمشرفين فما فوق")

        if text == "رتبتي":
            my_rank, my_level = get_user_rank(bot, chat_id, sender_id)
            bot.reply_to(m, f"• اسمك: {m.from_user.first_name}\n• رتبتك: **{my_rank}**\n• المستوى: {my_level}\n• المجموع: {chat_id}", parse_mode="Markdown")

        elif text == "رفع":
            if not m.reply_to_message: return bot.reply_to(m, "💡 استخدم الأمر بالرد على العضو")
            target_id = m.reply_to_message.from_user.id
            target_name = m.reply_to_message.from_user.first_name
            target_rank, target_level = get_user_rank(bot, chat_id, target_id)

            if target_level >= sender_level: return bot.reply_to(m, "⚠️ لا يمكنك رفع شخص رتبته اعلى منك او تساويك")
            if target_rank == "مالك اساسي": return bot.reply_to(m, "⚠️ لا يمكن رفع المالك الاساسي")

            next_level = target_level + 1
            if next_level > sender_level: return bot.reply_to(m, f"⚠️ لا يمكنك رفع اكثر من رتبتك. رتبتك: {sender_rank}")

            new_rank = RANK_ORDER[next_level]
            cursor.execute("INSERT OR REPLACE INTO group_ranks VALUES (?,?,?)", (chat_id, target_id, new_rank))
            conn.commit()
            bot.reply_to(m, f"• العضو: {target_name}\n• تم رفعه من {target_rank} الى **{new_rank}** 🛡️", parse_mode="Markdown")

        elif text == "تنزيل":
            if not m.reply_to_message: return bot.reply_to(m, "💡 استخدم الأمر بالرد على العضو")
            target_id = m.reply_to_message.from_user.id
            target_name = m.reply_to_message.from_user.first_name
            target_rank, target_level = get_user_rank(bot, chat_id, target_id)

            if target_level >= sender_level: return bot.reply_to(m, "⚠️ لا يمكنك تنزيل شخص رتبته اعلى منك او تساويك")
            if target_level == 0: return bot.reply_to(m, "⚠️ العضو بالفعل رتبته عضو")

            new_level = target_level - 1
            new_rank = RANK_ORDER[new_level]
            if new_rank == "عضو":
                cursor.execute("DELETE FROM group_ranks WHERE chat_id =? AND user_id =?", (chat_id, target_id))
            else:
                cursor.execute("INSERT OR REPLACE INTO group_ranks VALUES (?,?,?)", (chat_id, target_id, new_rank))
            conn.commit()
            bot.reply_to(m, f"• العضو: {target_name}\n• تم تنزيله من {target_rank} الى **{new_rank}** ❌", parse_mode="Markdown")

        elif text == "تنزيل الكل":
            if sender_level < 5: return bot.reply_to(m, "⚠️ هذا الامر للمالكين فقط")
            cursor.execute("DELETE FROM group_ranks WHERE chat_id =?", (chat_id,))
            conn.commit()
            bot.reply_to(m, "• تم مسح جميع الرتب المرفوعة 🛑")

        elif text.startswith("مسح "):
            if sender_level < 2: return bot.reply_to(m, "❌ ليس لديك صلاحية")
            parts = text.split(" ")
            if len(parts) > 1 and parts[1].isdigit():
                count = int(parts[1])
                if count > 100: return bot.reply_to(m, "⚠️ اقصى شي 100 رسالة")
                try: bot.delete_message(chat_id, m.message_id)
                except: pass
                for i in range(1, count + 1):
                    try: bot.delete_message(chat_id, m.message_id - i)
                    except: pass
                bot.send_message(chat_id, f"✅ تم مسح {count} رسالة")

        elif text in ["حظر", "طرد", "كتم", "الغاء الكتم", "الغاء الحظر"]:
            if not m.reply_to_message: return bot.reply_to(m, "💡 رد على العضو")
            target_id = m.reply_to_message.from_user.id
            target_name = m.reply_to_message.from_user.first_name
            _, target_level = get_user_rank(bot, chat_id, target_id)
            if target_level >= sender_level: return bot.reply_to(m, "⚠️ لا يمكنك معاقبة من هو اعلى منك")

            if text == "حظر":
                bot.ban_chat_member(chat_id, target_id)
                bot.reply_to(m, f"🚷 تم حظر {target_name}")
            elif text == "طرد":
                bot.ban_chat_member(chat_id, target_id)
                bot.unban_chat_member(chat_id, target_id)
                bot.reply_to(m, f"🚪 تم طرد {target_name}")
            elif text == "كتم":
                bot.restrict_chat_member(chat_id, target_id, permissions=ChatPermissions(can_send_messages=False))
                bot.reply_to(m, f"🔇 تم كتم {target_name}")
            elif text in ["الغاء الكتم", "الغاء الحظر"]:
                bot.unban_chat_member(chat_id, target_id)
                bot.restrict_chat_member(chat_id, target_id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
                bot.reply_to(m, f"✅ تم فك الحظر عن {target_name}")
