import sqlite3

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

def register_settings_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
    def settings_commands(m):
        if not m.text: return
        chat_id = m.chat.id
        sender_id = m.from_user.id
        text = m.text.strip()

        _, sender_level = get_user_rank(bot, chat_id, sender_id)
        is_admin = sender_level >= 2

        # ===== امر الهمسة =====
        if text.startswith("همس "):
            parts = text.split(" ", 2)
            if len(parts) < 3: return bot.reply_to(m, "⚠️ الطريقة: `همس @username النص`", parse_mode="Markdown")
            username = parts[1].replace("@", "")
            whisper_text = parts[2]
            sender_name = m.from_user.first_name
            try:
                target_user = bot.get_chat_member(chat_id, username)
                target_id = target_user.user.id
                bot.send_message(target_id, f"""🔒 **همسة جديدة من {sender_name}**

في قروب: {m.chat.title}
الرسالة:
{whisper_text}""", parse_mode="Markdown")
                bot.reply_to(m, f"✅ تم ارسال همسة الى @{username} في الخاص")
            except:
                bot.reply_to(m, "❌ ما قدرت ارسل الهمسة. تأكد ان الشخص بدأ البوت خاص وكتب /start")

        # ===== ارسال الاعدادات خاص =====
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

        # ===== قائمة الاعدادات =====
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
- همس @username النص
━━━━━━━━━━━━""", parse_mode="Markdown")

        # ===== رؤية الاعدادات =====
        elif text == "الرابط":
            link = get_setting(chat_id, "group_link", "لا يوجد رابط محفوظ")
            bot.reply_to(m, f"🔗 رابط المجموعة:\n{link}")

        elif text == "المالكين":
            owners = get_list(chat_id, "owners")
            bot.reply_to(m, f"👑 المالكين: {len(owners)}" if owners else "لا يوجد مالكين مضافين")

        elif text == "المنشئين":
            creators = get_list(chat_id, "creators")
            bot.reply_to(m, f"📝 المنشئين: {len(creators)}" if creators else "لا يوجد منشئين مضافين")

        elif text == "الادمنيه":
            admins = get_list(chat_id, "admins")
            bot.reply_to(m, f"🛡️ الادمنيه: {len(admins)}" if admins else "لا يوجد ادمنيه مضافين")

        elif text == "المدراء":
            mods = get_list(chat_id, "mods")
            bot.reply_to(m, f"👮 المدراء: {len(mods)}" if mods else "لا يوجد مدراء مضافين")

        elif text == "المميزين":
            vip = get_list(chat_id, "vip")
            bot.reply_to(m, f"⭐ المميزين: {len(vip)}" if vip else "لا يوجد مميزين مضافين")

        elif text == "المحظورين":
            banned = get_list(chat_id, "banned")
            bot.reply_to(m, f"🚷 المحظورين: {len(banned)}" if banned else "لا يوجد محظورين")

        elif text == "المكتومين":
            muted = get_list(chat_id, "muted")
            bot.reply_to(m, f"🔇 المكتومين: {len(muted)}" if muted else "لا يوجد مكتومين")

        elif text == "معلوماتي":
            my_rank, my_level = get_user_rank(bot, chat_id, sender_id)
            user = m.from_user
            bot.reply_to(m, f"""👤 **معلوماتك الشخصية:**

- الاسم: {user.first_name}
- الآيدي: `{user.id}`
- اليوزر: @{user.username if user.username else 'لا يوجد'}
- رتبتك: {my_rank}""", parse_mode="Markdown")

        elif text == "المجموعه":
            bot.reply_to(m, f"""🏢 **بيانات المجموعة:**

- الاسم: {m.chat.title}
- الآيدي: `{chat_id}`""", parse_mode="Markdown")

        elif text == "القوانين":
            rules = get_setting(chat_id, "rules", "لا توجد قوانين محددة")
            bot.reply_to(m, f"📜 **قوانين المجموعة:**\n{rules}")

        elif text == "الحمايه":
            bot.reply_to(m, "🛡️ الحماية: استخدم اوامر القفل من قائمة m3")

        # ===== وضع الاعدادات - للادمن فقط =====
        elif not is_admin:
            if any(x in text for x in ["اضف", "مسح", "انشاء", "ضع", "تعيين"]):
                return bot.reply_to(m, "❌ عذراً، هذا الأمر خاص بالأدمن والمالكين فقط.")

        elif text == "انشاء رابط":
            try:
                new_link = bot.export_chat_invite_link(chat_id)
                set_setting(chat_id, "group_link", new_link)
                bot.reply_to(m, f"✅ تم إنشاء رابط دعوة جديد:\n{new_link}")
            except:
                bot.reply_to(m, "❌ ارفع البوت ادمن بصلاحية دعوة عبر الرابط")

        elif text == "مسح الرابط":
            set_setting(chat_id, "group_link", "")
            bot.reply_to(m, "🗑️ تم مسح رابط المجموعة")

        elif text.startswith("ضع الترحيب"):
            welcome = text.replace("ضع الترحيب", "").strip()
            if welcome:
                set_setting(chat_id, "welcome_text", welcome)
                bot.reply_to(m, f"✅ تم حفظ الترحيب:\n`{welcome}`", parse_mode="Markdown")
            else:
                bot.reply_to(m, "⚠️ مثال: `ضع الترحيب اهلا {name}`", parse_mode="Markdown")

        elif text.startswith("ضع قوانين"):
            rules = text.replace("ضع قوانين", "").strip()
            if rules:
                set_setting(chat_id, "rules", rules)
                bot.reply_to(m, f"✅ تم اعتماد القوانين:\n{rules}")
            else:
                bot.reply_to(m, "⚠️ مثال: `ضع قوانين ممنوع السب`")

        elif text.startswith("ضع رابط"):
            link = text.replace("ضع رابط", "").replace("ضـع رابط", "").strip()
            if link:
                set_setting(chat_id, "group_link", link)
                bot.reply_to(m, f"✅ تم حفظ الرابط: {link}")
            else:
                bot.reply_to(m, "⚠️ مثال: `ضع رابط https://t.me/...`")

        elif text.startswith("تعيين الايدي"):
            id_text = text.replace("تعيين الايدي", "").strip()
            if id_text:
                set_setting(chat_id, "id_template", id_text)
                bot.reply_to(m, f"✅ تم تعيين شكل الايدي:\n`{id_text}`", parse_mode="Markdown")
            else:
                bot.reply_to(m, "⚠️ مثال: `تعيين الايدي الاسم: {name}\nالايدي: {id}`", parse_mode="Markdown")
