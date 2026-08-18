# -*- coding: utf-8 -*-
import telebot, json, os, random
from telebot import types

API_TOKEN = os.environ.get('BOT_TOKEN') # او حط التوكن هنا مباشر "123456:ABC"
ADMIN_ID = 7488375443 # غيره لايديك
BOT_NAME = "𝐓𝐢𝐚"
WELCOME_PHOTO = "https://t.me/eeccvu/2" # لو ما اشتغلت الصورة حط رابط مباشر

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
DATA_FILE = "tia_data.json"

# ===== قاعدة البيانات =====
def load_data():
    global users, admins, PROTECTION, REPLY_TEXT, locks, toggles
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = set(data.get("users", []))
            admins = set(data.get("admins", []))
            PROTECTION = data.get("PROTECTION", True)
            REPLY_TEXT = data.get("REPLY_TEXT", "⊱ اهلا بك في الدعم سيتم الرد عليك")
            locks = {int(k):v for k,v in data.get("locks", {}).items()} # تحويل المفاتيح ل int
            toggles = data.get("toggles", {})
    else:
        users = set()
        admins = set()
        PROTECTION = True
        REPLY_TEXT = "⊱ اهلا بك في الدعم سيتم الرد عليك"
        locks = {}
        toggles = {}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"users": list(users), "admins": list(admins), "PROTECTION": PROTECTION,
                   "REPLY_TEXT": REPLY_TEXT, "locks": locks, "toggles": toggles}, f, ensure_ascii=False)

load_data()

# ===== لوحة المطور =====
def dev_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("⊱ معلومات التنصيب"))
    markup.row(types.KeyboardButton("⊱ اعدادات البوت"), types.KeyboardButton("⊱ اعدادات الاساسي"))
    markup.row(types.KeyboardButton("⊱ اوامر الاذاعة"), types.KeyboardButton("⊱ الاوامر العامة"))
    markup.row(types.KeyboardButton("⊱ الغاء الامر"))
    return markup

def is_dev(user_id):
    return user_id == ADMIN_ID or user_id in admins

def is_admin(message):
    if message.chat.type == 'private': return False
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def escape_md(text):
    # تهريب الرموز عشان Markdown ما يضرب
    return text.replace('_','\_').replace('*','\*').replace('`','\`').replace('[','\[')

# ===== اوامر الخاص =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = escape_md(message.from_user.first_name or "مستخدم")
    if user_id not in users:
        users.add(user_id); save_data()

    welcome_text = f"""⊱ مرحبا {name} في {BOT_NAME} 𓆩♡𓆪
⊱ {REPLY_TEXT}
⊱ ارسل رسالتك الان"""

    try:
        if is_dev(user_id):
            bot.send_photo(user_id, WELCOME_PHOTO, caption=welcome_text, reply_markup=dev_keyboard())
        else:
            bot.send_photo(user_id, WELCOME_PHOTO, caption=welcome_text)
    except:
        bot.send_message(user_id, welcome_text, reply_markup=dev_keyboard() if is_dev(user_id) else None)

@bot.message_handler(func=lambda m: is_dev(m.from_user.id) and m.chat.type == 'private')
def dev_panel(message):
    global PROTECTION, REPLY_TEXT
    text = message.text

    if text == "⊱ معلومات التنصيب":
        info = f"""⊱ معلومات التنصيب
⊱ اسم البوت: {BOT_NAME}
⊱ عدد المستخدمين: {len(users)}
⊱ عدد المطورين: {len(admins)+1}
⊱ حالة الحماية: {'مفعلة ✅' if PROTECTION else 'معطلة ❌'}"""
        bot.send_message(ADMIN_ID, info, reply_markup=dev_keyboard())

    elif text == "⊱ اعدادات البوت":
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("⊱ 🔒 تفعيل الحماية", "⊱ 🔓 تعطيل الحماية")
        kb.row("⊱ اضف رد", "⊱ علم مطورين")
        kb.row("⊱ الغاء الامر")
        bot.send_message(ADMIN_ID, "⊱ اعدادات البوت:", reply_markup=kb)

    elif text == "⊱ اعدادات الاساسي":
        admins_list = "\n".join([f"⊱ `{i}`" for i in admins]) if admins else "⊱ لا يوجد"
        msg = f"⊱ اعدادات الاساسي\n⊱ المطور الاساسي: `{ADMIN_ID}`\n⊱ المطورين:\n{admins_list}"
        bot.send_message(ADMIN_ID, msg, reply_markup=dev_keyboard())

    elif text == "⊱ اوامر الاذاعة":
        msg = bot.send_message(ADMIN_ID, "⊱ ارسل نص الاذاعة الان")
        bot.register_next_step_handler(msg, do_broadcast)

    elif text == "⊱ الاوامر العامة":
        bot.send_message(ADMIN_ID, f"⊱ الاوامر العامة\n⊱ عدد المشتركين: {len(users)}", reply_markup=dev_keyboard())

    elif text == "⊱ الغاء الامر":
        bot.send_message(ADMIN_ID, "⊱ تم الغاء الامر", reply_markup=dev_keyboard())

    elif text == "⊱ 🔒 تفعيل الحماية":
        PROTECTION=True; save_data(); bot.send_message(ADMIN_ID, "⊱ ✅ تم تفعيل الحماية", reply_markup=dev_keyboard())
    elif text == "⊱ 🔓 تعطيل الحماية":
        PROTECTION=False; save_data(); bot.send_message(ADMIN_ID, "⊱ ❌ تم تعطيل الحماية", reply_markup=dev_keyboard())
    elif text == "⊱ اضف رد":
        msg = bot.send_message(ADMIN_ID, "⊱ ارسل رسالة الترحيب الجديدة")
        bot.register_next_step_handler(msg, set_reply)
    elif text == "⊱ علم مطورين":
        msg = bot.send_message(ADMIN_ID, "⊱ ارسل ايدي الشخص اللي تريد تجعله مطور")
        bot.register_next_step_handler(msg, add_admin)

def set_reply(m):
    global REPLY_TEXT
    REPLY_TEXT = m.text
    save_data()
    bot.send_message(ADMIN_ID, f"⊱ ✅ تم حفظ الرد:\n⊱ {REPLY_TEXT}", reply_markup=dev_keyboard())

def add_admin(m):
    try:
        new_admin = int(m.text)
        admins.add(new_admin); save_data()
        bot.send_message(ADMIN_ID, f"⊱ ✅ تم تعيين `{new_admin}` كمطور", reply_markup=dev_keyboard())
        bot.send_message(new_admin, f"⊱ تم تعيينك كمطور في {BOT_NAME}")
    except:
        bot.send_message(ADMIN_ID, "⊱ ❌ ايدي خطأ", reply_markup=dev_keyboard())

def do_broadcast(m):
    count=0
    for u in users:
        try:
            bot.send_photo(u, WELCOME_PHOTO, caption=f"⊱ 📢 {BOT_NAME}\n⊱ {m.text}")
            count+=1
        except: pass
    bot.send_message(ADMIN_ID, f"⊱ ✅ تم الارسال لـ {count} شخص", reply_markup=dev_keyboard())

# ===== اوامر الكروبات M1 الى M11 =====
@bot.message_handler(content_types=['text'])
def group_commands(message):
    chat_id = message.chat.id
    text = message.text.strip()
    user_id = message.from_user.id

    if message.chat.type not in ['group', 'supergroup', 'channel']: return
    if chat_id not in locks: locks[chat_id] = []

    # فحص الاقفال قبل كل شي
    if "link" in locks.get(chat_id, []) and "http" in text.lower():
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        return

    # M1 ادارة
    if text == "رفع ادمن" and is_admin(message):
        bot.reply_to(message, "✅ تم رفع العضو ادمن - ملاحظة: لازم ترفعه يدوي من صلاحيات الكروب")
    elif text == "تنزيل ادمن" and is_admin(message):
        bot.reply_to(message, "✅ تم تنزيل العضو من الادمنية - ملاحظة: لازم تنزله يدوي")
    elif text == "تثبيت" and is_admin(message):
        if message.reply_to_message:
            try:
                bot.pin_chat_message(chat_id, message.reply_to_message.message_id)
                bot.reply_to(message, "📌 تم تثبيت الرسالة")
            except:
                bot.reply_to(message, "❌ ما عندي صلاحية التثبيت")
        else:
            bot.reply_to(message, "❌ رد على الرسالة اللي تريد تثبتها")

    # M2 حماية
    elif text == "قفل الروابط" and is_admin(message):
        if "link" not in locks[chat_id]: locks[chat_id].append("link"); save_data()
        bot.reply_to(message, "🔒 تم قفل الروابط")
    elif text == "فتح الروابط" and is_admin(message):
        if "link" in locks[chat_id]: locks[chat_id].remove("link"); save_data()
        bot.reply_to(message, "🔓 تم فتح الروابط")

    # M4 اعضاء
    elif text == "ايدي":
        name = escape_md(message.from_user.first_name)
        bot.reply_to(message, f"🆔 ايديك : `{user_id}`\n👤 اسمك : {name}")

    # M5
    elif text == "رفع مميز" and is_admin(message):
        bot.reply_to(message, "⭐ تم رفع العضو مميز")

    # M6 تحشيش
    elif text in ["تاج","ملك","ملكه","اثول","جلب","مطي","بوسه","هديه"]:
        replies = {"تاج":"🤴 هذا تاج الملك 👑","ملك":"🧝‍♂️ انت الملك اليوم","ملكه":"🧝‍♀️ انتي الملكة",
                   "اثول":"🤦‍♀️ يمعود اثول","جلب":"👩‍🎤 هوووه جلب","مطي":"🧑‍🦯 مطي رسمي",
                   "بوسه":"👩‍❤️‍💋‍👨 موواح 😘","هديه":"🎁 هاي الك هديه"}
        bot.reply_to(message, replies[text])
    elif text == "نسبه الحب":
        bot.reply_to(message, f"✨ نسبة الحب بينكم : {random.randint(70,100)}% ❤️")

    # M8 تسلية
    elif text == "غنيلي":
        bot.reply_to(message, "🎵 اختار اغنيه تريدها")
    elif text == "زواج":
        bot.reply_to(message, "💍 تم زواجكم مبارك")

    # M9 بنك
    elif text == "انشاء حساب":
        bot.reply_to(message, "💳 تم انشاء حساب بنكي الك")
    elif text == "راتب":
        bot.reply_to(message, "💸 تم استلام الراتب : 500$")

    # M10 قفل
    elif text.startswith("قفل ") and is_admin(message):
        lock_item = text.replace("قفل ","")
        if lock_item not in locks[chat_id]: locks[chat_id].append(lock_item); save_data()
        bot.reply_to(message, f"🔒 تم قفل {lock_item}")
    elif text.startswith("فتح ") and is_admin(message):
        lock_item = text.replace("فتح ","")
        if lock_item in locks[chat_id]: locks[chat_id].remove(lock_item); save_data()
        bot.reply_to(message, f"🔓 تم فتح {lock_item}")

    # M11 تفعيل
    elif text.startswith("تفعيل ") and is_admin(message):
        toggle = text.replace("تفعيل ","")
        toggles[f"{chat_id}_{toggle}"] = True; save_data()
        bot.reply_to(message, f"✅ تم تفعيل {toggle}")
    elif text.startswith("تعطيل ") and is_admin(message):
        toggle = text.replace("تعطيل ","")
        toggles[f"{chat_id}_{toggle}"] = False; save_data()
        bot.reply_to(message, f"❌ تم تعطيل {toggle}")

# ===== رسائل الاعضاء للخاص =====
@bot.message_handler(func=lambda m: not is_dev(m.from_user.id) and m.chat.type == 'private')
def user_msg
