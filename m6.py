from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, json, os, requests

FILE_SERVICE = 'service.json'
FILE_SETTINGS = 'settings.json'

def load_service():
    global service_data, settings
    if not os.path.exists(FILE_SERVICE): json.dump({}, open(FILE_SERVICE, 'w', encoding='utf-8'))
    if not os.path.exists(FILE_SETTINGS): json.dump({}, open(FILE_SETTINGS, 'w', encoding='utf-8'))
    service_data = json.load(open(FILE_SERVICE, 'r', encoding='utf-8'))
    settings = json.load(open(FILE_SETTINGS, 'r', encoding='utf-8'))

def save_service():
    json.dump(service_data, open(FILE_SERVICE, 'w', encoding='utf-8'), ensure_ascii=False)

load_service()

def show_service_menu(bot, chat_id):
    text = """• اهلا بك عزي
- اوامر الخدميه :
━━━━━━━━━━━━
• نسبه الحب
• نسبه الغباء - بالرد
• تحبه - بالرد
• ارسل + الكلام + اليوزر زاجل
• صيح
• صيح + اليوزر
• شبيهي - شبيهتي
• اهديني
• اهديه - بالرد
• شرايك في افتاري
• افتاره - بالرد
• البايو - بالرد
• افلام
• نسبه انوثتها - بالرد
• نسبه رجولته - بالرد
• البوت السحري
• قوقل + كلام البحث
• معنى + اسمك
• العمر + عمرك
• زخرف + اسمك
• ترجم عربي + الكلام
• ترجم انقليزي + الكلام
• قران
• اذكار
• شعر ، قصائد
• اقتباسات
• ثريد
• اطربني
• هيدرات
• جداريات
• ميمز
• كتب
• ايدت
• قيفات
• افتارات
━━━━━━━━━━━━
التحميل :
• ساوند + الرابط
• تيك + الرابط
• تويتر + الرابط
━━━━━━━━━━━━"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ الرجوع للقائمة الرئيسية", callback_data="back_to_main"))
    bot.send_message(chat_id, text, reply_markup=markup)

def is_admin(bot, chat_id, user_id):
    try: return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
    except: return False

def register_m6_handlers(bot):

    # ترحيب القروبات بصورة اجباري
    @bot.message_handler(content_types=['new_chat_members'])
    def welcome_group(m):
        welcome = settings.get('welcome', 'اهلا {name} نورتنا')
        photo = settings.get('welcome_photo')
        default_photo = "https://i.imgur.com/8Km9tLL.jpg" # غيرها بصورتك

        for new in m.new_chat_members:
            text = welcome.replace('{name}', new.first_name).replace('{id}', str(new.id)).replace('{username}', f"@{new.username}" if new.username else "")
            if photo:
                bot.send_photo(m.chat.id, photo, caption=text)
            else:
                bot.send_photo(m.chat.id, default_photo, caption=text) # دايما صورة

    @bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'] and m.text)
    def service_commands(m):
        chat_id = m.chat.id
        user_id = m.from_user.id
        txt = m.text.strip()

        if chat_id not in service_data: service_data[chat_id] = {}

        if txt == 'نسبه الحب':
            bot.reply_to(m, f"❤️ نسبة الحب بينكم: {random.randint(1,100)}%")
        elif txt == 'نسبه الغباء' and m.reply_to_message:
            bot.reply_to(m, f"🤡 نسبة الغباء: {random.randint(1,100)}%")
        elif txt == 'نسبه انوثتها' and m.reply_to_message:
            bot.reply_to(m, f"👩 نسبة الانوثة: {random.randint(1,100)}%")
        elif txt == 'نسبه رجولته' and m.reply_to_message:
            bot.reply_to(m, f"👨 نسبة الرجولة: {random.randint(1,100)}%")

        elif txt == 'تحبه' and m.reply_to_message:
            bot.reply_to(m, f"اي احبه موووت 😍" if random.randint(0,1) else "لا مااحبه 😒")

        elif txt.startswith('ارسل') and 'زاجل' in txt:
            try:
                parts = txt.split()
                msg = " ".join(parts[1:-2])
                username = parts[-1].replace('@','')
                bot.send_message(f"@{username}", f"📨 رسالة زاجل من {m.from_user.first_name}:\n{msg}")
                bot.reply_to(m, "✅ تم ارسال الزاجل")
            except: bot.reply_to(m, "الصيغة: ارسل الكلام @اليوزر زاجل")

        elif txt == 'صيح':
            bot.send_message(chat_id, "صييح 😭")
        elif txt.startswith('صيح '):
            username = txt.split()[1]
            bot.reply_to(m, f"تم تزيعج {username} بالخاص 😂")

        elif txt in ['شبيهي','شبيهتي']:
            bot.reply_to(m, f"شبيهك هو: {random.choice(['احمد','محمد','علي','سارة','فاطمة'])}")

        elif txt == 'اهديني':
            bot.reply_to(m, f"اهديك وردة 🌹")
        elif txt == 'اهديه' and m.reply_to_message:
            bot.reply_to(m, f"تم اهداء {m.reply_to_message.from_user.first_name} 🌹")

        elif txt == 'شرايك في افتاري':
            bot.reply_to(m, random.choice(["افتارك فخم 🔥","افتارك عادي 😂"]))
        elif txt == 'افتاره' and m.reply_to_message:
            bot.reply_to(m, "ارسلي صورته خاص واقيمه")
        elif txt == 'البايو' and m.reply_to_message:
            try:
                user = bot.get_chat(m.reply_to_message.from_user.id)
                bot.reply_to(m, f"البايو: {user.bio or 'مافي بايو'}")
            except: bot.reply_to(m, "ماقدرت اجيب البايو")

        elif txt == 'قران':
            bot.reply_to(m, "📖 {وَقُل رَّبِّ زِدْنِي عِلْمًا}")
        elif txt == 'اذكار':
            bot.reply_to(m, "🌙 سبحان الله وبحمده سبحان الله العظيم")

        elif txt in ['شعر','قصائد']:
            bot.reply_to(m, random.choice(["اذا الشعب يوما اراد الحياة...","عيونك بحر"]))
        elif txt == 'اقتباسات':
            bot.reply_to(m, random.choice(["لا تيأس","كن قوياً"]))
        elif txt == 'اطربني':
            bot.reply_to(m, "🎵 جاري تشغيل اغنية...")
        elif txt in ['هيدرات','جداريات','ميمز','كتب','ايدت']:
            bot.reply_to(m, f"📁 تم ارسال {txt}")

        elif txt.startswith('قوقل '):
            query = txt[5:]
            bot.reply_to(m, f"🔍 https://www.google.com/search?q={query}")
        elif txt.startswith('معنى '):
            name = txt[5:]
            bot.reply_to(m, f"معنى {name}: اسم جميل 😊")
        elif txt.startswith('العمر '):
            age = txt[5:]
            bot.reply_to(m, f"عمرك {age} سنة")
        elif txt.startswith('زخرف '):
            name = txt[5:]
            bot.reply_to(m, f"زخرفة: 『{name}』")
        elif txt.startswith('ترجم عربي '):
            bot.reply_to(m, "تمت الترجمة للعربي")
        elif txt.startswith('ترجم انقليزي '):
            bot.reply_to(m, "Translated to English")

        elif txt.startswith('ساوند '):
            bot.reply_to(m, "⏬ جاري تحميل من ساوند...")
        elif txt.startswith('تيك '):
            bot.reply_to(m, "⏬ جاري تحميل من تيك توك...")
        elif txt.startswith('تويتر '):
            bot.reply_to(m, "⏬ جاري تحميل من تويتر...")

        elif txt == 'قيفات':
            bot.reply_to(m, "📂 قيفات: اطفال, رومنسيه, كوكسال, كيبوب, عيال, بنات")
        elif txt == 'افتارات':
            bot.reply_to(m, "📂 افتارات: بنات, عيال, فنانين, تطقيم, كيبوب, انمي")

        elif txt == 'من ضافني':
            bot.reply_to(m, "اللي ضافك هو: المدير")
