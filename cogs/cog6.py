import sqlite3
import random
import requests
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443

def setup(bot, المطور_الاساسي, admins):

    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS owner_replies
                    (chat_id INTEGER, trigger TEXT, reply TEXT, PRIMARY KEY(chat_id, trigger))''')
        c.execute('''CREATE TABLE IF NOT EXISTS inline_replies
                    (chat_id INTEGER, trigger TEXT, reply TEXT, PRIMARY KEY(chat_id, trigger))''')
        c.execute('''CREATE TABLE IF NOT EXISTS multi_replies
                    (chat_id INTEGER, trigger TEXT, reply TEXT, PRIMARY KEY(chat_id, trigger, reply))''')
        c.execute('''CREATE TABLE IF NOT EXISTS who_added
                    (chat_id INTEGER, user_id INTEGER, added_by INTEGER)''')
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

    def هو_مالك(chat_id, user_id):
        return جيب_الرتبة(chat_id, user_id) in ["منشئ","مالك","مالك_اساسي","مطور","مطور_اساسي"]

    # ========== 1. اوامر النسب والالعاب ==========
    @bot.message_handler(commands=['نسبه_الحب'])
    def نسبه_الحب(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        نسبه = random.randint(1, 100)
        bot.reply_to(message, f"❤️ نسبة الحب بينكم: {نسبه}%")

    @bot.message_handler(commands=['نسبه_الغباء'])
    def نسبه_الغباء(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        نسبه = random.randint(1, 100)
        bot.reply_to(message, f"🤡 نسبة الغباء: {نسبه}%")

    @bot.message_handler(commands=['تحبه'])
    def تحبه(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        اجوبه = ["اكيد احبه ❤️", "لا ما احبه 😒", "نص نص", "اموت فيه"]
        bot.reply_to(message, random.choice(اجوبه))

    @bot.message_handler(commands=['صيح'])
    def صيح(message):
        try: username = message.text.split(" ", 1)[1]
        except: username = ""
        if username: bot.reply_to(message, f"📢 {username} تعال يصيحون عليك")
        else: bot.reply_to(message, "📢 صييييح")

    @bot.message_handler(commands=['شبيهي', 'شبيهتي'])
    def شبيهي(message):
        bot.reply_to(message, "🚧 ميزة الشبيه قيد التطوير")

    @bot.message_handler(commands=['اهديه'])
    def اهديه(message):
        if message.reply_to_message: target = message.reply_to_message.from_user.first_name
        else:
            try: target = message.text.split(" ", 1)[1]
            except: return bot.reply_to(message, "⚠️ رد او اكتب اليوزر")
        هدايا = ["🌹 وردة", "💍 خاتم", "🎁 هدية", "🍫 شوكولاته"]
        bot.reply_to(message, f"تم اهداء {target} {random.choice(هدايا)}")

    @bot.message_handler(commands=['شرايك_في_افتاري', 'افتاره'])
    def افتاري(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الصورة")
        اراء = ["افتارك فخم 🔥", "حلو بس يحتاج تعديل", "افتارك توب"]
        bot.reply_to(message, random.choice(اراء))

    @bot.message_handler(commands=['البايو'])
    def البايو(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        try: bio = bot.get_chat(message.reply_to_message.from_user.id).bio
        except: bio = "لا يوجد بايو"
        bot.reply_to(message, f"📝 البايو:\n{bio}")

    @bot.message_handler(commands=['نسبه_انوثتها', 'نسبه_رجولته'])
    def النسب(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        نسبه = random.randint(1, 100)
        if "انوثتها" in message.text: bot.reply_to(message, f"👩 نسبة الانوثة: {نسبه}%")
        else: bot.reply_to(message, f"👨 نسبة الرجولة: {نسبه}%")

    # ========== 2. اوامر البحث والترجمة ==========
    @bot.message_handler(commands=['قوقل'])
    def قوقل(message):
        try: query = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /قوقل كلام البحث")
        bot.reply_to(message, f"🔍 نتائج البحث عن: {query}\nhttps://www.google.com/search?q={query}")

    @bot.message_handler(commands=['تطبيق'])
    def تطبيق(message):
        try: name = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /تطبيق اسم التطبيق")
        bot.reply_to(message, f"📱 ابحث عن {name} في المتجر")

    @bot.message_handler(commands=['تحميل_لعبه'])
    def تحميل_لعبه(message):
        try: name = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /تحميل_لعبه اسم اللعبة")
        bot.reply_to(message, f"🎮 جاري البحث عن تحميل {name}")

    @bot.message_handler(commands=['معنى'])
    def معنى(message):
        try: name = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /معنى اسمك")
        bot.reply_to(message, f"📖 معنى {name}: قيد التطوير")

    @bot.message_handler(commands=['العمر'])
    def العمر(message):
        try: age = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /العمر عمرك")
        bot.reply_to(message, f"🎂 عمرك {age} سنة")

    @bot.message_handler(commands=['زخرف'])
    def زخرف(message):
        try: name = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /زخرف اسمك")
        bot.reply_to(message, f"✨ {name} ✨ \n۝ {name} ۝ \n★彡{name}彡★")

    @bot.message_handler(commands=['ترجم_عربي', 'ترجم_انقليزي'])
    def ترجم(message):
        try: text = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /ترجم_عربي النص")
        bot.reply_to(message, f"🌐 الترجمة: {text}")

    # ========== 3. اوامر المحتوى ==========
    @bot.message_handler(commands=['قران', 'اذكار', 'شعر', 'قصائد', 'اقتباسات', 'ثريد', 'قصص', 'كتب', 'اطربني', 'اغاني', 'هيدرات', 'جداريات', 'ميمز', 'ايدت'])
    def محتوى(message):
        محتوايات = {
            'قران': "📖 آية اليوم: وقل ربي زدني علما",
            'اذكار': "🌅 اذكار الصباح: سبحان الله وبحمده",
            'شعر': "✍️ شعر: ما كل ما يتمنى المرء يدركه",
            'اقتباسات': "💬 اقتباس: كن انت التغيير",
            'اغاني': "🎵 تم ارسال اغنية"
        }
        cmd = message.text.replace("/", "")
        bot.reply_to(message, محتوايات.get(cmd, "🚧 المحتوى قيد التطوير"))

    @bot.message_handler(commands=['قيفات', 'افتارات'])
    def صور(message):
        try: النوع = message.text.split(" ", 1)[1]
        except: النوع = "عام"
        bot.reply_to(message, f"🖼️ تم ارسال {النوع}")

    @bot.message_handler(commands=['البوت_السحري'])
    def البوت_السحري(message):
        bot.reply_to(message, "🧙‍♂️ انا البوت السحري. اطلب امنيتك")

    @bot.message_handler(commands=['نادي_المطور'])
    def نادي_المطور(message):
        for admin_id in admins: bot.send_message(admin_id, f"📢 {message.from_user.first_name} نادى المطور")
        bot.reply_to(message, "✅ تم ابلاغ المطور")

    @bot.message_handler(commands=['تفعيل_كليشة_المطور'])
    def تفعيل_كليشة_المطور(message):
        if not هو_مالك(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمالك فقط")
        bot.reply_to(message, "✅ تم تفعيل كليشة المطور")

    @bot.message_handler(commands=['من_ضافني'])
    def من_ضافني(message):
        conn = sqlite3.connect(DB); result = conn.execute("SELECT added_by FROM who_added WHERE chat_id =? AND user_id =?", (message.chat.id, message.from_user.id)).fetchone(); conn.close()
        if result: bot.reply_to(message, f"👤 الشخص اللي ضافك: {result[0]}")
        else: bot.reply_to(message, "❌ ما اعرف من ضافك")

    @bot.message_handler(commands=['اضف_رد_المالك'])
    def اضف_رد_المالك(message):
        if not هو_مالك(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمالك فقط")
        try: _, trigger, reply = message.text.split(" ", 2)
        except: return bot.reply_to(message, "⚠️ الاستخدام: /اضف_رد_المالك كلمة الرد")
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO owner_replies VALUES (?,?,?)", (message.chat.id, trigger, reply)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم اضافة رد المالك: {trigger}")

    @bot.message_handler(commands=['اضف_رد_انلاين'])
    def اضف_رد_انلاين(message):
        if not هو_مالك(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمالك فقط")
        try: _, trigger, reply = message.text.split(" ", 2)
        except: return bot.reply_to(message, "⚠️ الاستخدام: /اضف_رد_انلاين كلمة الرد")
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO inline_replies VALUES (?,?,?)", (message.chat.id, trigger, reply)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم اضافة رد انلاين: {trigger}")

    @bot.message_handler(commands=['اضف_رد_متعدد'])
    def اضف_رد_متعدد(message):
        if not هو_مالك(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمالك فقط")
        try: _, trigger, reply = message.text.split(" ", 2)
        except: return bot.reply_to(message, "⚠️ الاستخدام: /اضف_رد_متعدد كلمة الرد")
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO multi_replies VALUES (?,?,?)", (message.chat.id, trigger, reply)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم اضافة رد متعدد: {trigger}")

    @bot.message_handler(commands=['ارسل'])
    def ارسل_زاجل(message):
        try: _, text, username = message.text.split(" ", 2)
        except: return bot.reply_to(message, "⚠️ الاستخدام: /ارسل الكلام @username")
        bot.reply_to(message, f"📨 تم ارسال الرسالة الى {username}")

    # ========== 4. اوامر التحميل ==========
    @bot.message_handler(commands=['ساوند', 'تيك', 'تويتر'])
    def التحميل(message):
        try: link = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /ساوند الرابط")
        if "ساوند" in message.text: bot.reply_to(message, f"🎵 جاري تحميل ساوند: {link}")
        elif "تيك" in message.text: bot.reply_to(message, f"📱 جاري تحميل تيك: {link}")
        else: bot.reply_to(message, f"🐦 جاري تحميل تويتر: {link}")

    @bot.message_handler(commands=['تحويل'])
    def تحويل(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الفيديو")
        try: النوع = message.text.split(" ", 1)[1]
        except: النوع = "صوت"
        bot.reply_to(message, f"🔄 جاري تحويل الفيديو الى {النوع}")

    # ========== امر قائمة 6 ==========
    @bot.message_handler(commands=['م6'])
    def م6(message):
        bot.reply_to(message, """<b>• اهلا بك عزي
- اوامر الخدميه :
━━━━━━━━━━━━
- نسبه_الحب
- نسبه_الغباء - بالرد
- تحبه - بالرد
- ارسل + الكلام + اليوزر
- صيح - صيح + اليوزر
- شبيهي - شبيهتي
- اهديه - اهديه + يوزر
- شرايك_في_افتاري
- افتاره - بالرد
- البايو - بالرد
- اضف_رد_المالك
- افلام
- نسبه_انوثتها - نسبه_رجولته
- البوت_السحري
- قوقل + كلام
- تطبيق + اسم
- تحميل_لعبه + اسم
- معنى + اسمك
- العمر + عمرك
- زخرف + اسمك
- ترجم_عربي + الكلام
- ترجم_انقليزي + الكلام
- قران - اذكار - شعر - اقتباسات
- ثريد - قصص - اطربني - اغاني
- هيدرات - جداريات - ميمز - ايدت
- قيفات - افتارات
- نادي_المطور
- تفعيل_كليشة_المطور
- من_ضافني
- اضف_رد_انلاين
- اضف_رد_متعدد

التحميل :
- ساوند + الرابط
- تيك + الرابط
- تويتر + الرابط
- تحويل + النوع - بالرد
━━━━━━━━━━━━</b>""", parse_mode="HTML")

    print("✅ تم تحميل: cog6.py - ملف الخدميه")
