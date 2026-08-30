import sqlite3
import random
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

DB_NAME = "service_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS inline_replies (chat_id INTEGER, trigger TEXT, reply TEXT, type TEXT, PRIMARY KEY(chat_id, trigger))")
    cursor.execute("CREATE TABLE IF NOT EXISTS multi_replies (chat_id INTEGER, trigger TEXT, reply TEXT)")
    conn.commit()
    conn.close()

init_db()

def get_service_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("❤️ نسب", callback_data="ser_ratio"),
        InlineKeyboardButton("📨 زاجل", callback_data="ser_zajel"),
        InlineKeyboardButton("🎁 اهداء", callback_data="ser_gift")
    )
    markup.add(
        InlineKeyboardButton("📚 محتوى", callback_data="ser_content"),
        InlineKeyboardButton("🔍 بحث", callback_data="ser_search"),
        InlineKeyboardButton("⬇️ تحميل", callback_data="ser_download")
    )
    return markup

def register_service_handlers(bot):

    content_db = {
        "افلام": ["فيلم 1: Inception", "فيلم 2: Interstellar", "فيلم 3: The Dark Knight"],
        "قران": ["اية الكرسي: الله لا اله الا هو الحي القيوم", "سورة الاخلاص: قل هو الله احد"],
        "اذكار": ["سبحان الله", "الحمدلله", "الله اكبر"],
        "شعر": ["اذا الشعب يوما اراد الحياة", "قفا نبك من ذكرى حبيب ومنزل"],
        "اقتباسات": ["الصبر مفتاح الفرج", "من جد وجد ومن سار على الدرب وصل"],
        "ثريد": ["ثريد: 10 اسرار عن البرمجة"],
        "قصص": ["قصة: كان هناك ولد ذكي"],
        "اطربني": ["🎵 اغنية عربية", "🎵 اغنية اجنبية"],
        "اغاني": ["اغنية 1", "اغنية 2"],
        "هيدرات": ["صورة هيدر 1"],
        "جداريات": ["جدارية 1"],
        "ميمز": ["ميمز مضحك 1"],
        "ايدت": ["ايدت انمي 1"],
        "قيفات": ["قيف رومنسي 1", "قيف كيبوب 1"],
        "افتارات": ["افتار بنات 1", "افتار عيال 1"],
    }

    @bot.message_handler(commands=['الخدميه'], chat_types=['group','supergroup','private'])
    @bot.message_handler(func=lambda m: m.text == "الخدمية", chat_types=['group','supergroup','private'])
    def service_menu(m):
        bot.reply_to(m, "⚙️ **قائمة الخدمية**\nاختار القسم:", parse_mode="Markdown", reply_markup=get_service_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("ser_"))
    def service_buttons(call):
        if call.data == "ser_ratio":
            bot.answer_callback_query(call.id, "اكتب: نسبة الحب / نسبة الغباء بالرد", show_alert=True)
        elif call.data == "ser_zajel":
            bot.answer_callback_query(call.id, "اكتب: ارسل الكلام @اليوزر زاجل", show_alert=True)
        elif call.data == "ser_gift":
            bot.answer_callback_query(call.id, "اكتب: اهديه بالرد او اهديه @اليوزر", show_alert=True)
        elif call.data == "ser_content":
            markup = InlineKeyboardMarkup(row_width=3)
            for key in ["قران","اذكار","شعر","اقتباسات","افلام","ميمز"]:
                markup.add(InlineKeyboardButton(key, callback_data=f"content_{key}"))
            bot.edit_message_text("📚 اختار المحتوى:", call.message.chat.id, call.message_id, reply_markup=markup)
        elif call.data == "ser_search":
            bot.answer_callback_query(call.id, "اكتب: قوقل + البحث او ترجم عربي + النص", show_alert=True)
        elif call.data == "ser_download":
            bot.answer_callback_query(call.id, "اكتب: ساوند + الرابط او تيك + الرابط", show_alert=True)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("content_"))
    def send_content(call):
        key = call.data.replace("content_", "")
        bot.answer_callback_query(call.id, random.choice(content_db.get(key, ["فاضي"])), show_alert=True)

    @bot.message_handler(func=lambda m: True, chat_types=['group','supergroup','private'])
    def process_service(m):
        if not m.text: return
        text = m.text.strip()
        chat_id = m.chat.id
        user = m.from_user

        # ===== نسب =====
        if text == "نسبه الحب":
            num = random.randint(1,100)
            bot.reply_to(m, f"❤️ نسبه حبك هي: {num}%")
        if text.startswith("نسبه الغباء") and m.reply_to_message:
            num = random.randint(1,100)
            bot.reply_to(m, f"😂 نسبه غباء {m.reply_to_message.from_user.first_name} هي: {num}%")
        if text.startswith("نسبه انوثتها") and m.reply_to_message:
            num = random.randint(1,100)
            bot.reply_to(m, f"👩 نسبه انوثه {m.reply_to_message.from_user.first_name} هي: {num}%")
        if text.startswith("نسبه رجولته") and m.reply_to_message:
            num = random.randint(1,100)
            bot.reply_to(m, f"👨 نسبه رجوله {m.reply_to_message.from_user.first_name} هي: {num}%")

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
            bot.reply_to(m, f"ااه {user.first_name} ليش تصيح 😂")
        if text.startswith("صيح "):
            username = text.split(" ", 1)[1]
            bot.reply_to(m, f"ااه {username} ليش تصيح 😂")

        # ===== الشبيه =====
        if text == "شبيهي":
            bot.reply_to(m, f"شبيهك هو {random.choice(['احمد', 'محمد', 'علي', 'خالد'])}")
        if text == "شبيهتي":
            bot.reply_to(m, f"شبيهتك هي {random.choice(['فاطمة', 'سارة', 'نور', 'ريم'])}")

        # ===== الاهداء =====
        if text == "اهديه" and m.reply_to_message:
            gifts = ["🌹 وردة", "💍 خاتم", "🍫 شوكولاته", "🎁 هدية"]
            bot.reply_to(m, f"اهديت {m.reply_to_message.from_user.first_name} {random.choice(gifts)}")
        if text.startswith("اهديه "):
            username = text.split(" ", 1)[1]
            bot.reply_to(m, f"اهديت {username} 🌹")

        # ===== معلومات الحساب =====
        if text == "شرايك في افتاري":
            bot.reply_to(m, "افتارك جميل جدا 🔥")
        if text == "افتاره" and m.reply_to_message:
            try:
                photos = bot.get_user_profile_photos(m.reply_to_message.from_user.id, limit=1)
                bot.send_photo(m.chat.id, photos.photos[0][0].file_id, caption="📸 افتاره")
            except: bot.reply_to(m, "ماعنده صورة")
        if text == "البايو" and m.reply_to_message:
            try:
                info = bot.get_chat(m.reply_to_message.from_user.id)
                bot.reply_to(m, f"📝 البايو: {info.bio if info.bio else 'فاضي'}")
            except: bot.reply_to(m, "ماقدر اجيب البايو")

        # ===== محتوى عشوائي =====
        if text in content_db:
            bot.reply_to(m, random.choice(content_db[text]))

        # ===== ادوات =====
        if text.startswith("قوقل "):
            query = text.split(" ", 1)[1]
            bot.reply_to(m, f"🔍 ابحث في قوقل: https://google.com/search?q={query}")
        if text.startswith("ترجم عربي "):
            txt = text.split(" ", 2)[2]
            bot.reply_to(m, f"🇸🇦 الترجمة: {txt} [ترجمة وهمية]")
        if text.startswith("ترجم انقليزي "):
            txt = text.split(" ", 2)[2]
            bot.reply_to(m, f"🇺🇸 Translation: {txt} [fake]")
        if text.startswith("زخرف "):
            name = text.split(" ", 1)[1]
            bot.reply_to(m, f"✨ زخرفة: 『{name}』『★{name}★』『❥{name}❥』")

        # ===== نادي المطور =====
        if text == "نادي المطور":
            bot.reply_to(m, "@YourUsername تعال المطور يناديك")

        # ===== من ضافني =====
        if text == "من ضافني":
            bot.reply_to(m, "⚠️ هذي الميزة تحتاج تخزين من اول ما دخلت")

        # ===== التحميل =====
        if text.startswith("ساوند ") or text.startswith("تيك ") or text.startswith("تويتر "):
            link = text.split(" ", 1)[1]
            bot.reply_to(m, f"⬇️ جاري تحميل: {link}\nملاحظة: تحتاج مكتبة yt-dlp للتحميل الفعلي")

        # ===== تحويل الصيغ =====
        if text.startswith("تحويل") and m.reply_to_message:
            bot.reply_to(m, "🔄 تم التحويل... تحتاج مكتبة ffmpeg")
