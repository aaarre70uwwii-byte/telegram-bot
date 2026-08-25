import sqlite3
import random
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443

# رتب التسليه
رتب_التسليه = {
    "هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب",
    "كلبه": "الكلبات", "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج",
    "لحجيه": "اللحجيات", "خروف": "الخرفان", "خفيفه": "الخفينات", "خفيف": "الخفيفين"
}

رتب_التسليه_عام = ["هطف", "بثر", "حمار", "كلب", "عتوي", "لحجي", "خروف"]

def setup(bot, المطور_الاساسي, admins):

    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS fun_ranks
                    (chat_id INTEGER, user_id INTEGER, rank_name TEXT, type TEXT DEFAULT 'group', PRIMARY KEY(chat_id, user_id, rank_name, type))''')
        c.execute('''CREATE TABLE IF NOT EXISTS marriages
                    (chat_id INTEGER, user1_id INTEGER, user2_id INTEGER, PRIMARY KEY(chat_id, user1_id, user2_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS vote_kick
                    (chat_id INTEGER, target_id INTEGER, voters TEXT, PRIMARY KEY(chat_id, target_id))''')
        conn.commit()
        conn.close()
    انشاء_جداول()

    def جيب_الرتبة(chat_id, user_id):
        if user_id == ID_المطور_الاساسي: return "مطور_اساسي"
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "creator": return "مالك_اساسي"
            if member.status == "administrator": return "ادمن"
        except: pass
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT role FROM ranks WHERE chat_id =? AND user_id =?",(chat_id, user_id)).fetchone()
        conn.close()
        return result[0] if result else "عضو"

    def يقدر_يتصرف(chat_id, user_id):
        return جيب_الرتبة(chat_id, user_id) in ["مدير","منشئ","مالك","مالك_اساسي","مطور","مطور_اساسي"]

    def جيب_حالة_التفعيل(chat_id, الاسم):
        conn = sqlite3.connect(DB); result = conn.execute("SELECT status FROM features WHERE chat_id =? AND feature_name =?", (chat_id, الاسم)).fetchone(); conn.close()
        return result[0] if result else 1

    # ========== 1. اوامر رفع وتنزيل رتب التسليه ==========
    @bot.message_handler(func=lambda m: any(f'رفع : {x}' in m.text for x in رتب_التسليه.keys()) or any(f'تنزيل : {x}' in m.text for x in رتب_التسليه.keys()))
    def رفع_تنزيل_تسليه(message):
        if جيب_حالة_التفعيل(message.chat.id, "التسليه") == 0: return bot.reply_to(message, "❌ التسليه معطلة")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمدير فما فوق")

        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
        chat_id = message.chat.id
        text = message.text

        for rank, plural in رتب_التسليه.items():
            if f"رفع : {rank}" in text:
                conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?,'group')", (chat_id, target_id, rank)); conn.commit(); conn.close()
                return bot.reply_to(message, f"✅ تم رفع {target_name} الى {plural}")
            if f"تنزيل : {rank}" in text:
                conn = sqlite3.connect(DB); conn.execute("DELETE FROM fun_ranks WHERE chat_id =? AND user_id =? AND rank_name =? AND type='group'", (chat_id, target_id, rank)); conn.commit(); conn.close()
                return bot.reply_to(message, f"✅ تم تنزيل {target_name} من {plural}")

    @bot.message_handler(commands=['رفع_بقلبي'])
    def رفع_بقلبي(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        chat_id = message.chat.id; target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?,'group')", (chat_id, target_id, "بقلبي")); conn.commit(); conn.close()
        bot.reply_to(message, f"❤️ تم رفع {target_name} بقلبك")

    @bot.message_handler(commands=['تنزيل_من_قلبي'])
    def تنزيل_من_قلبي(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        chat_id = message.chat.id; target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM fun_ranks WHERE chat_id =? AND user_id =? AND rank_name ='بقلبي'", (chat_id, target_id)); conn.commit(); conn.close()
        bot.reply_to(message, f"💔 تم تنزيل {target_name} من قلبك")

    @bot.message_handler(commands=['رفع'])
    def رفع_اختياري(message):
        if جيب_حالة_التفعيل(message.chat.id, "التسليه") == 0: return bot.reply_to(message, "❌ التسليه معطلة")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمدير فما فوق")
        try:
            rank_name = message.text.split(" ", 1)[1]
        except: rank_name = "عضو_تسليه"
        chat_id = message.chat.id; target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?,'group')", (chat_id, target_id, rank_name)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم رفع {target_name} الى {rank_name}")

    @bot.message_handler(commands=['مسح_رتب_التسليه'])
    def مسح_رتب_التسليه(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمدير فما فوق")
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM fun_ranks WHERE chat_id =? AND type='group'", (message.chat.id,)); conn.commit(); conn.close()
        bot.reply_to(message, "🗑️ تم مسح جميع رتب التسليه في القروب")

    @bot.message_handler(commands=['رتب_التسليه'])
    def رتب_التسليه(message):
        chat_id = message.chat.id
        conn = sqlite3.connect(DB); results = conn.execute("SELECT user_id, rank_name FROM fun_ranks WHERE chat_id =? AND type='group'", (chat_id,)).fetchall(); conn.close()
        if not results: return bot.reply_to(message, "❌ لا يوجد رتب تسليه")
        text = "<b>رتب التسليه في القروب:</b>\n━━━━━━━━━━━━\n"
        for uid, rank in results:
            try: name = bot.get_chat_member(chat_id, uid).user.first_name
            except: name = uid
            text += f"- {name} : {rank}\n"
        bot.reply_to(message, text, parse_mode="HTML")

    # ========== 2. اوامر التسليه العام ==========
    @bot.message_handler(commands=['رفع_عام'])
    def رفع_عام(message):
        if جيب_حالة_التفعيل(message.chat.id, "التسليه") == 0: return bot.reply_to(message, "❌ التسليه معطلة")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        try: rank_name = message.text.split(" ", 1)[1]
        except: rank_name = random.choice(رتب_التسليه_عام)
        target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?,'global')", (0, target_id, rank_name)); conn.commit(); conn.close()
        bot.reply_to(message, f"🌍 تم رفع {target_name} عام الى {rank_name}")

    @bot.message_handler(commands=['رتب_التسليه_عام'])
    def رتب_التسليه_عام(message):
        conn = sqlite3.connect(DB); results = conn.execute("SELECT user_id, rank_name FROM fun_ranks WHERE type='global'").fetchall(); conn.close()
        if not results: return bot.reply_to(message, "❌ لا يوجد رتب تسليه عام")
        text = "<b>رتب التسليه العام:</b>\n━━━━━━━━━━━━\n"
        for uid, rank in results:
            text += f"- {uid} : {rank}\n"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=['مسح_رتب_التسليه_عام'])
    def مسح_رتب_التسليه_عام(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM fun_ranks WHERE type='global'"); conn.commit(); conn.close()
        bot.reply_to(message, "🗑️ تم مسح جميع رتب التسليه العام")

    # ========== 3. اوامر الزواج والطلاق ==========
    @bot.message_handler(commands=['تتزوجني'])
    def تتزوجني(message):
        if جيب_حالة_التفعيل(message.chat.id, "زوجني") == 0: return bot.reply_to(message, "❌ امر الزواج معطل")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        user1 = message.from_user.id; user2 = message.reply_to_message.from_user.id
        if user1 == user2: return bot.reply_to(message, "❌ ما تقدر تتزوج نفسك")
        chat_id = message.chat.id
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO marriages VALUES (?,?,?)", (chat_id, user1, user2)); conn.commit(); conn.close()
        bot.reply_to(message, f"💍 {message.from_user.first_name} طلب الزواج من {message.reply_to_message.from_user.first_name}")

    @bot.message_handler(commands=['طلاق'])
    def طلاق(message):
        chat_id = message.chat.id; user_id = message.from_user.id
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM marriages WHERE chat_id =? AND (user1_id =? OR user2_id =?)", (chat_id, user_id, user_id)); conn.commit(); conn.close()
        bot.reply_to(message, "💔 تم الطلاق")

    @bot.message_handler(commands=['زوجي', 'زوجتي'])
    def زوجي_زوجتي(message):
        chat_id = message.chat.id; user_id = message.from_user.id
        conn = sqlite3.connect(DB); result = conn.execute("SELECT user1_id, user2_id FROM marriages WHERE chat_id =? AND (user1_id =? OR user2_id =?)", (chat_id, user_id, user_id)).fetchone(); conn.close()
        if not result: return bot.reply_to(message, "❌ انت مش متزوج")
        partner_id = result[1] if result[0] == user_id else result[0]
        try: partner_name = bot.get_chat_member(chat_id, partner_id).user.first_name
        except: partner_name = partner_id
        bot.reply_to(message, f"💑 زوجك/زوجتك هو: {partner_name}")

    # ========== 4. امر اكتموه تصويت ==========
    @bot.message_handler(commands=['اكتموه'])
    def اكتموه(message):
        if جيب_حالة_التفعيل(message.chat.id, "اكتموه") == 0: return bot.reply_to(message, "❌ امر اكتموه معطل")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        chat_id = message.chat.id; target_id = message.reply_to_message.from_user.id; voter_id = message.from_user.id

        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT voters FROM vote_kick WHERE chat_id =? AND target_id =?", (chat_id, target_id)).fetchone()
        voters = result[0].split(",") if result else []
        if str(voter_id) in voters: conn.close(); return bot.reply_to(message, "⚠️ انت صوتت من قبل")

        voters.append(str(voter_id))
        conn.execute("INSERT OR REPLACE INTO vote_kick VALUES (?,?,?)", (chat_id, target_id, ",".join(voters)))
        conn.commit(); conn.close()

        if len(voters) >= 3:
            bot.restrict_chat_member(chat_id, target_id, permissions=types.ChatPermissions(can_send_messages=False))
            conn = sqlite3.connect(DB); conn.execute("DELETE FROM vote_kick WHERE chat_id =? AND target_id =?", (chat_id, target_id)); conn.commit(); conn.close()
            bot.reply_to(message, f"🔇 تم كتم {message.reply_to_message.from_user.first_name} بالتصويت")
        else:
            bot.reply_to(message, f"🗳️ تم التصويت. باقي {3-len(voters)} اصوات لكتمه")

    @bot.message_handler(commands=['تفعيل_اكتموه', 'تعطيل_اكتموه', 'تفعيل_زوجني', 'تعطيل_زوجني'])
    def تفعيل_تعطيل_اوامر(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمدير فما فوق")
        command = message.text.replace("/", "")
        if command.startswith("تفعيل_"):
            feature = command.replace("تفعيل_", "")
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO features VALUES (?,?,1)", (message.chat.id, feature)); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم تفعيل {feature}")
        else:
            feature = command.replace("تعطيل_", "")
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO features VALUES (?,?,0)", (message.chat.id, feature)); conn.commit(); conn.close()
            bot.reply_to(message, f"❌ تم تعطيل {feature}")

    # ========== امر قائمة 4 ==========
    @bot.message_handler(commands=['م4'])
    def م4(message):
        bot.reply_to(message, """<b>• اهلا بك عزي
- اوامر التسليه :
━━━━━━━━━━━━
- اوامر تسلية تظهر بالايدي :
- رفع : هطف - تنزيل : هطف
- رفع : بثر - تنزيل : بثر
- رفع : حمار - تنزيل : حمار
- رفع : كلب - تنزيل : كلب
- رفع : كلبه - تنزيل : كلبه
- رفع : عتوي - تنزيل : عتوي
- رفع : عتويه - تنزيل : عتويه
- رفع : لحجي - تنزيل : لحجي
- رفع : لحجيه - تنزيل : لحجيه
- رفع : خروف - تنزيل : خروف
- رفع : خفيفه - تنزيل : خفيفه
- رفع : خفيف - تنزيل : خفيف
- رفع_بقلبي - تنزيل_من_قلبي

للقروب:
- رفع + الاسم
- مسح_رتب_التسليه
- رتب_التسليه
- تعطيل_التسليه - تفعيل_التسليه

للعام:
- رفع_عام + الاسم
- رتب_التسليه_عام
- مسح_رتب_التسليه_عام

- طلاق - زواج
- زوجي - زوجتي
- تتزوجني

- اكتموه
- تعطيل_اكتموه - تفعيل_اكتموه
- تعطيل_زوجني - تفعيل_زوجني
━━━━━━━━━━━━</b>""", parse_mode="HTML")

    print("✅ تم تحميل: cog4.py - ملف التسليه")
