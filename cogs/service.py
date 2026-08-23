import sqlite3
import random
import requests
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443

def setup_service(bot):

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
        conn.execute("CREATE TABLE IF NOT EXISTS owner_replies (chat_id INTEGER, word TEXT, reply TEXT, type TEXT DEFAULT 'نص', PRIMARY KEY(chat_id, word))")
        conn.execute("CREATE TABLE IF NOT EXISTS added_by (chat_id INTEGER, user_id INTEGER, added_by INTEGER, PRIMARY KEY(chat_id, user_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS magic_bot (chat_id INTEGER PRIMARY KEY, text TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS clich_dev (chat_id INTEGER PRIMARY KEY, type TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS dev_contact (chat_id INTEGER PRIMARY KEY, username TEXT)")
        conn.commit(); conn.close()
    انشاء_جداول()

    # ========== 1. اوامر النسب ==========
    @bot.message_handler(commands=['نسبه_الحب'])
    def نسبه_الحب(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        n = random.randint(1,100)
        bot.reply_to(message, f"💘 نسبة حب {message.reply_to_message.from_user.first_name} لك: {n}%")

    @bot.message_handler(commands=['نسبه_الغباء', 'نسبه_انوثتها', 'نسبه_رجولته'])
    def نسب(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        n = random.randint(1,100)
        t = "الغباء" if "غباء" in message.text else "الانوثة" if "انوثتها" in message.text else "الرجولة"
        bot.reply_to(message, f"📊 نسبة {t} لـ {message.reply_to_message.from_user.first_name}: {n}%")

    @bot.message_handler(commands=['تحبه'])
    def تحبه(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        res = random.choice(["اكيد احبه ❤️", "لا ما احبه 💔", "ممكن شويه 😅"])
        bot.reply_to(message, f"{message.reply_to_message.from_user.first_name}: {res}")

    # ========== 2. الزاجل والصياح ==========
    @bot.message_handler(commands=['ارسل'])
    def زاجل(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        try:
            _, text, username = message.text.split(" ", 2)
            bot.send_message(f"@{username}", f"📨 رسالة من {message.from_user.first_name}:\n{text}")
            bot.reply_to(message, f"✅ تم ارسال الزاجل لـ @{username}")
        except: bot.reply_to(message, "⚠️ الصيغة: /ارسل الكلام @username")

    @bot.message_handler(commands=['صيح'])
    def صيح(message):
        if len(message.text.split()) > 1:
            username = message.text.split(" ",1)[1]
            try: bot.send_message(f"@{username}", f"🔔 {message.from_user.first_name} يصيح عليك")
            except: pass
            bot.reply_to(message, "✅ تم الصياح")
        else:
            bot.reply_to(message, f"📢 {message.from_user.first_name} يصيح")

    # ========== 3. الاهداء والشبيه ==========
    @bot.message_handler(commands=['شبيهي', 'شبيهتي', 'اهديني'])
    def شبيه_اهداء(message):
        imgs = {"شبيهي": "boy", "شبيهتي": "girl", "اهديني": "flower"}
        for key, url in imgs.items():
            if key in message.text:
                bot.send_photo(message.chat.id, f"https://picsum.photos/200/200?{url}", caption=f"{message.from_user.first_name} هذا {key}")
                break

    @bot.message_handler(commands=['اهديه'])
    def اهديه(message):
        target = message.reply_to_message.from_user.first_name if message.reply_to_message else message.text.split(" ",1)[1] if len(message.text.split()) > 1 else "؟"
        bot.send_photo(message.chat.id, "https://picsum.photos/200/200?gift", caption=f"🎁 اهداء من {message.from_user.first_name} الى {target}")

    # ========== 4. الافتار والبايو والافلام ==========
    @bot.message_handler(commands=['شرايك_في_افتاري', 'افتاره', 'البايو', 'افلام'])
    def افاتار(message):
        if "افلام" in message.text: return bot.reply_to(message, "🎬 افلام مقترحة:\n1. فلم اكشن\n2. فلم كوميدي\n3. فلم رعب")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        try:
            photos = bot.get_user_profile_photos(message.reply_to_message.from_user.id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][0].file_id
                if "شرايك" in message.text: bot.send_photo(message.chat.id, file_id, caption="🔥 افتارك فخم")
                elif "افتاره" in message.text: bot.send_photo(message.chat.id, file_id)
                elif "البايو" in message.text:
                    user = bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id).user
                    bot.reply_to(message, f"📝 بايو {message.reply_to_message.from_user.first_name}:\n{user.bio if user.bio else 'مافي بايو'}")
            else: bot.reply_to(message, "❌ مافي صورة")
        except: bot.reply_to(message, "❌ خطأ")

    # ========== 5. ادوات البحث ==========
    @bot.message_handler(commands=['قوقل', 'تطبيق', 'تحميل_لعبه', 'معنى', 'العمر', 'زخرف'])
    def ادوات(message):
        cmd = message.text.split(" ", 1)
        if len(cmd) < 2: return bot.reply_to(message, "⚠️ اكتب الكلمة")
        text = cmd[1]
        if "قوقل" in message.text: bot.reply_to(message, f"🔍 https://www.google.com/search?q={text}")
        if "تطبيق" in message.text: bot.reply_to(message, f"📱 {text}\nhttps://play.google.com/store/search?q={text}")
        if "تحميل_لعبه" in message.text: bot.reply_to(message, f"🎮 {text}\nhttps://play.google.com/store/search?q={text}")
        if "معنى" in message.text: bot.reply_to(message, f"📖 معنى {text}: ابحث في المعجم")
        if "العمر" in message.text: bot.reply_to(message, f"🎂 عمرك {text} سنة")
        if "زخرف" in message.text: bot.reply_to(message, f"✨ {text}\n♡{text}♡\n❤{text}❤\n『{text}』")

    @bot.message_handler(commands=['ترجم_عربي', 'ترجم_انقليزي'])
    def ترجم(message):
        try: text = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الصيغة: /ترجم_عربي hello")
        bot.reply_to(message, f"🔄 ترجمة: {text}")

    # ========== 6. ديني وتسلية ومحتوى ==========
    @bot.message_handler(commands=['قران', 'اذكار', 'شعر', 'اقتباسات', 'ثريد', 'قصص', 'كتب', 'شوية_حكي'])
    def محتوى(message):
        data = {
            "قران": "﴿ وقل رب زدني علما ﴾",
            "اذكار": "سبحان الله وبحمده 100 مرة",
            "شعر": "اذا الشعب يوما اراد الحياة",
            "اقتباسات": "العقل زينة",
            "ثريد": "ثريد عن النجاح: 1- اسعى 2- اجتهد 3- اصبر",
            "قصص": "كان يا مكان في قديم الزمان",
            "كتب": "كتاب اليوم: فن اللامبالاة",
            "شوية_حكي": "نصيحة اليوم: لا تستسلم"
        }
        for key, val in data.items():
            if key in message.text: bot.reply_to(message, val)

    @bot.message_handler(commands=['اطربني', 'اغاني', 'هيدرات', 'جداريات', 'ميمز', 'باب_الحاره', 'ايدت'])
    def ميديا(message):
        types = {"اطربني": "music", "اغاني": "song", "هيدرات": "header", "جداريات": "wallpaper", "ميمز": "meme", "باب_الحاره": "series", "ايدت": "edit"}
        for key, val in types.items():
            if key in message.text: bot.send_photo(message.chat.id, f"https://picsum.photos/400/400?{val}", caption=f"🎵 {key}")

    # ========== 7. البوت السحري ونادي المطور ==========
    @bot.message_handler(commands=['البوت_السحري'])
    def سحري(message):
        conn = sqlite3.connect(DB)
        res = conn.execute("SELECT text FROM magic_bot WHERE chat_id =?", (message.chat.id,)).fetchone()
        conn.close()
        bot.reply_to(message, res[0] if res else "🔮 اهلا بك في البوت السحري")

    @bot.message_handler(commands=['نادي_المطور'])
    def نادي_المطور(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return
        if len(message.text.split()) > 1:
            username = message.text.split(" ",1)[1]
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO dev_contact VALUES (?,?)", (message.chat.id, username)); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم حفظ يوزر المطور: {username}")
        else:
            conn = sqlite3.connect(DB)
            res = conn.execute("SELECT username FROM dev_contact WHERE chat_id =?", (message.chat.id,)).fetchone()
            conn.close()
            bot.reply_to(message, f"👑 تواصل مع المطور: @{res[0]}" if res else "❌ مافي يوزر مطور محفوظ")

    # ========== 8. القيفات والافتارات ==========
    @bot.message_handler(commands=['قيفات', 'افتارات'])
    def قيفات(message):
        types = message.text.split(" ",1)[1] if len(message.text.split()) > 1 else "بنات"
        bot.send_photo(message.chat.id, f"https://picsum.photos/300/300?{types}", caption=f"🖼️ {message.text}")

    # ========== 9. تفعيل كليشة المطور ==========
    @bot.message_handler(commands=['تفعيل_كليشة_المطور'])
    def كليشة_مطور(message):
        if message.from_user.id!= ID_المطور_الاساسي: return
        type = message.text.split(" ",1)[1] if len(message.text.split()) > 1 else "افتار"
        conn = sqlite3.connect(DB)
        conn.execute("INSERT OR REPLACE INTO clich_dev VALUES (?,?)", (message.chat.id, type))
        conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم تفعيل كليشة المطور: {type}")

    # ========== 10. من ضافني ==========
    @bot.message_handler(commands=['من_ضافني'])
    def من_ضافني(message):
        conn = sqlite3.connect(DB)
        res = conn.execute("SELECT added_by FROM added_by WHERE chat_id =? AND user_id =?", (message.chat.id, message.from_user.id)).fetchone()
        conn.close()
        bot.reply_to(message, f"👤 اللي ضافك: {res[0] if res else 'البوت'}")

    # ========== 11. ردود المالك ==========
    @bot.message_handler(commands=['اضف_رد_المالك'])
    def رد_مالك(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return
        try:
            _, word, reply = message.text.split(" ", 2)
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO owner_replies VALUES (?,?,?,'نص')", (message.chat.id, word, reply)); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم اضافة الرد: {word}")
        except: bot.reply_to(message, "⚠️ الصيغة: /اضف_رد_المالك الكلمة الرد")

    @bot.message_handler(commands=['اضف_رد_انلاين'])
    def رد_انلاين(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return
        try:
            _, word, reply = message.text.split(" ", 2)
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO owner_replies VALUES (?,?,?,'انلاين')", (message.chat.id, word, reply)); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم اضافة الرد الانلاين: {word}")
        except: bot.reply_to(message, "⚠️ الصيغة: /اضف_رد_انلاين الكلمة الرد")

    @bot.message_handler(commands=['اضف_رد_متعدد'])
    def رد_متعدد(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return
        try:
            _, word, reply = message.text.split(" ", 2)
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO owner_replies VALUES (?,?,?,'متعدد')", (message.chat.id, word, reply)); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم اضافة الرد المتعدد: {word}")
        except: bot.reply_to(message, "⚠️ الصيغة: /اضف_رد_متعدد الكلمة الرد")

    @bot.message_handler(content_types=['text'])
    def فلتر_رد_مالك(message):
        conn = sqlite3.connect(DB)
        res = conn.execute("SELECT reply, type FROM owner_replies WHERE chat_id =? AND word =?", (message.chat.id, message.text)).fetchone()
        conn.close()
        if res:
            if res[1] == 'انلاين':
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("اضغط هنا", callback_data="none"))
                bot.reply_to(message, res[0], reply_markup=markup)
            else: bot.reply_to(message, res[0])

    # ========== 12. التحميل ==========
    @bot.message_handler(commands=['ساوند', 'تيك', 'تويتر'])
    def تحميل(message):
        if len(message.text.split()) < 2: return bot.reply_to(message, "⚠️ ارسل الرابط")
        link = message.text.split(" ",1)[1]
        bot.reply_to(message, f"⏳ جاري تحميل: {link}")

    # ========== 13. تحويل الصيغ ==========
    @bot.message_handler(content_types=['video', 'voice', 'audio', 'animation'])
    def تحويل(message):
        if message.caption and "تحويل" in message.caption:
            type = "صوت" if "صوت" in message.caption else "متحركه" if "متحركه" in message.caption else "بصمه"
            bot.reply_to(message, f"🔄 جاري تحويل الى {type}...")

    # ========== 14. حفظ من ضاف من ==========
    @bot.message_handler(content_types=['new_chat_members'])
    def حفظ_الاضافة(message):
        for user in message.new_chat_members:
            conn = sqlite3.connect(DB)
            conn.execute("INSERT OR REPLACE INTO added_by VALUES (?,?,?)", (message.chat.id, user.id, message.from_user.id))
            conn.commit(); conn.close()
