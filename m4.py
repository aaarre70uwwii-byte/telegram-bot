import sqlite3
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

DB_NAME = "entertainment_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fun_roles (
            user_id INTEGER,
            chat_id INTEGER,
            role_name TEXT,
            PRIMARY KEY (user_id, chat_id, role_name)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marriage (
            user_one INTEGER,
            user_two INTEGER,
            PRIMARY KEY (user_one, user_two)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fun_settings (
            chat_id INTEGER PRIMARY KEY,
            entertainment TEXT DEFAULT 'تفعيل',
            kick_vote TEXT DEFAULT 'تفعيل',
            marry_sys TEXT DEFAULT 'تفعيل'
        )
    """)
    conn.commit()
    conn.close()

init_db()
vote_data = {}

RANK_LEVELS = {"مالك اساسي": 6, "مالك": 5, "منشئ": 4, "مدير": 3, "ادمن": 2, "مشرف": 2, "مميز": 1, "عضو": 0}

def get_user_rank(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status == "creator": return "مالك اساسي", 6
        elif member.status == "administrator": return "مدير", 3
    except: pass
    return "عضو", 0

def manage_fun_role(user_id: int, chat_id: int, role: str, action: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if action == "add":
        cursor.execute("INSERT OR IGNORE INTO fun_roles VALUES (?,?,?)", (user_id, chat_id, role))
    elif action == "remove":
        cursor.execute("DELETE FROM fun_roles WHERE user_id =? AND chat_id =? AND role_name =?", (user_id, chat_id, role))
    conn.commit()
    conn.close()

def get_user_fun_roles(user_id: int, chat_id: int) -> list:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role_name FROM fun_roles WHERE user_id =? AND chat_id =?", (user_id, chat_id))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def clear_chat_fun_roles(chat_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fun_roles WHERE chat_id =?", (chat_id,))
    conn.commit()
    conn.close()

def get_setting(chat_id: int, column: str) -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {column} FROM fun_settings WHERE chat_id =?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "تفعيل"

def update_setting(chat_id: int, column: str, value: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO fun_settings (chat_id, {}) VALUES (?,?)".format(column), (chat_id, value))
    conn.commit()
    conn.close()

def get_fun_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("😂 نكتة", callback_data="fun_joke"),
        InlineKeyboardButton("🎭 صراحة", callback_data="fun_saraha"),
        InlineKeyboardButton("🔥 تحدي", callback_data="fun_challenge")
    )
    markup.add(
        InlineKeyboardButton("❤️ نسبه الحب", callback_data="fun_love"),
        InlineKeyboardButton("💍 الزواج", callback_data="fun_marry_menu"),
        InlineKeyboardButton("🏅 رتبي", callback_data="fun_myroles")
    )
    return markup

def register_fun_handlers(bot):

    static_roles = {
        "هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب",
        "كلبه": "الكلبات", "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج",
        "لحجيه": "اللحجيات", "خروف": "الخرفان", "خفيفه": "الخفيفات", "خفيف": "الخفيفين", "بقلبي": "قلبي"
    }

    @bot.message_handler(commands=['التسلية'], chat_types=['group','supergroup'])
    @bot.message_handler(func=lambda m: m.text == "التسلية", chat_types=['group','supergroup'])
    def fun_menu(m):
        chat_id = m.chat.id
        if get_setting(chat_id, "entertainment") == "تعطيل":
            return bot.reply_to(m, "❌ نظام التسلية معطل")

        bot.reply_to(m, "🎉 **قائمة التسلية**\nاختار اللي تريده:", parse_mode="Markdown", reply_markup=get_fun_keyboard())

    # ===== هاندلر الازرار =====
    @bot.callback_query_handler(func=lambda call: call.data.startswith("fun_"))
    def handle_fun_buttons(call):
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        data = call.data

        if data == "fun_joke":
            jokes = ["مرة واحد محش دخل الامتحان قالوا له اكتب اسمك كتب اسمي","واحد غبي طاح من فوق قال الحمدلله ما مت","محش سألوه 2+2 قال 5 نقصت 1"]
            bot.answer_callback_query(call.id, random.choice(jokes), show_alert=True)

        elif data == "fun_saraha":
            saraha = ["ايش اكثر شي تندم عليه؟","من تكره في القروب؟","تحب مين بالسري؟","ايش سرك؟"]
            bot.answer_callback_query(call.id, "🎭 صراحة: " + random.choice(saraha), show_alert=True)

        elif data == "fun_challenge":
            challenges = ["تحداك ترسل 5 ملصقات","تحداك تغير اسمك 10 دقايق","تحداك تمدح الادمن","تحداك ترسل صوتية"]
            bot.answer_callback_query(call.id, "🔥 تحدي: " + random.choice(challenges), show_alert=True)

        elif data == "fun_love":
            bot.answer_callback_query(call.id, "⚠️ رد على الشخص واكتب: نسبة الحب", show_alert=True)

        elif data == "fun_myroles":
            roles = get_user_fun_roles(user_id, chat_id)
            bot.answer_callback_query(call.id, f"🏅 رتبك: {', '.join(roles) if roles else 'بدون رتبة'}", show_alert=True)

        elif data == "fun_marry_menu":
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("💍 طلب زواج", callback_data="marry_request"))
            markup.add(InlineKeyboardButton("💔 طلاق", callback_data="marry_divorce"))
            markup.add(InlineKeyboardButton("👰 زوجي/زوجتي", callback_data="marry_show"))
            bot.edit_message_text("💍 **نظام الزواج**", chat_id, call.message_id, reply_markup=markup)

    # ===== هاندلر الاوامر النصية =====
    @bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"] and m.text)
    def process_fun(m):
        text = m.text.strip()
        chat_id = m.chat.id
        user_id = m.from_user.id
        _, sender_level = get_user_rank(bot, chat_id, user_id)

        if get_setting(chat_id, "entertainment") == "تعطيل" and not any(x in text for x in ["تفعيل", "تعطيل"]):
            return

        # ===== التحكم للادمن =====
        if sender_level >= 2:
            if text == "تعطيل التسليه": update_setting(chat_id, "entertainment", "تعطيل"); return bot.reply_to(m, "⚙️ تم تعطيل نظام التسلية")
            if text == "تفعيل التسليه": update_setting(chat_id, "entertainment", "تفعيل"); return bot.reply_to(m, "⚙️ تم تفعيل نظام التسلية")
            if text == "تعطيل اكتموه": update_setting(chat_id, "kick_vote", "تعطيل"); return bot.reply_to(m, "⚙️ تم تعطيل تصويت الكتم")
            if text == "تفعيل اكتموه": update_setting(chat_id, "kick_vote", "تفعيل"); return bot.reply_to(m, "⚙️ تم تفعيل تصويت الكتم")
            if text == "تعطيل زوجني": update_setting(chat_id, "marry_sys", "تعطيل"); return bot.reply_to(m, "⚙️ تم تعطيل نظام الزواج")
            if text == "تفعيل زوجني": update_setting(chat_id, "marry_sys", "تفعيل"); return bot.reply_to(m, "⚙️ تم تفعيل نظام الزواج")
            if text == "مسح رتب التسليه": clear_chat_fun_roles(chat_id); return bot.reply_to(m, "🗑️ تم مسح كل رتب التسلية")

        # ===== رفع وتنزيل الرتب =====
        if text.startswith("رفع ") or text.startswith("تنزيل "):
            if not m.reply_to_message: return bot.reply_to(m, "⚠️ رد على الشخص")
            parts = text.split(" ", 1)
            action, role_input = parts[0], parts[1].strip()
            target = m.reply_to_message.from_user
            if role_input in static_roles:
                plural = static_roles[role_input]
                manage_fun_role(target.id, chat_id, role_input, "add" if action == "رفع" else "remove")
                bot.reply_to(m, f"{'👑 تم رفع' if action == 'رفع' else '🗑️ تم تنزيل'} {target.first_name} {'في' if action == 'رفع' else 'من'} {plural}")

        # ===== رفع بقلبي =====
        if text == "رفع بقلبي" and m.reply_to_message:
            target = m.reply_to_message.from_user
            manage_fun_role(target.id, chat_id, "بقلبي", "add")
            bot.reply_to(m, f"❤️ تم رفع {target.first_name} في قلبي")

        if text == "تنزيل من قلبي" and m.reply_to_message:
            target = m.reply_to_message.from_user
            manage_fun_role(target.id, chat_id, "بقلبي", "remove")
            bot.reply_to(m, f"💔 تم تنزيل {target.first_name} من قلبي")

        # ===== نظام الزواج =====
        if get_setting(chat_id, "marry_sys") == "تفعيل":
            if text == "تتزوجني" and m.reply_to_message:
                target = m.reply_to_message.from_user
                bot.reply_to(m, f"{target.first_name} هل تقبل الزواج من {m.from_user.first_name} ؟\nرد بـ `قبول` او `رفض`", parse_mode="Markdown")

            if text in ["قبول", "رفض", "طلاق"] and m.reply_to_message:
                target_id = m.reply_to_message.from_user.id
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                if text == "قبول":
                    cursor.execute("INSERT OR REPLACE INTO marriage VALUES (?,?)", (user_id, target_id))
                    cursor.execute("INSERT OR REPLACE INTO marriage VALUES (?,?)", (target_id, user_id))
                    bot.reply_to(m, f"🎉 مبروك تم الزواج رسمياً 💍")
                elif text == "طلاق":
                    cursor.execute("DELETE FROM marriage WHERE user_one =? AND user_two =?", (user_id, target_id))
                    cursor.execute("DELETE FROM marriage WHERE user_one =? AND user_two =?", (target_id, user_id))
                    bot.reply_to(m, "💔 تم الطلاق")
                elif text == "رفض":
                    bot.reply_to(m, "💔 تم رفض طلب الزواج")
                conn.commit(); conn.close()

            if text in ["زوجي", "زوجتي"]:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT user_two FROM marriage WHERE user_one =?", (user_id,))
                row = cursor.fetchone(); conn.close()
                bot.reply_to(m, f"💍 زوجك/زوجتك: `{row[0]}`" if row else "انت اعزب/عزباء", parse_mode="Markdown")

        # ===== تصويت الكتم =====
        if text == "اكتموه" and m.reply_to_message and get_setting(chat_id, "kick_vote") == "تفعيل":
            target_id = m.reply_to_message.from_user.id
            vote_data[target_id] = vote_data.get(target_id, 0) + 1
            if vote_data[target_id] >= 3:
                try: bot.restrict_chat_member(chat_id, target_id, until_date=3600); bot.reply_to(m, f"🔇 تم كتم {m.reply_to_message.from_user.first_name} ساعة"); vote_data[target_id] = 0
                except: bot.reply_to(m, "❌ ما عندي صلاحية كتم")
            else: bot.reply_to(m, f"📢 تصويت {vote_data[target_id]}/3 لكتم {m.reply_to_message.from_user.first_name}")

        # ===== نسبه الحب =====
        if text == "نسبه الحب" and m.reply_to_message:
            percent = random.randint(1, 100)
            bot.reply_to(m, f"❤️ نسبة الحب بين {m.from_user.first_name} و {m.reply_to_message.from_user.first_name} هي: {percent}%")
