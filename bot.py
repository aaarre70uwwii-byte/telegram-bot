import telebot, os, json, time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
DEVELOPER_ID = 7488375443

# قاعدة بيانات مؤقتة
data = {"groups": {}, "ranks": {}, "locks": {}, "settings": {}}

def get_group(gid):
    gid = str(gid)
    if gid not in data["groups"]:
        data["groups"][gid] = {"admins":[], "mods":[], "owners":[], "banned":[], "muted":[]}
    return data["groups"][gid]

def get_buttons():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("م1 الادمنية", callback_data="m1"))
    keyboard.row(InlineKeyboardButton("م2 الاعدادات", callback_data="m2"))
    keyboard.row(InlineKeyboardButton("م3 القفل", callback_data="m3"))
    keyboard.row(InlineKeyboardButton("م4 المطور", callback_data="m4"))
    keyboard.row(InlineKeyboardButton("م5 التسليه", callback_data="m5"))
    keyboard.row(InlineKeyboardButton("الغاء", callback_data="cancel"))
    return keyboard

# ======== اوامر اساسية =========
@bot.message_handler(commands=['start'])
def start(m): bot.reply_to(m, "🤖 بوت تيا شغال\nاكتب /تفعيل")

@bot.message_handler(commands=['تفعيل'])
def activate(m):
    get_group(m.chat.id)
    text = f"""- : تم تفعيل مجموعة تلقائيا
- : اسم المجموعه [ {m.chat.title} ]
- : ايدي المجموعه [ `{m.chat.id}` ]"""
    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=get_buttons())

# ======== م1 الادمنية =========
@bot.message_handler(regexp="^(رفع|تنزيل) (مالك اساسي|مالك|مشرف|منشئ|مدير|ادمن|مميز)$")
def rank_cmd(m):
    act, rank = m.text.split()[0], " ".join(m.text.split()[1:])
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    uid = m.reply_to_message.from_user.id
    g = get_group(m.chat.id)
    key = rank
    if act == "رفع":
        if uid not in g.get(key, []): g.setdefault(key, []).append(uid)
        bot.reply_to(m, f"✅ تم رفع {m.reply_to_message.from_user.first_name} {rank}")
    else:
        if uid in g.get(key, []): g[key].remove(uid)
        bot.reply_to(m, f"❌ تم تنزيل {m.reply_to_message.from_user.first_name} من {rank}")

@bot.message_handler(commands=['تنزيل_الكل'])
def del_all_ranks(m):
    g = get_group(m.chat.id)
    for k in ["مالك اساسي","مالك","مشرف","منشئ","مدير","ادمن","مميز"]: g[k] = []
    bot.reply_to(m, "✅ تم تنزيل الكل")

@bot.message_handler(regexp="^(حظر|طرد|كتم|تقييد)$")
def punish(m):
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    uid = m.reply_to_message.from_user.id
    cmd = m.text
    if cmd == "حظر": bot.ban_chat_member(m.chat.id, uid)
    if cmd == "طرد": bot.ban_chat_member(m.chat.id, uid); bot.unban_chat_member(m.chat.id, uid)
    if cmd == "كتم": bot.restrict_chat_member(m.chat.id, uid, can_send_messages=False)
    if cmd == "تقييد": bot.restrict_chat_member(m.chat.id, uid, can_send_messages=False, can_send_media_messages=False)
    bot.reply_to(m, f"✅ تم {cmd} {m.reply_to_message.from_user.first_name}")

@bot.message_handler(regexp="^(الغاء الحظر|الغاء الكتم|فك التقييد)$")
def unpunish(m):
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    uid = m.reply_to_message.from_user.id
    bot.unban_chat_member(m.chat.id, uid)
    bot.restrict_chat_member(m.chat.id, uid, can_send_messages=True, can_send_media_messages=True)
    bot.reply_to(m, "✅ تم فك العقوبة")

@bot.message_handler(commands=['مسح'])
def delete_msg(m):
    if m.reply_to_message: bot.delete_message(m.chat.id, m.reply_to_message.message_id)

# ======== م2 الاعدادات =========
@bot.message_handler(commands=['الرابط'])
def link(m): bot.reply_to(m, "ارسل /اضف_رابط لوضعه")

@bot.message_handler(commands=['القوانين'])
def rules(m): bot.reply_to(m, data["settings"].get(str(m.chat.id),{}).get("rules","لا توجد قوانين"))

@bot.message_handler(commands=['ضع_قوانين'])
def set_rules(m):
    rules = m.text.replace("/ضع_قوانين ","")
    data["settings"].setdefault(str(m.chat.id),{})["rules"] = rules
    bot.reply_to(m, "✅ تم وضع القوانين")

# ======== م3 القفل =========
@bot.message_handler(regexp="^(قفل|فتح) (الروابط|الصور|الفيديو|الملصقات|الدردشه|الكل)$")
def lock(m):
    lock_type = m.text.split()[1]
    state = "قفل" in m.text
    data["locks"].setdefault(str(m.chat.id),{})[lock_type] = state
    bot.reply_to(m, f"✅ تم {'قفل' if state else 'فتح'} {lock_type}")

# ======== م4 المطور =========
@bot.message_handler(commands=['اذاعه'])
def broadcast(m):
    if m.from_user.id!= DEVELOPER_ID: return
    msg = m.text.replace("/اذاعه ","")
    for gid in data["groups"]: bot.send_message(gid, msg)
    bot.reply_to(m, "✅ تمت الاذاعة")

@bot.message_handler(commands=['غادر'])
def leave(m):
    if m.from_user.id!= DEVELOPER_ID: return
    bot.leave_chat(m.chat.id)

# ======== م5 التسليه =========
TSALYA = ["هطف","بثر","حمار","كلب","خروف","خفيف"]
@bot.message_handler(regexp="^(رفع|تنزيل) (هطف|بثر|حمار|كلب|خروف|خفيف)$")
def tsalya_cmd(m):
    act, rank = m.text.split()[0], m.text.split()[1]
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    bot.reply_to(m, f"✅ تم {act} {m.reply_to_message.from_user.first_name} {rank}")

@bot.message_handler(commands=['زواج'])
def marriage(m):
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    bot.reply_to(m, f"💍 {m.from_user.first_name} طلب الزواج من {m.reply_to_message.from_user.first_name}")

# ======== ازرار القائمة =========
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "m1": bot.answer_callback_query(call.id, "اوامر الرفع الحظر الطرد")
    elif call.data == "m2": bot.answer_callback_query(call.id, "اوامر الرابط القوانين الاعدادات")
    elif call.data == "m3": bot.answer_callback_query(call.id, "اوامر القفل والفتح")
    elif call.data == "m4": bot.answer_callback_query(call.id, "اوامر المطور")
    elif call.data == "m5": bot.answer_callback_query(call.id, "اوامر التسليه")
    elif call.data == "cancel": bot.delete_message(call.message.chat.id, call.message_id)

print("Tia v3.0 اشتغل")
bot.infinity_polling()
