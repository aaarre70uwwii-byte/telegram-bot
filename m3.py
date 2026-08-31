import os
import json
import re
from collections import defaultdict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

SETTINGS_FILE = "protection_settings.json"
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'r') as f:
        protection_settings = json.load(f)
else:
    protection_settings = {}

def save_settings():
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(protection_settings, f)

spam_data = defaultdict(lambda: defaultdict(list))

RANK_LEVELS = {"مالك اساسي": 6, "مالك": 5, "منشئ": 4, "مدير": 3, "ادمن": 2, "مشرف": 2, "مميز": 1, "عضو": 0}
LOCKS_LIST = ["الروابط","الصور","الفيديو","الملصقات","المتحركه","الصوت","الدردشه","التوجيه","المعرفات","السب","التكرار","البوتات","البوتات بالطرد"]

def get_user_rank(bot, chat_id, user_id):
    chat_id = str(chat_id)
    user_id = str(user_id)
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status == "creator": return "مالك اساسي", 6
        elif member.status == "administrator": return "مدير", 3
    except: pass
    return "عضو", 0

def set_status(chat_id, feature, status):
    chat_id = str(chat_id)
    if chat_id not in protection_settings: protection_settings[chat_id] = {}
    protection_settings[chat_id][feature] = status
    save_settings()

def get_status(chat_id, feature):
    chat_id = str(chat_id)
    return protection_settings.get(chat_id, {}).get(feature, "فتح")

def get_locks_keyboard(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for f in LOCKS_LIST[:-1]:
        status = get_status(chat_id, f)
        text = f"🔒 {f}" if status == "قفل" else f"🔓 {f}"
        buttons.append(InlineKeyboardButton(text, callback_data=f"lock_{f}"))
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🚷 قفل البوتات بالطرد", callback_data="lock_البوتات بالطرد"))
    return markup

def register_lock_handlers(bot, active_groups):

    # 1. امر لوحة الحماية
    @bot.message_handler(content_types=['text'], func=lambda m: m.text == "الحماية" and m.chat.type in ["group","supergroup"])
    def locks_menu(m):
        if m.chat.id not in active_groups: return
        chat_id = m.chat.id
        _, sender_level = get_user_rank(bot, chat_id, m.from_user.id)
        if sender_level < 2: return bot.reply_to(m, "❌ هذا الامر للادمن فقط")
        bot.reply_to(m, "⚙️ **اعدادات الحماية:**\nاضغط على الزر لقفل/فتح", parse_mode="Markdown", reply_markup=get_locks_keyboard(chat_id))

    # 2. اوامر الكتابه الجديده: قفل و فتح
    @bot.message_handler(content_types=['text'], chat_types=['group','supergroup'])
    def lock_commands(m):
        if m.chat.id not in active_groups: return
        chat_id = m.chat.id
        text = m.text.strip()
        _, sender_level = get_user_rank(bot, chat_id, m.from_user.id)
        if sender_level < 2: return

        if text.startswith("قفل "):
            feature = text.replace("قفل ", "")
            if feature in LOCKS_LIST:
                set_status(chat_id, feature, "قفل")
                bot.reply_to(m, f"🔒 تم قفل {feature}")

        elif text.startswith("فتح "):
            feature = text.replace("فتح ", "")
            if feature in LOCKS_LIST:
                set_status(chat_id, feature, "فتح")
                bot.reply_to(m, f"🔓 تم فتح {feature}")

    # 3. ازرار الحماية
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

    # 4. نظام المنع التلقائي
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
