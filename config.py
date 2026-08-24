import sqlite3
import config

DB = "bot.db"

def setup(bot, المطور_الاساسي, admins):

    # انشاء جدول الاقفال
    def انشاء_جدول_القفل():
        conn = sqlite3.connect(DB)
        conn.execute('''CREATE TABLE IF NOT EXISTS locks
                        (chat_id INTEGER PRIMARY KEY, links TEXT, photos TEXT, spam TEXT)''')
        conn.commit()
        conn.close()
    انشاء_جدول_القفل()

    def جيب_حالة_القفل(chat_id, النوع):
        conn = sqlite3.connect(DB)
        result = conn.execute(f"SELECT {النوع} FROM locks WHERE chat_id =?", (chat_id,)).fetchone()
        conn.close()
        return result[0] if result else "مفتوح"

    def حط_حالة_القفل(chat_id, النوع, الحالة):
        conn = sqlite3.connect(DB)
        conn.execute("INSERT OR REPLACE INTO locks (chat_id, links, photos, spam) VALUES (?,?,?)",
                     (chat_id,
                      الحالة if النوع == "links" else جيب_حالة_القفل(chat_id, "links"),
                      الحالة if النوع == "photos" else جيب_حالة_القفل(chat_id, "photos"),
                      الحالة if النوع == "spam" else جيب_حالة_القفل(chat_id, "spam")))
        conn.commit()
        conn.close()

    # ========== اوامر القفل من الازرار ==========
    @bot.message_handler(func=lambda m: m.text in ["قفل الروابط", "فتح الروابط", "قفل الصور", "فتح الصور", "قفل الكلايش", "فتح الكلايش"])
    def اوامر_القفل(message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        # فحص ادمن
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status not in ['creator', 'administrator'] and user_id not in admins:
                return bot.reply_to(message, "❌ هذا للادمنية فقط")
        except: return

        text = message.text
        if text == "قفل الروابط":
            حط_حالة_القفل(chat_id, "links", "مقفول")
            bot.reply_to(message, "🔒 تم
