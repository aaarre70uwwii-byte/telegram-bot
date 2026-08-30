import sqlite3
import random
import requests

DB_NAME = "service_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS inline_replies (chat_id INTEGER, trigger TEXT, reply TEXT, type TEXT, PRIMARY KEY(chat_id, trigger))")
    cursor.execute("CREATE TABLE IF NOT EXISTS multi_replies (chat_id INTEGER, trigger TEXT, reply TEXT)")
    conn.commit()
    conn.close()

init_db()

def register_service_handlers(bot):

    # ===== قائمة الاوامر =====
    @bot.message_handler(commands=['الخدميه'], chat_types=['group','supergroup','private'])
    def service_menu(m):
        bot.reply_to(m, """- اهلا بك عزي
- اوامر الخدميه :
━━━━━━━━━━━━
• نسبه الحب
• نسبه الغباء - بالرد
• تحبه - بالرد
• ارسل + الكلام + اليوزر زاجل
• صيح
• صيح + اليوزر
• شبيهي - شبيهتي
• اهديه بالرد
• اهديه + يوزر الشخص
• شرايك في افتاري
• افتاره بالرد
• البايو بالرد
• افلام
• نسبه انوثتها - بالرد
• نسبه رجولته - بالرد
• البوت السحري
• قوقل + كلام البحث
• تطبيق + اسم التطبيق
• تحميل لعبه + اسم اللعبه
• معنى + اسمك
• العمر + عمرك
• زخرف + اسمك
• ترجم عربي + الكلام
• ترجم انقليزي + الكلام
• قران - اذكار - شعر - اقتباسات
• ثريد - قصص - اطربني - اغاني
• هيدرات - جداريات - ميمز - ايدت
• قيفات - افتارات
• نادي المطور
• من ضافني
━━━━━━━━━━━━
**التحميل:**
ساوند + الرابط
تيك + الرابط
تويتر + الرابط
━━━━━━━━━━━━""")

    @bot.message_handler(func=lambda m: True, chat_types=['group','supergroup','private'])
    def process_service(m):
        text = m.text.strip()
        chat_id = m.chat.id
        user = m.from_user

        # ===== نسب =====
        if text == "نسبه الحب":
            num = random.randint(1,100)
            bot.reply_to(m, f"نسبه حبك هي: {num}% ❤️")
        if text.startswith("نسبه الغباء") and m.reply_to_message:
            num = random.randint(1,100)
            bot.reply_to(m, f"نسبه غباء {m.reply_to_message.from_user.first_name} هي: {num}% 😂")
        if text.startswith("نسبه انوثتها") and m.reply_to_message:
            num = random.randint(1,100)
            bot.reply_to(m, f"نسبه انوثه {m.reply_to_message.from_user.first_name} هي: {num}% 👩")
        if text.startswith("نسبه رجولته") and m.reply_to_message:
            num = random.randint(1,100)
            bot.reply_to(m, f"نسبه رجوله {m.reply_to_message.from_user.first_name} هي: {num}% 👨")

        # ===== تحبه =====
        if text == "تحبه" and m.reply_to_message:
            answers = ["اي احبه موت ❤️", "لا اكرهه 😂", "عادي"]
            bot.reply_to(m, random.choice(answers))

        # ===== الزاجل =====
        if text.startswith("ارسل") and "زاجل" in text:
            parts = text.split(" ", 2)
            if len(parts) >= 3:
                msg, username = parts[1], parts[2]
                bot.reply_to(m, f"📨 تم ارسال الزاجل لـ {username}\nالرسالة: {msg}")

        # ===== الصياح =====
        if text == "صيح":
            bot.reply_to(m, f"اااااااه {user.first_name} ليش تصيح 😂")
        if text.startswith("صيح"):
            username = text.split(" ", 1)[1]
            bot.reply_to(m, f"ااه {username} ليش تصيح 😂")

        # ===== الشبيه =====
        if text == "شبيهي":
            bot.reply_to(m, f"شبيهك هو {random.choice(['احمد', 'محمد', 'علي'])}")
        if text == "شبيهتي":
            bot.reply_to(m, f"شبيهتك هي {random.choice(['فاطمة', 'سارة', 'نور'])}")

        # ===== الاهداء =====
        if text == "اهديه" and m.reply_to_message:
            gifts = ["🌹 وردة", "💍 خاتم", "🍫 شوكولاته"]
            bot.reply_to(m, f"اهديت {m.reply_to_message.from_user.first_name} {random.choice(gifts)}")
        if text.startswith("اهديه"):
            username = text.split(" ", 1)[1]
            bot.reply_to(m, f"اهديت {username} 🌹")

        # ===== معلومات الحساب =====
        if text == "شرايك في افتاري":
            bot.reply_to(m, "افتارك جميل جدا 🔥")
        if text == "افتاره" and m.reply_to_message:
            try:
                photos = bot.get_user_profile_photos(m.reply_to_message.from_user.id, limit=1)
                bot.send_photo(m.chat.id, photos.photos[0][0].file_id, caption="افتاره")
            except: bot.reply_to(m, "ماعنده صورة")
        if text == "البايو" and m.reply_to_message:
            try:
                info = bot.get_chat(m.reply_to_message.from_user.id)
                bot.reply_to(m, f"البايو: {info.bio if info.bio else 'فاضي'}")
            except: bot.reply_to(m, "ماقدر اجيب البايو")

        # ===== محتوى عشوائي =====
        content = {
            "افلام": ["فيلم 1", "فيلم 2", "فيلم 3"],
            "قران": ["اية الكرسي", "سورة الملك"],
            "اذكار": ["سبحان الله", "الحمدلله"],
            "شعر": ["اذا الشعب يوما اراد الحياة"],
            "اقتباسات": ["الصبر مفتاح الفرج"],
            "ثريد": ["ثريد عن البرمجة"],
            "قصص": ["قصة قصيرة"],
            "اطربني": ["اغنية 1", "اغنية 2"],
            "اغاني": ["اغنية عربية", "اغنية اجنبية"],
            "هيدرات": ["هيدر 1"],
            "جداريات": ["جدارية 1"],
            "ميمز": ["ميمز 1"],
            "ايدت": ["ايدت 1"],
        }
        if text in content:
            bot.reply_to(m, random.choice(content[text]))

        # ===== قيفات وافتارات =====
        if "قيفات" in text:
            bot.reply_to(m, "ارسل: قيفات اطفال - قيفات رومنسيه - قيفات كيبوب")
        if "افتارات" in text:
            bot.reply_to(m, "ارسل: افتارات بنات - افتارات عيال - افتارات انمي")

        # ===== ادوات =====
        if text.startswith("قوقل"):
            query = text.split(" ", 1)[1]
            bot.reply_to(m, f"ابحث في قوقل: https://google.com/search?q={query}")
        if text.startswith("ترجم عربي"):
            txt = text.split(" ", 2)[2]
            bot.reply_to(m, f"الترجمة: {txt} [ترجمة وهمية]")
        if text.startswith("ترجم انقليزي"):
            txt = text.split(" ", 2)[2]
            bot.reply_to(m, f"Translation: {txt} [fake]")
        if text.startswith("زخرف"):
            name = text.split(" ", 1)[1]
            bot.reply_to(m, f"زخرفة: 『{name}』『★{name}★』")

        # ===== نادي المطور =====
        if text == "نادي المطور":
            bot.reply_to(m, "@YourUsername تعال المطور يناديك")

        # ===== من ضافني =====
        if text == "من ضافني":
            bot.reply_to(m, "هذي الميزة تحتاج تخزين من اول ما دخلت")

        # ===== التحميل =====
        if text.startswith("ساوند") or text.startswith("تيك") or text.startswith("تويتر"):
            bot.reply_to(m, "جاري تحميل الرابط... الميزة تحتاج مكتبة خارجية")

        # ===== تحويل الصيغ =====
        if text.startswith("تحويل") and m.reply_to_message:
            bot.reply_to(m, "تم التحويل... تحتاج مكتبة ffmpeg")
