import sqlite3
import random
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443

def setup_fun(bot):

    def جيب_الرتبة(chat_id, user_id):
        if user_id == ID_المطور_الاساسي: return "مطور_اساسي"
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "creator": return "مالك_اساسي"
        except: pass
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT role FROM ranks WHERE chat_id =? AND user_id =?",(chat_id, user_id)).fetchone()
        conn.close()
        return result[0] if result else "عضو"

    def يقدر_يتصرف(chat_id, user_id):
        return جيب_الرتبة(chat_id, user_id)!= "عضو"

    def جيب_تفعيل(chat_id, field):
        conn = sqlite3.connect(DB)
        result = conn.execute(f"SELECT {field} FROM features WHERE chat_id =?", (chat_id,)).fetchone()
        conn.close()
        return result[0] if result else 1

    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        conn.execute("CREATE TABLE IF NOT EXISTS fun_ranks (chat_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY(chat_id, user_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS global_fun_ranks (user_id INTEGER PRIMARY KEY, rank TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS marriages (chat_id INTEGER, user1 INTEGER, user2 INTEGER, PRIMARY KEY(chat_id, user1))")
        conn.execute("CREATE TABLE IF NOT EXISTS vote_kick (chat_id INTEGER, target_id INTEGER, votes INTEGER, voters TEXT, PRIMARY KEY(chat_id, target_id))")
        conn.commit(); conn.close()
    انشاء_جداول()

    رتب_التسليه = {
        "هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب", "كلبه": "الكلبات",
        "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج", "لحجيه": "اللحجيات",
        "خروف": "الخرفان", "خفيفه": "الخفيفات", "خفيف": "الخفيفين"
    }

    # ========== رفع تنزيل رتب التسلية ==========
    @bot.message_handler(commands=['رفع', 'تنزيل'])
    def رفع_تنزيل(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        if not جيب_تفعيل(message.chat.id, "تسليه"): return bot.reply_to(message, "❌ التسلية معطلة")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")

        parts = message.text.split(" ", 1)
        if len(parts) < 2: return bot.reply_to(message, "⚠️ الصيغة: /رفع هطف")
        cmd, rank = parts[0].replace("/", ""), parts[1].strip()

        if rank == "بقلبي":
            conn = sqlite3.connect(DB)
            if cmd == "رفع": conn.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?, 'في قلبي')", (message.chat.id, message.reply_to_message.from_user.id))
            else: conn.execute("DELETE FROM fun_ranks WHERE chat_id =? AND user_id =?", (message.chat.id, message.reply_to_message.from_user.id))
            conn.commit(); conn.close()
            return bot.reply_to(message, f"{'❤️ تم رفعه بقلبك' if cmd == 'رفع' else '💔 تم تنزيله من قلبك'}")

        if rank not in رتب_التسليه: return bot.reply_to(message, "❌ الرتبة غير موجودة")

        conn = sqlite3.connect(DB)
        if cmd == "رفع": conn.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?)", (message.chat.id, message.reply_to_message.from_user.id, rank))
        else: conn.execute("DELETE FROM fun_ranks WHERE chat_id =? AND user_id =?", (message.chat.id, message.reply_to_message.from_user.id))
        conn.commit(); conn.close()
        bot.reply_to(message, f"{'✅ تم رفع' if cmd == 'رفع' else '❌ تم تنزيل'} {message.reply_to_message.from_user.first_name} الى {رتب_التسليه[rank]}")

    # ========== اوامر القروب ==========
    @bot.message_handler(commands=['مسح_رتب_التسليه', 'رتب_التسليه', 'تعطيل_التسليه', 'تفعيل_التسليه'])
    def رتب_تسليه(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return
        conn = sqlite3.connect(DB)
        if "تعطيل" in message.text:
            conn.execute("INSERT OR IGNORE INTO features (chat_id) VALUES (?)", (message.chat.id,))
            conn.execute("UPDATE features SET تسليه = 0 WHERE chat_id =?", (message.chat.id,))
            conn.commit(); conn.close(); return bot.reply_to(message, "❌ تم تعطيل التسلية")
        if "تفعيل" in message.text:
            conn.execute("UPDATE features SET تسليه = 1 WHERE chat_id =?", (message.chat.id,))
            conn.commit(); conn.close(); return bot.reply_to(message, "✅ تم تفعيل التسلية")
        if "مسح" in message.text:
            conn.execute("DELETE FROM fun_ranks WHERE chat_id =?", (message.chat.id,))
            conn.commit(); conn.close(); return bot.reply_to(message, "🗑️ تم مسح رتب التسلية")

        results = conn.execute("SELECT user_id, rank FROM fun_ranks WHERE chat_id =?", (message.chat.id,)).fetchall()
        conn.close()
        text = "**رتب التسلية:**\n"
        for r in results:
            try: name = bot.get_chat_member(message.chat.id, r[0]).user.first_name
            except: name = r[0]
            text += f"{name} = {رتب_التسليه.get(r[1], r[1])}\n"
        bot.reply_to(message, text if results else "❌ مافي رتب")

    # ========== اوامر العام ==========
    @bot.message_handler(commands=['رفع_عام', 'رتب_التسليه_عام', 'مسح_رتب_التسليه_عام'])
    def عام_تسليه(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return
        conn = sqlite3.connect(DB)
        if "مسح" in message.text:
            conn.execute("DELETE FROM global_fun_ranks")
            conn.commit(); conn.close(); return bot.reply_to(message, "🗑️ تم مسح رتب التسلية العامة")
        if "رفع" in message.text:
            if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
            rank = message.text.split(" ", 1)[1] if len(message.text.split(" ")) > 1 else "عضو"
            conn.execute("INSERT OR REPLACE INTO global_fun_ranks VALUES (?,?)", (message.reply_to_message.from_user.id, rank))
            conn.commit(); conn.close(); return bot.reply_to(message, f"✅ تم رفع {message.reply_to_message.from_user.first_name} عام الى {rank}")

        results = conn.execute("SELECT user_id, rank FROM global_fun_ranks").fetchall()
        conn.close()
        text = "**رتب التسلية العامة:**\n" + "\n".join([f"{r[0]} = {r[1]}" for r in results])
        bot.reply_to(message, text if results else "❌ مافي رتب")

    # ========== الزواج والطلاق ==========
    @bot.message_handler(commands=['تتزوجني', 'زوجي', 'زوجتي', 'طلاق'])
    def زواج(message):
        if not جيب_تفعيل(message.chat.id, "تسليه"): return
        conn = sqlite3.connect(DB)
        if "تتزوجني" in message.text:
            if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
            u1, u2 = message.from_user.id, message.reply_to_message.from_user.id
            conn.execute("INSERT OR REPLACE INTO marriages VALUES (?,?,?)", (message.chat.id, u1, u2))
            conn.commit(); conn.close()
            return bot.reply_to(message, f"💍 {message.reply_to_message.from_user.first_name} وافق على الزواج من {message.from_user.first_name}")

        if "زوجي" in message.text:
            res = conn.execute("SELECT user2 FROM marriages WHERE chat_id =? AND user1 =?", (message.chat.id, message.from_user.id)).fetchone()
            if res:
                try: name = bot.get_chat(message.chat.id).get_member(res[0]).user.first_name
                except: name = res[0]
                bot.reply_to(message, f"💑 زوجك: {name}")
            else: bot.reply_to(message, "❌ ماعندك زوج")
            conn.close()

        if "زوجتي" in message.text:
            res = conn.execute("SELECT user1 FROM marriages WHERE chat_id =? AND user2 =?", (message.chat.id, message.from_user.id)).fetchone()
            if res:
                try: name = bot.get_chat(message.chat.id).get_member(res[0]).user.first_name
                except: name = res[0]
                bot.reply_to(message, f"💑 زوجتك: {name}")
            else: bot.reply_to(message, "❌ ماعندك زوجة")
            conn.close()

        if "طلاق" in message.text:
            conn.execute("DELETE FROM marriages WHERE chat_id =? AND (user1 =? OR user2 =?)", (message.chat.id, message.from_user.id, message.from_user.id))
            conn.commit(); conn.close()
            bot.reply_to(message, "💔 تم الطلاق")

    # ========== التصويت اكتموه ==========
    @bot.message_handler(commands=['اكتموه'])
    def اكتموه(message):
        if not جيب_تفعيل(message.chat.id, "تسليه"): return bot.reply_to(message, "❌ التسلية معطلة")
        if not جيب_تفعيل(message.chat.id, "انذار"): return bot.reply_to(message, "❌ امر اكتموه معطل")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target = message.reply_to_message.from_user.id

        conn = sqlite3.connect(DB)
        res = conn.execute("SELECT votes, voters FROM vote_kick WHERE chat_id =? AND target_id =?", (message.chat.id, target)).fetchone()
        voters = res[1].split(",") if res else []

        if str(message.from_user.id) in voters: return bot.reply_to(message, "❌ صوتك محسوب")
        voters.append(str(message.from_user.id))
        votes = len(voters)

        conn.execute("INSERT OR REPLACE INTO vote_kick VALUES (?,?,?,?)", (message.chat.id, target, votes, ",".join(voters)))
        conn.commit(); conn.close()

        if votes >= 3:
            try: bot.kick_chat_member(message.chat.id, target)
            except: pass
            bot.reply_to(message, f"🔨 تم طرد {message.reply_to_message.from_user.first_name} بالتصويت")
            conn = sqlite3.connect(DB); conn.execute("DELETE FROM vote_kick WHERE chat_id =? AND target_id =?", (message.chat.id, target)); conn.commit(); conn.close()
        else:
            bot.reply_to(message, f"📊 تصويت طرد: {votes}/3")

    # ========== تفعيل وتعطيل ==========
    @bot.message_handler(commands=['تفعيل_اكتموه', 'تعطيل_اكتموه', 'تفعيل_زوجني', 'تعطيل_زوجني'])
    def تفعيل_تسليه(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return
        cmd, item = message.text.split("_")
        field = "انذار" if "اكتموه" in item else "تسليه"
        val = 1 if "تفعيل" in cmd else 0
        conn = sqlite3.connect(DB)
        conn.execute("INSERT OR IGNORE INTO features (chat_id) VALUES (?)", (message.chat.id,))
        conn.execute(f"UPDATE features SET {field} =? WHERE chat_id =?", (val, message.chat.id))
        conn.commit(); conn.close()
        bot.reply_to(message, f"{'✅' if val else '❌'} تم {'تفعيل' if val else 'تعطيل'} {item}")
