import sqlite3
import re
from collections import defaultdict

DB_NAME = "protection_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            chat_id INTEGER,
            feature_name TEXT,
            status TEXT DEFAULT 'فتح',
            PRIMARY KEY (chat_id, feature_name)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# لتتبع التكرار لكل قروب وكل شخص
spam_data = defaultdict(lambda: defaultdict(list))

RANK_LEVELS = {"مالك اساسي": 6, "مالك": 5, "منشئ": 4, "مدير": 3, "ادمن": 2, "مشرف": 2, "مميز": 1, "عضو": 0}

def get_user_rank(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status == "creator": return "مالك اساسي", 6
        elif member.status == "administrator": return "مدير", 3
    except: pass
    return "عضو", 0

def set_status(chat_id: int, feature: str, status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings VALUES (?,?,?)", (chat_id, feature, status))
    conn.commit()
    conn.close()

def get_status(chat_id: int, feature: str) -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM settings WHERE chat_id =? AND feature_name =?", (chat_id, feature))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "فتح"

def register_lock_handlers(bot):

    # قائمة الكلمات الممنوعة للسب
    BAD_WORDS = ["احا", "كس", "شرموط", "قحبه", "عرص", "نيك"]

    @bot.message_handler(commands=['الحماية'], chat_types=['group','supergroup'])
    def locks_menu(m):
        bot.reply_to(m, """- اهلا بك في قائمة القفل - التعطيل :
━━━━━━━━━━━━
قفل - فتح الروابط
قفل - فتح الصور
قفل - فتح الفيديو
قفل - فتح الملصقات
قفل - فتح المتحركه
قفل - فتح الصوت
قفل - فتح الدردشه
قفل - فتح التوجيه
قفل - فتح المعرفات
قفل - فتح السب
قفل - فتح التكرار
قفل - فتح البوتات
قفل البوتات بالطرد
━━━━━━━━━━━━""")

    @bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"] and m.text)
    def process_locks(m):
        text = m.text.strip()
        chat_id = m.chat.id
        user_id = m.from_user.id
        _, sender_level = get_user_rank(bot, chat_id, user_id)
        if sender_level < 2: return

        if text.startswith("قفل ") or text.startswith("فتح "):
            parts = text.split(" ", 1)
            if len(parts) < 2: return
            action, target = parts[0], parts[1].strip()
            valid = ["الروابط","الصور","الفيديو","الملصقات","المتحركه","الصوت","الدردشه","التوجيه","المعرفات","السب","التكرار","البوتات","البوتات بالطرد"]

            if target in valid:
                set_status(chat_id, target, action)
                emoji = "🔒" if action == "قفل" else "🔓"
                bot.reply_to(m, f"{emoji} تم **{action}** {target}", parse_mode="Markdown")

    # ===== نظام الفحص والحذف التلقائي =====
    @bot.message_handler(content_types=['text','photo','video','sticker','voice','animation','document','new_chat_members','forward_date'], chat_types=['group','supergroup'])
    def anti_system(m):
        chat_id = m.chat.id
        user_id = m.from_user.id
        _, level = get_user_rank(bot, chat_id, user_id)
        if level >= 2: return # الادمن معفيين

        try:
            # 1. قفل الروابط
            if m.text and get_status(chat_id, "الروابط") == "قفل":
                if re.search(r"(http|https|t\.me|telegram\.me|@\w+)", m.text):
                    return bot.delete_message(chat_id, m.message_id)

            # 2. قفل الصور
            if m.photo and get_status(chat_id, "الصور") == "قفل":
                return bot.delete_message(chat_id, m.message_id)

            # 3. قفل الفيديو
            if m.video and get_status(chat_id, "الفيديو") == "قفل":
                return bot.delete_message(chat_id, m.message_id)

            # 4. قفل الملصقات
            if m.sticker and get_status(chat_id, "الملصقات") == "قفل":
                return bot.delete_message(chat_id, m.message_id)

            # 5. قفل المتحركه gif
            if m.animation and get_status(chat_id, "المتحركه") == "قفل":
                return bot.delete_message(chat_id, m.message_id)

            # 6. قفل الصوت
            if m.voice and get_status(chat_id, "الصوت") == "قفل":
                return bot.delete_message(chat_id, m.message_id)

            # 7. قفل الدردشه
            if m.text and get_status(chat_id, "الدردشه") == "قفل":
                return bot.delete_message(chat_id, m.message_id)

            # 8. قفل التوجيه
            if m.forward_from or m.forward_sender_name and get_status(chat_id, "التوجيه") == "قفل":
                return bot.delete_message(chat_id, m.message_id)

            # 9. قفل المعرفات
            if m.text and get_status(chat_id, "المعرفات") == "قفل":
                if "@" in m.text:
                    return bot.delete_message(chat_id, m.message_id)

            # 10. قفل السب
            if m.text and get_status(chat_id, "السب") == "قفل":
                if any(word in m.text for word in BAD_WORDS):
                    return bot.delete_message(chat_id, m.message_id)

            # 11. قفل التكرار
            if m.text and get_status(chat_id, "التكرار") == "قفل":
                spam_data[chat_id][user_id].append(m.text)
                if len(spam_data[chat_id][user_id]) > 5:
                    spam_data[chat_id][user_id].pop(0)
                if spam_data[chat_id][user_id].count(m.text) >= 3:
                    spam_data[chat_id][user_id].clear()
                    return bot.delete_message(chat_id, m.message_id)

            # 12. قفل البوتات - حذف رسائل البوتات
            if m.from_user.is_bot and get_status(chat_id, "البوتات") == "قفل":
                return bot.delete_message(chat_id, m.message_id)

            # 13. قفل البوتات بالطرد - طرد البوت عند دخوله
            if m.new_chat_members and get_status(chat_id, "البوتات بالطرد") == "قفل":
                for user in m.new_chat_members:
                    if user.is_bot:
                        bot.kick_chat_member(chat_id, user.id)
                        bot.delete_message(chat_id, m.message_id)

        except: pass
