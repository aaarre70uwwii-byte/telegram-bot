import sqlite3
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443

def setup_locks(bot):

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

    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        conn.execute("CREATE TABLE IF NOT EXISTS locks (chat_id INTEGER PRIMARY KEY, جمثون INTEGER DEFAULT 0, سب INTEGER DEFAULT 0, ايرانيه INTEGER DEFAULT 0, كتابه INTEGER DEFAULT 0, اباحي INTEGER DEFAULT 0, تعديل_ميديا INTEGER DEFAULT 0, تعديل INTEGER DEFAULT 0, فيديو INTEGER DEFAULT 0, صور INTEGER DEFAULT 0, ملصقات INTEGER DEFAULT 0, متحركه INTEGER DEFAULT 0, دردشه INTEGER DEFAULT 0, روابط INTEGER DEFAULT 0, تاك INTEGER DEFAULT 0, بوتات INTEGER DEFAULT 0, معرفات INTEGER DEFAULT 0, كلايش INTEGER DEFAULT 0, تكرار INTEGER DEFAULT 0, توجيه INTEGER DEFAULT 0, انلاين INTEGER DEFAULT 0, جهات INTEGER DEFAULT 0, دخول INTEGER DEFAULT 0, صوت INTEGER DEFAULT 0, توجيه_تقييد INTEGER DEFAULT 0, روابط_تقييد INTEGER DEFAULT 0, متحركه_تقييد INTEGER DEFAULT 0, صور_تقييد INTEGER DEFAULT 0, فيديو_تقييد INTEGER DEFAULT 0, بوتات_طرد INTEGER DEFAULT 0)")
        conn.execute("CREATE TABLE IF NOT EXISTS features (chat_id INTEGER PRIMARY KEY, ضافني INTEGER DEFAULT 1, اذكار INTEGER DEFAULT 1, ثنائي INTEGER DEFAULT 1, افتاري INTEGER DEFAULT 1, تسليه INTEGER DEFAULT 1, الكت INTEGER DEFAULT 1, ترحيب INTEGER DEFAULT 1, ردود INTEGER DEFAULT 1, انذار INTEGER DEFAULT 1, تحذير INTEGER DEFAULT 1, ايدي INTEGER DEFAULT 1, رابط INTEGER DEFAULT 1, اطردني INTEGER DEFAULT 1, حظر INTEGER DEFAULT 1, رفع INTEGER DEFAULT 1, تنزيل INTEGER DEFAULT 1, تحويل INTEGER DEFAULT 1, حمايه INTEGER DEFAULT 1, منشن INTEGER DEFAULT 1, اقتباسات INTEGER DEFAULT 1, خدميه INTEGER DEFAULT 1, يوتيوب INTEGER DEFAULT 1, ايدي_صوره INTEGER DEFAULT 1, تحقق INTEGER DEFAULT 1, ردود_سورس INTEGER DEFAULT 1)")
        conn.commit()
        conn.close()
    انشاء_جداول()

    def تحديث_قفل(chat_id, field, value):
        conn = sqlite3.connect(DB)
        conn.execute(f"INSERT OR IGNORE INTO locks (chat_id) VALUES (?)", (chat_id,))
        conn.execute(f"UPDATE locks SET {field} =? WHERE chat_id =?", (value, chat_id))
        conn.commit(); conn.close()

    def تحديث_ميزة(chat_id, field, value):
        conn = sqlite3.connect(DB)
        conn.execute(f"INSERT OR IGNORE INTO features (chat_id) VALUES (?)", (chat_id,))
        conn.execute(f"UPDATE features SET {field} =? WHERE chat_id =?", (value, chat_id))
        conn.commit(); conn.close()

    def جيب_قفل(chat_id, field):
        conn = sqlite3.connect(DB)
        result = conn.execute(f"SELECT {field} FROM locks WHERE chat_id =?", (chat_id,)).fetchone()
        conn.close()
        return result[0] if result else 0

    اوامر_القفل = {
        "جمثون": "جمثون", "السب": "سب", "الايرانيه": "ايرانيه", "الكتابه": "كتابه",
        "الاباحي": "اباحي", "تعديل_الميديا": "تعديل_ميديا", "التعديل": "تعديل",
        "الفيديو": "فيديو", "الصور": "صور", "الملصقات": "ملصقات", "المتحركه": "متحركه",
        "الدردشه": "دردشه", "الروابط": "روابط", "التاك": "تاك", "البوتات": "بوتات",
        "المعرفات": "معرفات", "الكلايش": "كلايش", "التكرار": "تكرار", "التوجيه": "توجيه",
        "الانلاين": "انلاين", "الجهات": "جهات", "الدخول": "دخول", "الصوت": "صوت",
        "التوجيه_بالتقييد": "توجيه_تقييد", "الروابط_بالتقييد": "روابط_تقييد",
        "المتحركه_بالتقييد": "متحركه_تقييد", "الصور_بالتقييد": "صور_تقييد", "الفيديو_بالتقييد": "فيديو_تقييد"
    }

    اوامر_الميزات = {
        "ضافني": "ضافني", "الاذكار": "اذكار", "الثنائي": "ثنائي", "افتاري": "افتاري",
        "التسليه": "تسليه", "الكت": "الكت", "الترحيب": "ترحيب", "الردود": "ردود",
        "الانذار": "انذار", "التحذير": "تحذير", "الايدي": "ايدي", "الرابط": "رابط",
        "اطردني": "اطردني", "الحظر": "حظر", "الرفع": "رفع", "التنزيل": "تنزيل",
        "التحويل": "تحويل", "الحمايه": "حمايه", "المنشن": "منشن", "وضع_الاقتباسات": "اقتباسات",
        "الخدميه": "خدميه", "اليوتيوب": "يوتيوب", "الايدي_بالصوره": "ايدي_صوره",
        "التحقق": "تحقق", "ردود_السورس": "ردود_سورس"
    }

    @bot.message_handler(commands=['قفل', 'فتح'])
    def قفل_فتح(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        parts = message.text.split(" ", 1)
        if len(parts) < 2: return bot.reply_to(message, "⚠️ الصيغة: /قفل الروابط")
        cmd, item = parts[0].replace("/", ""), parts[1].strip()

        if item == "الكل":
            fields = list(اوامر_القفل.values())
            conn = sqlite3.connect(DB)
            conn.execute("INSERT OR IGNORE INTO locks (chat_id) VALUES (?)", (message.chat.id,))
            conn.execute(f"UPDATE locks SET {','.join([f'{f}=1' for f in fields])} WHERE chat_id =?", (message.chat.id,))
            conn.commit(); conn.close()
            return bot.reply_to(message, "🔒 تم قفل الكل")
        if item == "الكل": # تم التصحيح هنا
            fields = list(اوامر_القفل.values())
            conn = sqlite3.connect(DB)
            conn.execute(f"UPDATE locks SET {','.join([f'{f}=0' for f in fields])} WHERE chat_id =?", (message.chat.id,))
            conn.commit(); conn.close()
            return bot.reply_to(message, "🔓 تم فتح الكل")

        if item in اوامر_القفل:
            تحديث_قفل(message.chat.id, اوامر_القفل[item], 1 if cmd == "قفل" else 0)
            bot.reply_to(message, f"{'🔒 تم قفل' if cmd == 'قفل' else '🔓 تم فتح'} {item}")
        else: bot.reply_to(message, "❌ الامر غير موجود")

    @bot.message_handler(commands=['قفل_البوتات_بالطرد'])
    def قفل_بوتات_طرد(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        تحديث_قفل(message.chat.id, "بوتات_طرد", 1)
        bot.reply_to(message, "🔒 تم قفل البوتات بالطرد")

    @bot.message_handler(commands=['تفعيل', 'تعطيل'])
    def تفعيل_تعطيل(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        parts = message.text.split(" ", 1)
        if len(parts) < 2: return bot.reply_to(message, "⚠️ الصيغة: /تفعيل الترحيب")
        cmd, item = parts[0].replace("/", ""), parts[1].strip()

        if item in اوامر_الميزات:
            تحديث_ميزة(message.chat.id, اوامر_الميزات[item], 1 if cmd == "تفعيل" else 0)
            bot.reply_to(message, f"{'✅ تم تفعيل' if cmd == 'تفعيل' else '❌ تم تعطيل'} {item}")
        else: bot.reply_to(message, "❌ الميزة غير موجودة")

    @bot.message_handler(commands=['الحاله'])
    def الحاله(message):
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT * FROM locks WHERE chat_id =?", (message.chat.id,)).fetchone()
        conn.close()
        if not result: return bot.reply_to(message, "❌ مافي اعدادات")
        text = "**حالة الاقفال:**\n"
        for i, key in enumerate(اوامر_القفل.keys()):
            text += f"{'🔒' if result[i+1] else '🔓'} {key}\n"
        bot.reply_to(message, text)

    @bot.message_handler(content_types=['text', 'photo', 'video', 'sticker', 'animation'])
    def فلتر_القفل(message):
        if message.from_user.id == ID_المطور_الاساسي: return
        if جيب_الرتبة(message.chat.id, message.from_user.id)!= "عضو": return
        cid = message.chat.id

        if جيب_قفل(cid, "روابط") and message.text and ("http" in message.text or "t.me" in message.text):
            bot.delete_message(cid, message.message_id); return bot.send_message(cid, "🚫 الروابط مقفلة")
        if جيب_قفل(cid, "تاك") and message.text and "@" in message.text:
            bot.delete_message(cid, message.message_id); return bot.send_message(cid, "🚫 التاك مقفل")
        if جيب_قفل(cid, "صور") and message.content_type == "photo": bot.delete_message(cid, message.message_id); return bot.send_message(cid, "🚫 الصور مقفلة")
        if جيب_قفل(cid, "فيديو") and message.content_type == "video": bot.delete_message(cid, message.message_id); return bot.send_message(cid, "🚫 الفيديو مقفل")
        if جيب_قفل(cid, "ملصقات") and message.content_type == "sticker": bot.delete_message(cid, message.message_id); return bot.send_message(cid, "🚫 الملصقات مقفلة")
        if جيب_قفل(cid, "متحركه") and message.content_type == "animation": bot.delete_message(cid, message.message_id); return bot.send_message(cid, "🚫 المتحركة مقفلة")
        if جيب_قفل(cid, "دردشه") and message.content_type == "text": bot.delete_message(cid, message.message_id); return bot.send_message(cid, "🚫 الدردشة مقفلة")
