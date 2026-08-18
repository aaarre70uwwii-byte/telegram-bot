# -*- coding: utf-8 -*-
import telebot, json, os, random
from telebot import types

API_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7488375443
BOT_NAME = "𝐓𝐢𝐚"
WELCOME_PHOTO = "https://t.me/eeccvu/2"
DEV_PHOTO = "https://t.me/eeccvu/2"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
DATA_FILE = "tia_data.json"

def load_data():
    global users, admins, devs, PROTECTION, REPLY_TEXT, locks, toggles, active_groups
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = set(data.get("users", []))
            admins = set(data.get("admins", []))
            devs = set(data.get("devs", []))
            PROTECTION = data.get("PROTECTION", True)
            REPLY_TEXT = data.get("REPLY_TEXT", "⊱ اهلا بك في الدعم سيتم الرد عليك")
            locks = {int(k):v for k,v in data.get("locks", {}).items()}
            toggles = data.get("toggles", {})
            active_groups = set(data.get("active_groups", []))
    else:
        users = set(); admins = set(); devs = set(); PROTECTION = True
        REPLY_TEXT = "⊱ اهلا بك في الدعم سيتم الرد عليك"
        locks = {}; toggles = {}; active_groups = set()

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"users": list(users), "admins": list(admins), "devs": list(devs),
                   "PROTECTION": PROTECTION, "REPLY_TEXT": REPLY_TEXT,
                   "locks": locks, "toggles": toggles, "active_groups": list(active_groups)}, f, ensure_ascii=False)

load_data()

def dev_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("⊱ معلومات التنصيب"))
    markup.row(types.KeyboardButton("⊱ اعدادات البوت"), types.KeyboardButton("⊱ اعدادات الاساسي"))
    markup.row(types.KeyboardButton("⊱ اوامر الاذاعة"), types.KeyboardButton("⊱ الاوامر العامة"))
    markup.row(types.KeyboardButton("⊱ الغاء الامر"))
    return markup

def is_dev(user_id): return user_id == ADMIN_ID or user_id in devs or user_id in admins
def is_admin(message):
    if message.chat.type == 'private': return False
    try: return bot.get_chat_member(message.chat.id, message.from_user.id).status in ['administrator', 'creator']
    except: return False

def escape_md(text):
    if not text: return ""
    return text.replace('_','\\_').replace('*','\\*').replace('`','\\`').replace('[','\\[')

# ===== اوامر الخاص + لوحة المطور =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = escape_md(message.from_user.first_name)
    if user_id not in users: users.add(user_id); save_data()

    welcome_text = f"⊱ مرحبا {name} في {BOT_NAME}\n⊱ {REPLY_TEXT}\n⊱ ارسل رسالتك الان"
    
    if is_dev(user_id):
        bot.send_photo(user_id, WELCOME_PHOTO, caption=welcome_text, reply_markup=dev_keyboard())
    else:
        bot.send_photo(user_id, WELCOME_PHOTO, caption=welcome_text)

@bot.message_handler(func=lambda m: is_dev(m.from_user.id) and m.chat.type == 'private')
def dev_panel(message):
    global PROTECTION, REPLY_TEXT
    text = message.text

    if text == "⊱ معلومات التنصيب":
        info = f"⊱ اسم البوت: {BOT_NAME}\n⊱ عدد المستخدمين: {len(users)}\n⊱ عدد المطورين: {len(admins)+len(devs)+1}\n⊱ عدد الكروبات: {len(active_groups)}\n⊱ حالة الحماية: {'مفعلة ✅' if PROTECTION else 'معطلة ❌'}"
        bot.send_message(ADMIN_ID, info, reply_markup=dev_keyboard())

    elif text == "⊱ اعدادات البوت":
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("⊱ 🔒 تفعيل الحماية", "⊱ 🔓 تعطيل الحماية")
        kb.row("⊱ اضف رد", "⊱ علم مطورين")
        kb.row("⊱ الغاء الامر")
        bot.send_message(ADMIN_ID, "⊱ اعدادات البوت:", reply_markup=kb)

    elif text == "⊱ اعدادات الاساسي":
        admins_list = "\n".join([f"⊱ `{i}`" for i in admins]) if admins else "⊱ لا يوجد"
        devs_list = "\n".join([f"⊱ `{i}`" for i in devs]) if devs else "⊱ لا يوجد"
        msg = f"⊱ المطور الاساسي: `{ADMIN_ID}`\n⊱ المطورين:\n{admins_list}\n⊱ المطورين الثانويين:\n{devs_list}"
        bot.send_message(ADMIN_ID, msg, reply_markup=dev_keyboard())

    elif text == "⊱ اوامر الاذاعة":
        msg = bot.send_message(ADMIN_ID, "⊱ ارسل نص الاذاعة")
        bot.register_next_step_handler(msg, do_broadcast)
    elif text == "⊱ الاوامر العامة":
        bot.send_message(ADMIN_ID, f"⊱ عدد المشتركين: {len(users)}\n⊱ عدد الكروبات المفعلة: {len(active_groups)}", reply_markup=dev_keyboard())
    elif text == "⊱ الغاء الامر":
        bot.send_message(ADMIN_ID, "⊱ تم الالغاء", reply_markup=dev_keyboard())
    elif text == "⊱ 🔒 تفعيل الحماية":
        PROTECTION=True; save_data(); bot.send_message(ADMIN_ID, "⊱ ✅ تم التفعيل", reply_markup=dev_keyboard())
    elif text == "⊱ 🔓 تعطيل الحماية":
        PROTECTION=False; save_data(); bot.send_message(ADMIN_ID, "⊱ ❌ تم التعطيل", reply_markup=dev_keyboard())
    elif text == "⊱ اضف رد":
        msg = bot.send_message(ADMIN_ID, "⊱ ارسل الرد الجديد")
        bot.register_next_step_handler(msg, set_reply)
    elif text == "⊱ علم مطورين":
        msg = bot.send_message(ADMIN_ID, "⊱ ارسل ايدي المطور")
        bot.register_next_step_handler(msg, add_admin)

def set_reply(m): 
    global REPLY_TEXT; REPLY_TEXT = m.text; save_data()
    bot.send_message(ADMIN_ID, f"⊱ ✅ تم الحفظ:\n⊱ {REPLY_TEXT}", reply_markup=dev_keyboard())

def add_admin(m):
    try: devs.add(int(m.text)); save_data(); bot.send_message(ADMIN_ID, f"⊱ ✅ تم تعيين `{m.text}`", reply_markup=dev_keyboard())
    except: bot.send_message(ADMIN_ID, "⊱ ❌ ايدي خطأ", reply_markup=dev_keyboard())

def do_broadcast(m):
    count=0
    for u in users:
        try: bot.send_photo(u, WELCOME_PHOTO, caption=f"⊱ 📢 {BOT_NAME}\n⊱ {m.text}"); count+=1
        except: pass
    bot.send_message(ADMIN_ID, f"⊱ ✅ تم الارسال لـ {count}", reply_markup=dev_keyboard())

# ===== اوامر الكروبات M1-M11 كاملة =====
@bot.message_handler(content_types=['text'])
def group_commands(message):
    chat_id = message.chat.id
    text = message.text.strip()
    user_id = message.from_user.id
    name = escape_md(message.from_user.first_name)

    if message.chat.type not in ['group', 'supergroup']: return
    if chat_id not in locks: locks[chat_id] = []

    if text == "تفعيل البوت" and is_admin(message):
        active_groups.add(chat_id); save_data()
        bot.reply_to(message, "✅ تم تفعيل المجموعة بنجاح\n⊱ الان يمكن استخدام اوامر البوت"); return
    elif text == "تعطيل البوت" and is_admin(message):
        if chat_id in active_groups: active_groups.remove(chat_id); save_data()
        bot.reply_to(message, "❌ تم تعطيل المجموعة"); return

    if chat_id not in active_groups: return

    if "link" in locks.get(chat_id, []) and "http" in text.lower():
        try: bot.delete_message(chat_id, message.message_id)
        except: pass; return

    if text in ["المطور", "مطور البوت"]:
        caption = f"--━━━━━━━━━━━━━━━\n⚡ 𝐁𝐎𝐓 {BOT_NAME} ⚡\n🤖 المطور الرسمي 🤖\n--━━━━━━━━━━━━━━━\n👑 الاسم : 𝐀𝐃𝐌𝐈𝐍\n🆔 الايدي : `{ADMIN_ID}`\n🔗 اليوزر : @rrrrxe\n📢 القناة : https://t.me/eeccvu\n--━━━━━━━━━━━━━━━"
        try: bot.send_photo(chat_id, DEV_PHOTO, caption=caption)
        except: bot.reply_to(message, caption); return

    # M1
    if text == "رفع ادمن" and is_admin(message): bot.reply_to(message, "✅ تم رفع ادمن")
    elif text == "تنزيل ادمن" and is_admin(message): bot.reply_to(message, "✅ تم تنزيل ادمن")
    elif text == "رفع مشرف" and is_admin(message): bot.reply_to(message, "✅ تم رفع مشرف")
    elif text == "تنزيل مشرف" and is_admin(message): bot.reply_to(message, "✅ تم تنزيل مشرف")
    elif text == "تثبيت" and is_admin(message):
        if message.reply_to_message: 
            try: bot.pin_chat_message(chat_id, message.reply_to_message.message_id); bot.reply_to(message, "📌 تم التثبيت")
            except: bot.reply_to(message, "❌ ما عندي صلاحية التثبيت")
        else: bot.reply_to(message, "❌ رد على الرسالة")
    elif text == "الغاء التثبيت" and is_admin(message): 
        try: bot.unpin_chat_message(chat_id); bot.reply_to(message, "📍 تم الغاء التثبيت")
        except: bot.reply_to(message, "❌ ما عندي صلاحية")

    # M2
    elif text == "قفل الروابط" and is_admin(message): 
        if "link" not in locks[chat_id]: locks[chat_id].append("link"); save_data()
        bot.reply_to(message, "🔒 تم قفل الروابط")
    elif text == "فتح الروابط" and is_admin(message): 
        if "link" in locks[chat_id]: locks[chat_id].remove("link"); save_data()
        bot.reply_to(message, "🔓 تم فتح الروابط")

    # M4
    elif text == "ايدي": bot.reply_to(message, f"🆔 ايديك : `{user_id}`\n👤 {name}")
    elif text == "معلوماتي": bot.reply_to(message, f"👤 {name}\n🆔 `{user_id}`")

    # M5
    elif text == "رفع مميز" and is_admin(message): bot.reply_to(message, "⭐ تم رفع مميز")
    elif text == "تنزيل مميز" and is_admin(message): bot.reply_to(message, "❌ تم تنزيل مميز")

    # M6
    elif text in ["تاج","ملك","ملكه","اثول","جلب","مطي","نسبه الحب"]:
        if text == "نسبه الحب": bot.reply_to(message, f"✨ نسبة الحب : {random.randint(70,100)}% ❤️")
        else: 
            replies = {"تاج":"🤴 تاج الملك","ملك":"🧝‍♂️ انت الملك","ملكه":"🧝‍♀️ انتي الملكة","اثول":"🤦‍♀️ اثول","جلب":"👩‍🎤 جلب","مطي":"🧑‍🦯 مطي"}
            bot.reply_to(message, replies.get(text))

    # M8
    elif text == "غنيلي": bot.reply_to(message, "🎵 اختار اغنيه")
    elif text == "زواج": bot.reply_to(message, "💍 تم زواجكم")
    elif text == "طلاق": bot.reply_to(message, "💔 تم الطلاق")

    # M9
    elif text == "انشاء حساب": bot.reply_to(message, "💳 تم انشاء حساب")
    elif text == "راتب": bot.reply_to(message, "💸 تم استلام الراتب : 500$")

    # M10 M11
    elif text.startswith("قفل ") and is_admin(message): 
        item = text.replace("قفل ","")
        if item not in locks[chat_id]: locks[chat_id].append(item); save_data()
        bot.reply_to(message, f"🔒 تم قفل {item}")
    elif text.startswith("فتح ") and is_admin(message): 
        item = text.replace("فتح ","")
        if item in locks[chat_id]: locks[chat_id].remove(item); save_data()
        bot.reply_to(message, f"🔓 تم فتح {item}")
    elif text.startswith("تفعيل ") and is_admin(message): 
        toggle = text.replace("تفعيل ","")
        toggles[f"{chat_id}_{toggle}"] = True; save_data(); bot.reply_to(message, f"✅ تم تفعيل {toggle}")
    elif text.startswith("تعطيل ") and is_admin(message): 
        toggle = text.replace("تعطيل ","")
        toggles[f"{chat_id}_{toggle}"] = False; save_data(); bot.reply_to(message, f"❌ تم تعطيل {toggle}")

# ===== رسائل الخاص للادمن =====
@bot.message_handler(func=lambda m: not is_dev(m.from_user.id) and m.chat.type == 'private')
def user_msg(message):
    if not PROTECTION: return
    txt = escape_md(message.text or f"[{message.content_type}]")
    bot.send_message(ADMIN_ID, f"⊱ 📩 من: {message.from_user.first_name}\n⊱ الايدي: `{message.from_user.id}`\n⊱ {txt}")

print(f"{BOT_NAME} Started...")
bot.infinity_polling(none_stop=True, timeout=60)
