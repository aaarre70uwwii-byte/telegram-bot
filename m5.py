from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json, os, sys

FILE_DEV = 'dev.json'
FILE_CONTACT = 'contact.json'
FILE_GBAN = 'gban.json'
FILE_GMUTE = 'gmute.json'
FILE_GLOBAL_RANKS = 'global_ranks.json'
FILE_GLOBAL_REPLIES = 'global_replies.json'
FILE_MULTI_REPLIES = 'multi_replies.json'
FILE_CLISHA = 'clisha.json'
FILE_BROADCAST = 'broadcast.json'
FILE_SETTINGS = 'settings.json'

DEVS = [7488375443] # المطور الاساسي

def load_dev_data():
    global devs, contact_replies, gban_list, gmute_list, global_ranks, global_replies, multi_replies, clisha, broadcast_status, settings
    for f in [FILE_DEV, FILE_CONTACT, FILE_GBAN, FILE_GMUTE, FILE_GLOBAL_RANKS, FILE_GLOBAL_REPLIES, FILE_MULTI_REPLIES, FILE_CLISHA, FILE_BROADCAST, FILE_SETTINGS]:
        if not os.path.exists(f):
            if f == FILE_DEV: json.dump([], open(f, 'w', encoding='utf-8'))
            else: json.dump({}, open(f, 'w', encoding='utf-8'))

    devs = json.load(open(FILE_DEV, 'r', encoding='utf-8'))
    contact_replies = json.load(open(FILE_CONTACT, 'r', encoding='utf-8'))
    gban_list = json.load(open(FILE_GBAN, 'r', encoding='utf-8'))
    gmute_list = json.load(open(FILE_GMUTE, 'r', encoding='utf-8'))
    global_ranks = json.load(open(FILE_GLOBAL_RANKS, 'r', encoding='utf-8'))
    global_replies = json.load(open(FILE_GLOBAL_REPLIES, 'r', encoding='utf-8'))
    multi_replies = json.load(open(FILE_MULTI_REPLIES, 'r', encoding='utf-8'))
    clisha = json.load(open(FILE_CLISHA, 'r', encoding='utf-8'))
    broadcast_status = json.load(open(FILE_BROADCAST, 'r', encoding='utf-8'))
    settings = json.load(open(FILE_SETTINGS, 'r', encoding='utf-8'))

def save_dev_data():
    json.dump(devs, open(FILE_DEV, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(contact_replies, open(FILE_CONTACT, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(gban_list, open(FILE_GBAN, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(gmute_list, open(FILE_GMUTE, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(global_ranks, open(FILE_GLOBAL_RANKS, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(global_replies, open(FILE_GLOBAL_REPLIES, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(multi_replies, open(FILE_MULTI_REPLIES, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(clisha, open(FILE_CLISHA, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(broadcast_status, open(FILE_BROADCAST, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(settings, open(FILE_SETTINGS, 'w', encoding='utf-8'), ensure_ascii=False)

load_dev_data()

def dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("ترحيب الخاص نص"), KeyboardButton("ترحيب الخاص صورة"),
        KeyboardButton("معاينة الترحيب"), KeyboardButton("مسح صورة ترحيب الخاص"),
        KeyboardButton("اضف رد تواصل"), KeyboardButton("ردود التواصل"),
        KeyboardButton("اضف رد عام"), KeyboardButton("الردود العامه"),
        KeyboardButton("اضف رد متعدد عام"), KeyboardButton("الردود المتعدده العامه"),
        KeyboardButton("ضع ترحيب"), KeyboardButton("ضع صورة الترحيب"),
        KeyboardButton("مسح صورة الترحيب"), KeyboardButton("قائمه العام"),
        KeyboardButton("مسح المحظورين عام"), KeyboardButton("اذاعة"),
        KeyboardButton("مغادرة"), KeyboardButton("تغير قناة البوت"),
        KeyboardButton("نقل الملكية"), KeyboardButton("تحديث الملفات"),
        KeyboardButton("اعاده تشغيل"), KeyboardButton("رجوع للقائمة")
    )
    return markup

def show_dev_menu(bot, chat_id):
    channel = settings.get('channel', 'لم يتم التعيين')
    welcome = settings.get('welcome', 'لم يتم التعيين')
    welcome_pm = settings.get('welcome_pm', 'اهلا بك في البوت')
    photo = "✅ موجودة" if settings.get('welcome_pm_photo') else "❌ غير موجودة"
    text = f"""- اهلا بك عزي Dev
- قناة البوت: @{channel}
- ترحيب القروبات: {welcome}
- ترحيب الخاص: {welcome_pm}
- صورة ترحيب الخاص: {photo}
━━━━━━━━━━━━"""
    bot.send_message(chat_id, text, reply_markup=dev_keyboard())

def is_dev(user_id):
    return user_id in DEVS or str(user_id) in devs

def send_welcome_pm(bot, chat_id, user):
    welcome = settings.get('welcome_pm', 'اهلا بك {name} في البوت')
    welcome = welcome.replace('{name}', user.first_name).replace('{id}', str(user.id)).replace('{username}', f"@{user.username}" if user.username else "")

    photo = settings.get('welcome_pm_photo')
    if not photo:
        photo = "https://i.imgur.com/8Km9tLL.jpg" # غير الرابط بصورتك

    bot.send_photo(chat_id, photo, caption=welcome)

def register_m5_handlers(bot):

    @bot.message_handler(commands=['start'])
    def start_pm(m):
        if m.chat.type == 'private':
            send_welcome_pm(bot, m.chat.id, m.from_user)
            if is_dev(m.from_user.id):
                bot.send_message(m.chat.id, "مرحبا عزي المطور", reply_markup=dev_keyboard())

    @bot.message_handler(func=lambda m: m.chat.type == 'private' and is_dev(m.from_user.id))
    def dev_keyboard_commands(m):
        txt = m.text.strip()

        if txt == "معاينة الترحيب":
            send_welcome_pm(bot, m.chat.id, m.from_user)

        elif txt == "ترحيب الخاص نص":
            msg = bot.send_message(m.chat.id, "ارسل نص ترحيب الخاص\nتقدر تستخدم: {name} {id} {username}")
            bot.register_next_step_handler(msg, set_welcome_pm)

        elif txt == "ترحيب الخاص صورة":
            msg = bot.send_message(m.chat.id, "ارسل الصورة لترحيب الخاص")
            bot.register_next_step_handler(msg, set_welcome_pm_photo)

        elif txt == "مسح صورة ترحيب الخاص":
            settings['welcome_pm_photo'] = ""
            save_dev_data()
            bot.send_message(m.chat.id, "✅ تم الرجوع للصورة الافتراضية", reply_markup=dev_keyboard())

        elif txt == "ضع ترحيب":
            msg = bot.send_message(m.chat.id, "ارسل نص ترحيب القروبات")
            bot.register_next_step_handler(msg, set_welcome)

        elif txt == "ضع صورة الترحيب":
            msg = bot.send_message(m.chat.id, "ارسل الصورة لترحيب القروبات")
            bot.register_next_step_handler(msg, set_welcome_photo)

        elif txt == "مسح صورة الترحيب":
            settings['welcome_photo'] = ""
            save_dev_data()
            bot.send_message(m.chat.id, "✅ تم مسح صورة ترحيب القروبات", reply_markup=dev_keyboard())

        elif txt == "اضف رد تواصل":
            msg = bot.send_message(m.chat.id, "ارسل الكلمة والرد مفصولين بـ |")
            bot.register_next_step_handler(msg, add_contact_reply)

        elif txt == "ردود التواصل":
            msg = "📋 ردود التواصل:\n" + "\n".join([f"- {k} : {v}" for k,v in contact_replies.items()]) if contact_replies else "مافي ردود"
            bot.send_message(m.chat.id, msg, reply_markup=dev_keyboard())

        elif txt == "اضف رد عام":
            msg = bot.send_message(m.chat.id, "ارسل الكلمة والرد مفصولين بـ |")
            bot.register_next_step_handler(msg, add_global_reply)

        elif txt == "الردود العامه":
            msg = "📋 الردود العامه:\n" + "\n".join([f"- {k}" for k in global_replies.keys()]) if global_replies else "مافي ردود"
            bot.send_message(m.chat.id, msg, reply_markup=dev_keyboard())

        elif txt == "اضف رد متعدد عام":
            msg = bot.send_message(m.chat.id, "ارسل الكلمة والردود مفصولين بـ | وبين الردود,")
            bot.register_next_step_handler(msg, add_multi_reply)

        elif txt == "الردود المتعدده العامه":
            msg = "📋 الردود المتعدده:\n" + "\n".join([f"- {k}" for k in multi_replies.keys()]) if multi_replies else "مافي ردود"
            bot.send_message(m.chat.id, msg, reply_markup=dev_keyboard())

        elif txt == "قائمه العام":
            msg = f"🚫 محظورين عام: {len(gban_list)}\n🔇 مكتومين عام: {len(gmute_list)}"
            bot.send_message(m.chat.id, msg, reply_markup=dev_keyboard())

        elif txt == "مسح المحظورين عام":
            gban_list.clear(); gmute_list.clear(); save_dev_data()
            bot.send_message(m.chat.id, "✅ تم مسح المحظورين والمكتومين عام", reply_markup=dev_keyboard())

        elif txt == "اذاعة":
            msg = bot.send_message(m.chat.id, "ارسل الرسالة للاذاعة")
            bot.register_next_step_handler(msg, broadcast_msg)

        elif txt == "مغادرة":
            msg = bot.send_message(m.chat.id, "ارسل ايدي المجموعة")
            bot.register_next_step_handler(msg, leave_chat)

        elif txt == "تغير قناة البوت":
            msg = bot.send_message(m.chat.id, "ارسل يوزر القناة بدون @")
            bot.register_next_step_handler(msg, set_channel)

        elif txt == "نقل الملكية":
            msg = bot.send_message(m.chat.id, "ارسل يوزر المطور الجديد")
            bot.register_next_step_handler(msg, transfer_owner)

        elif txt == "تحديث الملفات":
            bot.send_message(m.chat.id, "🔄 جاري تحديث الملفات...")
            os.system('git pull')
            bot.send_message(m.chat.id, "✅ تم تحديث الملفات", reply_markup=dev_keyboard())

        elif txt == "اعاده تشغيل":
            bot.send_message(m.chat.id, "♻️ جاري اعادة التشغيل...")
            os.execv(sys.executable, ['python'] + sys.argv)

        elif txt == "رجوع للقائمة":
            from menu import show_main_menu
            show_main_menu(bot, m.chat.id)

    @bot.message_handler(func=lambda m: is_dev(m.from_user.id) and m.text)
    def dev_text_commands(m):
        txt = m.text.strip()
        if txt.startswith('رفع Dev') and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            if target not in devs: devs.append(target); save_dev_data()
            bot.reply_to(m, "✅ تم رفع مطور ثانوي", reply_markup=dev_keyboard())
        elif txt.startswith('تنزيل Dev') and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            if target in devs: devs.remove(target); save_dev_data()
            bot.reply_to(m, "✅ تم تنزيل مطور ثانوي", reply_markup=dev_keyboard())
        elif txt == 'حظر عام' and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            gban_list[target] = True; save_dev_data()
            bot.reply_to(m, "🚫 تم حظر العضو عام", reply_markup=dev_keyboard())
        elif txt == 'كتم عام' and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            gmute_list[target] = True; save_dev_data()
            bot.reply_to(m, "🔇 تم كتم العضو عام", reply_markup=dev_keyboard())
        elif txt == 'الغاء كتم عام' and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            if target in gmute_list: gmute_list.pop(target); save_dev_data()
            bot.reply_to(m, "✅ تم الغاء الكتم", reply_markup=dev_keyboard())

    def set_welcome_pm(m):
        settings['welcome_pm'] = m.text
        save_dev_data()
        send_welcome_pm(bot, m.chat.id, m.from_user)
        bot.send_message(m.chat.id, "✅ تم حفظ ترحيب الخاص", reply_markup=dev_keyboard())

    def set_welcome_pm_photo(m):
        if m.photo:
            file_id = m.photo[-1].file_id
            settings['welcome_pm_photo'] = file_id
            save_dev_data()
            send_welcome_pm(bot, m.chat.id, m.from_user)
            bot.send_message(m.chat.id, "✅ تم حفظ صورة ترحيب الخاص", reply_markup=dev_keyboard())
        else:
            bot.send_message(m.chat.id, "❌ ارسل صورة فقط", reply_markup=dev_keyboard())

    def set_welcome(m):
        settings['welcome'] = m.text
        save_dev_data()
        bot.send_message(m.chat.id, "✅ تم حفظ ترحيب القروبات", reply_markup=dev_keyboard())

    def set_welcome_photo(m):
        if m.photo:
            file_id = m.photo[-1].file_id
            settings['welcome_photo'] = file_id
            save_dev_data()
            bot.send_message(m.chat.id, "✅ تم حفظ صورة ترحيب القروبات", reply_markup=dev_keyboard())
        else:
            bot.send_message(m.chat.id, "❌ ارسل صورة فقط", reply_markup=dev_keyboard())

    def add_contact_reply(m):
        try: k,v = m.text.split('|',1)
        except: return bot.send_message(m.chat.id, "الصيغة غلط", reply_markup=dev_keyboard())
        contact_replies[k.strip()] = v.strip(); save_dev_data()
        bot.send_message(m.chat.id, "✅ تم اضافة رد التواصل", reply_markup=dev_keyboard())

    def add_global_reply(m):
        try: k,v = m.text.split('|',1)
        except: return bot.send_message(m.chat.id, "الصيغة غلط", reply_markup=dev_keyboard())
        global_replies[k.strip()] = v.strip(); save_dev_data()
        bot.send_message(m.chat.id, "✅ تم اضافة رد عام", reply_markup=dev_keyboard())

    def add_multi_reply(m):
        try: k,v = m.text.split('|',1)
        except: return bot.send_message(m.chat.id, "الصيغة غلط", reply_markup=dev_keyboard())
        multi_replies[k.strip()] = [x.strip() for x in v.split(',')]
        save_dev_data(); bot.send_message(m.chat.id, "✅ تم اضافة رد متعدد", reply_markup=dev_keyboard())

    def set_channel(m):
        username = m.text.replace('@','').strip()
        settings['channel'] = username
        save_dev_data()
        bot.send_message(m.chat.id, f"✅ تم تعيين قناة البوت: @{username}", reply_markup=dev_keyboard())

    def transfer_owner(m):
        username = m.text.replace('@','').strip()
        try:
            user = bot.get_chat(username)
            new_id = user.id
            global DEVS
            DEVS = [new_id]
            json.dump(DEVS, open(FILE_DEV, 'w', encoding='utf-8'))
            bot.send_message(m.chat.id, f"✅ تم نقل الملكية للمطور: @{username}\nالايدي: {new_id}", reply_markup=dev_keyboard())
        except:
            bot.send_message(m.chat.id, "❌ اليوزر غلط", reply_markup=dev_keyboard())

    def broadcast_msg(m):
        groups = broadcast_status.get('groups', [])
        count = 0
        for chat_id in groups:
            try:
                bot.send_message(chat_id, f"📢 اذاعة:\n\n{m.text}")
                count += 1
            except: pass
        bot.send_message(m.chat.id, f"✅ تمت الاذاعة لـ {count} مجموعة", reply_markup=dev_keyboard())

    def leave_chat(m):
        try:
            bot.leave_chat(int(m.text))
            bot.send_message(m.chat.id, f"✅ تمت المغادرة من: {m.text}", reply_markup=dev_keyboard())
        except:
            bot.send_message(m.chat.id, "❌ ايدي غلط", reply_markup=dev_keyboard())
