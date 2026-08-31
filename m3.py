import sqlite3
import re
from collections import defaultdict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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

def get_locks_keyboard(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    features = ["الروابط","الصور","الفيديو","الملصقات","المتحركه","الصوت","الدردشه","التوجيه","المعرفات","السب","التكرار","البوتات"]

    buttons = []
    for f in features:
        status = get_status(chat_id, f)
        text = f"🔒 {f}" if status == "قفل" else f"🔓 {f}"
        buttons.append(InlineKeyboardButton(text, callback_data=f"lock_{f}"))

    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🚷 قفل البوتات بالطرد", callback_data="lock_البوتات بالطرد"))
    return markup

def register_lock_handlers(bot, active_groups):

    @bot.message_handler(content_types=['text'], func=lambda m: m.text == "الحماية" and m.chat.type in ["group","supergroup"])
    def locks_menu(m):
        if m.chat.id not in active_groups: return
        chat_id = m.chat.id
        _, sender_level = get_user_rank(bot, chat_id, m.from_user.id)
        if sender_level < 2: return bot.reply_to(m, "❌ هذا الامر للادمن فقط")
        bot.reply_to(m, "⚙️ **اعدادات الحماية:**\nاضغط على الزر لقفل/فتح", parse_mode="Markdown", reply_markup=get_locks_keyboard(chat_id))

    @bot.callback_query_handler(func=lambda call: call.data.startswith("lock_"))
    def handle_lock_buttons(call):
        chat_id = call.message.chat.id
        if chat_id not in active_groups: return
        user_id = call.from_user.id
        _, sender_level = get_user_rank(bot, chat_id, user_id)
        if sender_level < 2: return bot.answer_callback_query(call.id, "❌ للادمن فقط")

        feature = call.data.replace("lock_", "")
        current = get_status(chat_id, feature)
        new_status = "فتح" if current == "قفل" else "قفل"
        set_status(chat_id, feature, new_status)

        bot.edit_message_reply_markup(chat_id, call.message_id, reply_markup=get_locks_keyboard(chat_id))
        bot.answer_callback_query(call.id, f"{'🔒 تم القفل' if new_status == 'قفل' else '🔓 تم الفتح'} {feature}")

    @bot.message_handler(content_types=['text','photo','video','sticker','voice','animation','document','new_chat_members'], chat_types=['group','supergroup'])
    def anti_system(m):
        if m.chat.id not in active_groups: return
        chat_id = m.chat.id
        user_id = m.from_user.id
        _, level = get_user_rank(bot, chat_id, user_id)
        if level >= 2: return

        BAD_WORDS = ["احا", "كس", "شرموط", "قحبه", "عرص", "نيك"]
        try:
            if m.text and get_status(chat_id, "الروابط") == "قفل" and re.search(r"(http|https|t\.me|@\w+)", m.text):
                bot.delete_message(chat_id, m.message_id); return
            if m.photo and get_status(chat_id, "الصور") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if m.video and get_status(chat_id, "الفيديو") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if m.sticker and get_status(chat_id, "الملصقات") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if m.animation and get_status(chat_id, "المتحركه") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if m.voice and get_status(chat_id, "الصوت") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if m.text and get_status(chat_id, "الدردشه") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if (m.forward_from or m.forward_sender_name or m.forward_from_chat) and get_status(chat_id, "التوجيه") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if m.text and "@" in m.text and get_status(chat_id, "المعرفات") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if m.text and get_status(chat_id, "السب") == "قفل" and any(word in m.text for word in BAD_WORDS):
                bot.delete_message(chat_id, m.message_id); return
            if m.text and get_status(chat_id, "التكرار") == "قفل":
                spam_data[chat_id][user_id].append(m.text)
                if len(spam_data[chat_id][user_id]) > 5: spam_data[chat_id][user_id].pop(0)
                if spam_data[chat_id][user_id].count(m.text) >= 3:
                    spam_data[chat_id][user_id].clear()
                    bot.delete_message(chat_id, m.message_id); return
            if m.from_user.is_bot and get_status(chat_id, "البوتات") == "قفل":
                bot.delete_message(chat_id, m.message_id); return
            if m.new_chat_members and get_status(chat_id, "البوتات بالطرد") == "قفل":
                for user in m.new_chat_members:
                    if user.is_bot: bot.kick_chat_member(chat_id, user.id)
                bot.delete_message(chat_id, m.message_id)
        except: pass
