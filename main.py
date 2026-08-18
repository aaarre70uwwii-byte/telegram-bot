import telebot, json, re, os
from telebot import types

# يسحب التوكن من المتغيرات البيئية تلقائي
API_TOKEN = os.environ.get('BOT_TOKEN') # اسم المتغير BOT_TOKEN
ADMIN_ID = 7488375443 # حط ايديك
MY_CHANNEL = "eeccvu" # قناتك بدون @

if not API_TOKEN:
    raise ValueError("⊱ ❌ التوكن مش موجود! حط التوكن في متغير BOT_TOKEN")

bot = telebot.TeleBot(API_TOKEN)

# ملف الحفظ
DATA_FILE = "data.json"

def load_data():
    global users, blocked_users, required_channels
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = set(data.get("users", []))
            blocked_users = set(data.get("blocked_users", []))
            required_channels = data.get("required_channels", [MY_CHANNEL])
    else:
        users = set()
        blocked_users = set()
        required_channels = [MY_CHANNEL]

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "users": list(users),
            "blocked_users": list(blocked_users),
            "required_channels": required_channels
        }, f, ensure_ascii=False, indent=2)

load_data()

def normalize_channel(text):
    if not text: return None
    text = text.strip()
    if text.startswith("https://t.me/"): text = text.split("https://t.me/")[-1].strip("/")
    if text.startswith("http://t.me/"): text = text.split("http://t.me/")[-1].strip("/")
    text = text.lstrip("@")
    text = re.sub(r'[^A-Za-z0-9_]', '', text)
    return text if text else None

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("⊱ 👥 قائمة المستخدمين"), types.KeyboardButton("⊱ 🚫 حظر عضو"))
    markup.add(types.KeyboardButton("⊱ 📢 إذاعة للكل"), types.KeyboardButton("⊱ 🔓 فك حظر"))
    markup.add(types.KeyboardButton("⊱ ➕ إضافة قناة"), types.KeyboardButton("⊱ ➖ حذف قناة"))
    return markup

def user_msg_btns(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⊱ 🟩 الدخول للمطور", url=f"tg://user?id={ADMIN_ID}"))
    for i, ch in enumerate(required_channels):
        markup.add(types.InlineKeyboardButton(f"⊱ 🔗 قناة {i+1}", url=f"https://t.me/{ch}"))
    markup.add(types.InlineKeyboardButton("⊱ 🟩 الرد", callback_data=f"reply_{user_id}"), types.InlineKeyboardButton("⊱ 🔴 رجوع", callback_data="back_to_menu"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name or ""
    if user_id in blocked_users:
        bot.send_message(user_id, "⊱ ⚠️ عذراً، أنت محظور من استخدام البوت.")
        return
    if user_id not in users:
        users.add(user_id); save_data()

    if required_channels:
        ok = True
        for ch in required_channels:
            try:
                if bot.get_chat_member(f"@{ch}", user_id).status not in ['creator', 'administrator', 'member']:
                    ok = False; break
            except: ok = False; break
        if not ok:
            kb = types.InlineKeyboardMarkup()
            for ch in required_channels: kb.add(types.InlineKeyboardButton(f"⊱ دخول @{ch}", url=f"https://t.me/{ch}"))
            kb.add(types.InlineKeyboardButton("⊱ ✅ تحقّق الاشتراك", callback_data=f"check_subs_{user_id}"))
            bot.send_message(user_id, f"⊱ مرحباً: {name}\n⊱ الرجاء الاشتراك في القنوات المطلوبة", reply_markup=kb); return

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⊱ 🟩 الدخول للمطور", url=f"tg://user?id={ADMIN_ID}"))
    kb.add(types.InlineKeyboardButton("⊱ 🔗 قناتنا الرسمية", url=f"https://t.me/{MY_CHANNEL}"))
    bot.send_message(user_id, "⊱ مرحباً: 𓆩 Deadline Services 𓆪\n⊱ ارسل رسالتك الى الدعم", reply_markup=kb)

@bot.message_handler(func=lambda m: m.from_user.id!= ADMIN_ID)
def handle_user_messages(message):
    if message.from_user.id in blocked_users: return
    uid = message.from_user.id; name = message.from_user.first_name or ""
    body = message.text if message.content_type == 'text' else message.caption or "وسائط"
    forwarded = f"⊱ 📩 من: {name}\n⊱ الايدي: `{uid}`\n⊱ {body}"
    try: bot.send_message(ADMIN_ID, forwarded, reply_markup=user_msg_btns(uid), parse_mode="Markdown")
    except: pass

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def handle_admin_commands(message):
    text = message.text or ""
    if text == "⊱ 👥 قائمة المستخدمين": bot.send_message(ADMIN_ID, f"⊱ 📊 عدد المشتركين: {len(users)}", reply_markup=admin_keyboard())
    elif text == "⊱ 🚫 حظر عضو": msg = bot.send_message(ADMIN_ID, "⊱ ارسل ايدي الشخص:", reply_markup=admin_keyboard()); bot.register_next_step_handler(msg, process_block)
    elif text == "⊱ 🔓 فك حظر": msg = bot.send_message(ADMIN_ID, "⊱ ارسل ايدي الشخص:", reply_markup=admin_keyboard()); bot.register_next_step_handler(msg, process_unblock)
    elif text == "⊱ 📢 إذاعة للكل": msg = bot.send_message(ADMIN_ID, "⊱ ارسل نص الإذاعة:", reply_markup=admin_keyboard()); bot.register_next_step_handler(msg, process_broadcast)
    elif text == "⊱ ➕ إضافة قناة": msg = bot.send_message(ADMIN_ID, "⊱ ارسل اسم القناة:", reply_markup=admin_keyboard()); bot.register_next_step_handler(msg, process_add_channel)
    elif text == "⊱ ➖ حذف قناة":
        if not required_channels: bot.send_message(ADMIN_ID, "⊱ لا توجد قنوات.", reply_markup=admin_keyboard()); return
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for ch in required_channels: markup.add(types.KeyboardButton(f"⊱ حذف {ch}"))
        markup.add(types.KeyboardButton("⊱ إلغاء")); msg = bot.send_message(ADMIN_ID, "⊱ اختار قناة للحذف:", reply_markup=markup); bot.register_next_step_handler(msg, process_remove_channel_choice)

def process_block(m):
    try: blocked_users.add(int(m.text)); save_data(); bot.send_message(ADMIN_ID, f"⊱ ✅ تم الحظر", reply_markup=admin_keyboard())
    except: bot.send_message(ADMIN_ID, "⊱ ❌ ايدي غلط", reply_markup=admin_keyboard())
def process_unblock(m):
    try: blocked_users.discard(int(m.text)); save_data(); bot.send_message(ADMIN_ID, f"⊱ ✅ تم فك الحظر", reply_markup=admin_keyboard())
    except: bot.send_message(ADMIN_ID, "⊱ ❌ ايدي غلط", reply_markup=admin_keyboard())
def process_broadcast(m):
    count=0
    for user in list(users):
        try: bot.send_message(user, f"⊱ 📢 رسالة عامة\n⊱ {m.text}"); count+=1
        except: continue
    bot.send_message(ADMIN_ID, f"⊱ ✅ تم الارسال لـ {count}", reply_markup=admin_keyboard())
def process_add_channel(m):
    ch = normalize_channel(m.text)
    if not ch or ch in required_channels: bot.send_message(ADMIN_ID, "⊱ ❌ خطأ او مضافة", reply_markup=admin_keyboard()); return
    required_channels.append(ch); save_data(); bot.send_message(ADMIN_ID, f"⊱ ✅ تم إضافة @{ch}", reply_markup=admin_keyboard())
def process_remove_channel_choice(m):
    if m.text == "⊱ إلغاء": bot.send_message(ADMIN_ID, "⊱ تم الإلغاء.", reply_markup=admin_keyboard()); return
    ch = normalize_channel(m.text.replace("⊱ حذف ", ""))
    if ch in required_channels: required_channels.remove(ch); save_data(); bot.send_message(ADMIN_ID, f"⊱ ✅ تم حذف @{ch}", reply_markup=admin_keyboard())
    else: bot.send_message(ADMIN_ID, "⊱ غير موجودة", reply_markup=admin_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id)
    if call.data.startswith("reply_"):
        uid = int(call.data.split("_")[1]); msg = bot.send_message(ADMIN_ID, "⊱ ارسل ردك:"); bot.register_next_step_handler(msg, send_reply_to_user, uid)
    elif call.data == "back_to_menu": bot.send_message(ADMIN_ID, "⊱ 🏠 القائمة", reply_markup=admin_keyboard())
    elif call.data.startswith("check_subs_"):
        uid = int(call.data.split("_")[2]); ok=True
        for ch in required_channels:
            try:
                if bot.get_chat_member(f"@{ch}", uid).status not in ['creator', 'administrator', 'member']: ok=False
            except: ok=False
        if ok: bot.send_message(uid, "⊱ ✅ تم التحقق"); start(call.message)
        else: bot.send_message(uid, "⊱ ❌ لم تشترك بعد")

def prefix_lines(text): return "\n".join("⊱ " + line for line in text.splitlines()) if text else "⊱ None"
def send_reply_to_user(message, user_id):
    try:
        if message.content_type == 'text': bot.send_message(user_id, prefix_lines(message.text))
        elif message.content_type == 'photo': bot.send_photo(user_id, message.photo[-1].file_id, caption=prefix_lines(message.caption or ""))
        elif message.content_type == 'video': bot.send_video(user_id, message.video.file_id, caption=prefix_lines(message.caption or ""))
        elif message.content_type == 'document': bot.send_document(user_id, message.document.file_id, caption=prefix_lines(message.caption or ""))
        elif message.content_type == 'audio': bot.send_audio(user_id, message.audio.file_id, caption=prefix_lines(message.caption or ""))
        elif message.content_type == 'voice': bot.send_voice(user_id, message.voice.file_id, caption=prefix_lines(message.caption or ""))
        else: bot.send_message(user_id, prefix_lines("⊱ نوع غير مدعوم"))
        bot.send_message(ADMIN_ID, "⊱ ✅ تم الرد", reply_markup=admin_keyboard())
    except: bot.send_message(ADMIN_ID, "⊱ ❌ فشل الارسال", reply_markup=admin_keyboard())

print("Bot Started...")
bot.infinity_polling()
