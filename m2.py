import sqlite3
from telebot import types # <-- ضيف هذا السطر

DB_FILE = "group_management.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS group_settings (chat_id INTEGER, key TEXT, value TEXT, PRIMARY KEY (chat_id, key))")
conn.commit()

RANK_LEVELS = {"مالك اساسي": 6, "مالك": 5, "منشئ": 4, "مدير": 3, "ادمن": 2, "مشرف": 2, "مميز": 1, "عضو": 0}

def get_user_rank(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status == "creator": return "مالك اساسي", 6
        elif member.status == "administrator":
            cursor.execute("SELECT rank_name FROM group_ranks WHERE chat_id =? AND user_id =?", (chat_id, user_id))
            res = cursor.fetchone()
            rank = res[0] if res else "مدير"
            return rank, RANK_LEVELS.get(rank, 3)
    except: pass
    cursor.execute("SELECT rank_name FROM group_ranks WHERE chat_id =? AND user_id =?", (chat_id, user_id))
    res = cursor.fetchone()
    if res: return res[0], RANK_LEVELS.get(res[0], 1)
    return "عضو", 0

def get_setting(chat_id, key, default="غير محدد"):
    cursor.execute("SELECT value FROM group_settings WHERE chat_id =? AND key =?", (chat_id, key))
    res = cursor.fetchone()
    return res[0] if res else default

def set_setting(chat_id, key, value):
    cursor.execute("INSERT OR REPLACE INTO group_settings VALUES (?,?,?)", (chat_id, key, value))
    conn.commit()

def get_list(chat_id, key):
    cursor.execute("SELECT value FROM group_settings WHERE chat_id =? AND key =?", (chat_id, key))
    res = cursor.fetchone()
    return res[0].split(",") if res and res[0] else []

def register_settings_handlers(bot, active_groups):

    @bot.message_handler(content_types=['text'], func=lambda m: m.chat.type in ["group", "supergroup"])
    def settings_commands(m):
        if m.chat.id not in active_groups: return
        if not m.text: return
        chat_id = m.chat.id
        sender_id = m.from_user.id
        text = m.text.strip()

        _, sender_level = get_user_rank(bot, chat_id, sender_id)
        is_admin = sender_level >= 2

        # ===== امر الهمسة بالرد =====
        if text == "همس":
            if not m.reply_to_message:
                return bot.reply_to(m, "💡 استخدم الأمر بالرد على الشخص + النص\nمثال: `همس اهلا بيك`", parse_mode="Markdown")

            target_id = m.reply_to_message.from_user.id
            target_name = m.reply_to_message.from_user.first_name
            sender_name = m.from_user.first_name

            whisper_text = text.replace("همس", "").strip()
            if not whisper_text and m.reply_to_message:
                whisper_text = m.reply_to_message.text if m.reply_to_message.text else "بدون نص"

            if not whisper_text:
                return bot.reply_to(m, "⚠️ اكتب النص بعد همس او رد على رسالة فيها نص")

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("👁️ تمت القراءة", callback_data=f"read_whisper_{sender_id}"))

            try:
                bot.send_message(target_id, f"""🔒 **همسة جديدة من {sender_name}**

في قروب: {m.chat.title}
الرسالة:
{whisper_text}

━━━━━━━━━━━━
✅ اضغط الزر تحت لما تقرأها""", parse_mode="Markdown", reply_markup=keyboard)
                bot.reply_to(m, f"✅ تم ارسال همسة الى {target_name} في الخاص")
            except:
                bot.reply_to(m, f"❌ ما قدرت ارسل الهمسة لـ {target_name}. لازم يبدأ البوت خاص ويكتب /start")

        # ===== باقي الاوامر زي ما هي =====
        elif text == "الاعدادات خاص":
            welcome = get_setting(chat_id, "welcome_text", "معطل")
            link = get_setting(chat_id, "group_link", "غير محدد")
            rules = get_setting(chat_id, "rules", "غير محدد")
            settings_text = f"""⚙️ **اعدادات {m.chat.title}:**

👋 الترحيب: `{welcome}`
🔗 الرابط: {link}
📜 القوانين: {rules}"""
            try:
                bot.send_message(sender_id, settings_text, parse_mode="Markdown")
                bot.reply_to(m, "📩 تم ارسال الاعدادات لك في الخاص")
            except:
                bot.reply_to(m, "❌ ما قدرت ارسل لك خاص. اضغط /start على البوت اول")

        elif text == "الاعدادات":
            bot.reply_to(m, """- اهلا بك في قائمة اوامر الاعدادات :
━━━━━━━━━━━━
- اوامر رؤية الاعدادات :
- الرابط • المالكين • المنشئين
- الادمنيه • المدراء • المميزين
- المحظورين • القوانين • المكتومين
- معلوماتي • الحمايه • المجموعه
- الاعدادات خاص
- اوامر وضع الاعدادات :
- اضف رابط • مسح الرابط • انشاء رابط
- ضع الترحيب • ضع قوانين • ضع رابط
- تعيين الايدي [النص]
- اوامر الهمس:
- رد على رسالة واكتب `همس النص`
━━━━━━━━━━━━""", parse_mode="Markdown")

        #... باقي الاوامر خليها زي ما هي

    # ===== معالج زر قراءة الهمسة =====
    @bot.callback_query_handler(func=lambda call: call.data.startswith("read_whisper_"))
    def read_whisper(call):
        sender_id = int(call.data.split("_")[2])
        reader_name = call.from_user.first_name
        try:
            bot.send_message(sender_id, f"👁️ {reader_name} قرأ همستك")
            bot.answer_callback_query(call.id, "تم ابلاغ المرسل انك قرأتها")
            bot.edit_message_reply_markup(call.message.chat.id, call.message_id, reply_markup=None)
        except:
            bot.answer_callback_query(call.id, "ما قدرت ابلغ المرسل")
