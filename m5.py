from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json, os, sys
import menu # 👈 ضفنا هذا عشان زر الرجوع

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

def dev_keyboard(): # هذا حق الخاص
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

# ===== جديد: قائمة القروب ازرار =====
def show_dev_menu(bot, chat_id):
    channel = settings.get('channel', 'لم يتم التعيين')
    text = f"""🔧 **اوامر المطور Dev**
- قناة البوت: @{channel}
━━━━━━━━━━━━
اختر الامر من الازرار"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📢 اذاعة", callback_data="dev_broadcast"),
        InlineKeyboardButton("📊 قائمه العام", callback_data="dev_gbanlist"),
        InlineKeyboardButton("🧹 مسح العام", callback_data="dev_cleangban"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    )
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

def show_dev_keyboard(bot, chat_id): # هذا حق الخاص
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
    if not photo: photo = "https://i.imgur.com/8Km9tLL.jpg"
    bot.send_photo(chat_id, photo, caption=welcome)

# ===== غيرنا الاسم من register_m5_handlers الى register_handlers =====
def register_handlers(bot):

    @bot.message_handler(commands=['start'])
    def start_pm(m):
        if m.chat.type == 'private':
            send_welcome_pm(bot, m.chat.id, m.from_user)
            if is_dev(m.from_user.id):
                bot.send_message(m.chat.id, "مرحبا عزي المطور", reply_markup=dev_keyboard())

    @bot.message_handler(func=lambda m: m.chat.type == 'private' and is_dev(m.from_user.id))
    def dev_keyboard_commands(m):
        # كل الكود حقك هنا بدون تغيير
        txt = m.text.strip()
        if txt == "معاينة الترحيب": send_welcome_pm(bot, m.chat.id, m.from_user)
        elif txt == "ترحيب الخاص نص":
            msg = bot.send_message(m.chat.id, "ارسل نص ترحيب الخاص\nتقدر تستخدم: {name} {id} {username}")
            bot.register_next_step_handler(msg, set_welcome_pm)
        elif txt == "اذاعة":
            msg = bot.send_message(m.chat.id, "ارسل الرسالة للاذاعة")
            bot.register_next_step_handler(msg, broadcast_msg)
        elif txt == "رجوع للقائمة":
            menu.show_menu(bot, m.chat.id) # عدلتها
        #... باقي الاوامر حقك كلها هنا
        # لخصتها عشان الطول بس خلي كل اللي عندك

    # ===== جديد: اوامر ازرار القروب =====
    @bot.callback_query_handler(func=lambda call: call.data.startswith("dev_"))
    def dev_callbacks(call):
        bot.answer_callback_query(call.id)
        if call.data == "dev_broadcast":
            bot.send_message(call.message.chat.id, "ارسل الاذاعة هنا")
        elif call.data == "dev_gbanlist":
            msg = f"🚫 محظورين عام: {len(gban_list)}\n🔇 مكتومين عام: {len(gmute_list)}"
            bot.send_message(call.message.chat.id, msg)
        elif call.data == "dev_cleangban":
            gban_list.clear(); gmute_list.clear(); save_dev_data()
            bot.send_message(call.message.chat.id, "✅ تم مسح المحظورين والمكتومين عام")

    # كل دوال set_welcome_pm و broadcast_msg... خليها زي ما هي
    # الصقها من الكود اللي ارسلته انت
    def set_welcome_pm(m):
        settings['welcome_pm'] = m.text
        save_dev_data()
        send_welcome_pm(bot, m.chat.id, m.from_user)
        bot.send_message(m.chat.id, "✅ تم حفظ ترحيب الخاص", reply_markup=dev_keyboard())
    def broadcast_msg(m):
        groups = broadcast_status.get('groups', [])
        count = 0
        for chat_id in groups:
            try: bot.send_message(chat_id, f"📢 اذاعة:\n\n{m.text}"); count += 1
            except: pass
        bot.send_message(m.chat.id, f"✅ تمت الاذاعة لـ {count} مجموعة", reply_markup=dev_keyboard())
    #... الصق باقي دوالك هنا
