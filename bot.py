import telebot, os, json, time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not found")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)
DEVELOPER_ID = 7488375443
DB_FILE = "data.json"

# ======== قاعدة بيانات بحفظ تلقائي ========
def load_data():
    global data
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"groups": {}, "locks": {}, "settings": {}}

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

load_data()

def get_group(gid):
    gid = str(gid)
    if gid not in data["groups"]:
        data["groups"][gid] = {"owners":[], "admins":[], "mods":[], "banned":[], "muted":[]}
        save_data()
    return data["groups"][gid]

def is_admin(m):
    g = get_group(m.chat.id)
    uid = m.from_user.id
    if uid == DEVELOPER_ID: return True
    if uid in g["owners"] or uid in g["admins"] or uid in g["mods"]: return True
    try:
        member = bot.get_chat_member(m.chat.id, uid)
        if member.status in ["creator", "administrator"]: return True
    except: pass
    return False

# ======== الازرار ========
def get_buttons():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("م1 الادمنية", callback_data="m1"))
    keyboard.row(InlineKeyboardButton("م2 الاعدادات", callback_data="m2"))
    keyboard.row(InlineKeyboardButton("م3 القفل", callback_data="m3"))
    keyboard.row(InlineKeyboardButton("م4 المطور", callback_data="m4"))
    keyboard.row(InlineKeyboardButton("م5 التسليه", callback_data="m5"))
    keyboard.row(InlineKeyboardButton("❌ الغاء", callback_data="cancel"))
    return keyboard

def get_back_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("🔙 الرجوع", callback_data="back"))
    return keyboard

# ======== اوامر اساسية =========
@bot.message_handler(commands=['start'])
def start(m): bot.reply_to(m, "🤖 بوت تيا v3.1 شغال\nاكتب /تفعيل")

@bot.message_handler(commands=['تفعيل'])
def activate(m):
    if m.chat.type not in ["group", "supergroup"]: return bot.reply_to(m, "هذا الامر للمجموعات فقط")
    if not is_admin(m): return bot.reply_to(m, "❌ هذا الامر للادمنية فقط")
    get_group(m.chat.id)
    text = f"""**تم تفعيل المجموعة ✅**

**الاسم**: {m.chat.title}
**الايدي**: `{m.chat.id}`

اختر من القائمة:"""
    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=get_buttons())

# ======== م1 الادمنية =========
@bot.message_handler(regexp="^(رفع|تنزيل) (مالك|ادمن|مشرف|مميز)$")
def rank_cmd(m):
    if not is_admin(m): return bot.reply_to(m, "❌ انت لست ادمن")
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    act, rank = m.text.split()[0], m.text.split()[1]
    uid = m.reply_to_message.from_user.id
    g = get_group(m.chat.id)
    key = "admins" if rank == "ادمن" else "mods" if rank == "مشرف" else "owners" if rank == "مالك" else rank

    if act == "رفع":
        if uid not in g[key]: g[key].append(uid)
        bot.reply_to(m, f"✅ تم رفع {m.reply_to_message.from_user.first_name} {rank}")
    else:
        if uid in g[key]: g[key].remove(uid)
        bot.reply_to(m, f"❌ تم تنزيل {m.reply_to_message.from_user.first_name} من {rank}")
    save_data()

@bot.message_handler(commands=['تنزيل_الكل'])
def del_all_ranks(m):
    if not is_admin(m): return
    g = get_group(m.chat.id)
    g["owners"] = []; g["admins"] = []; g["mods"] = []
    save_data()
    bot.reply_to(m, "✅ تم تنزيل الكل")

@bot.message_handler(regexp="^(حظر|طرد|كتم|تقييد)$")
def punish(m):
    if not is_admin(m): return bot.reply_to(m, "❌ انت لست ادمن")
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    uid = m.reply_to_message.from_user.id
    cmd = m.text
    try:
        if cmd == "حظر": bot.ban_chat_member(m.chat.id, uid)
        if cmd == "طرد": bot.ban_chat_member(m.chat.id, uid); bot.unban_chat_member(m.chat.id, uid)
        if cmd == "كتم": bot.restrict_chat_member(m.chat.id, uid, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
        if cmd == "تقييد": bot.restrict_chat_member(m.chat.id, uid, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
        bot.reply_to(m, f"✅ تم {cmd} {m.reply_to_message.from_user.first_name}")
    except Exception as e: bot.reply_to(m, f"❌ خطأ: {e}")

@bot.message_handler(regexp="^(الغاء الحظر|الغاء الكتم|فك التقييد)$")
def unpunish(m):
    if not is_admin(m): return
    if not m.reply_to_message: return
    uid = m.reply_to_message.from_user.id
    bot.unban_chat_member(m.chat.id, uid)
    bot.restrict_chat_member(m.chat.id, uid, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
    bot.reply_to(m, "✅ تم فك العقوبة")

@bot.message_handler(commands=['مسح'])
def delete_msg(m):
    if not is_admin(m): return
    if m.reply_to_message: bot.delete_message(m.chat.id, m.reply_to_message.message_id)

# ======== م2 الاعدادات =========
@bot.message_handler(commands=['الرابط'])
def link(m):
    if not is_admin(m): return
    try:
        link = bot.export_chat_invite_link(m.chat.id)
        bot.reply_to(m, f"🔗 رابط المجموعة:\n{link}")
    except: bot.reply_to(m, "❌ ماعندي صلاحية جلب الرابط")

@bot.message_handler(commands=['القوانين'])
def rules(m):
    rules = data["settings"].get(str(m.chat.id),{}).get("rules","لا توجد قوانين")
    bot.reply_to(m, f"📜 القوانين:\n{rules}")

@bot.message_handler(commands=['ضع_قوانين'])
def set_rules(m):
    if not is_admin(m): return
    rules = m.text.replace("/ضع_قوانين ","")
    data["settings"].setdefault(str(m.chat.id),{})["rules"] = rules
    save_data()
    bot.reply_to(m, "✅ تم وضع القوانين")

# ======== م3 القفل =========
@bot.message_handler(regexp="^(قفل|فتح) (الروابط|الصور|الفيديو|الملصقات|الدردشه|الكل)$")
def lock(m):
    if not is_admin(m): return
    lock_type = m.text.split()[1]
    state = "قفل" in m.text
    data["locks"].setdefault(str(m.chat.id),{})[lock_type] = state
    save_data()
    bot.reply_to(m, f"✅ تم {'قفل' if state else 'فتح'} {lock_type}")

# ======== م4 المطور =========
@bot.message_handler(commands=['اذاعه'])
def broadcast(m):
    if m.from_user.id!= DEVELOPER_ID: return
    msg = m.text.replace("/اذاعه ","")
    for gid in data["groups"]:
        try: bot.send_message(gid, f"📢 اذاعة:\n{msg}")
        except: pass
    bot.reply_to(m, "✅ تمت الاذاعة")

@bot.message_handler(commands=['غادر'])
def leave(m):
    if m.from_user.id!= DEVELOPER_ID: return
    bot.leave_chat(m.chat.id)

# ======== م5 التسليه =========
@bot.message_handler(regexp="^(رفع|تنزيل) (هطف|بثر|حمار|كلب|خروف|خفيف)$")
def tsalya_cmd(m):
    act, rank = m.text.split()[0], m.text.split()[1]
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    bot.reply_to(m, f"✅ تم {act} {m.reply_to_message.from_user.first_name} {rank} 😂")

@bot.message_handler(commands=['زواج'])
def marriage(m):
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص")
    bot.reply_to(m, f"💍 {m.from_user.first_name} طلب الزواج من {m.reply_to_message.from_user.first_name}")

# ======== ازرار القائمة ========
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message_id # <-- هنا كان الخطأ

    if call.data == "m1":
        text = """**📜 م1 - اوامر الادمنية**
`رفع ادمن` `رفع مشرف` `رفع مالك` - بالرد
`تنزيل ادمن` - بالرد
`حظر` `طرد` `كتم` `تقييد` - بالرد
`الغاء الحظر` - بالرد
`مسح` - بالرد
`/تنزيل_الكل`"""
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

    elif call.data == "m2":
        text = """**⚙️ م2 - الاعدادات**
`/الرابط` - جلب رابط المجموعة
`/القوانين` - عرض القوانين
`/ضع_قوانين` - لوضع قوانين"""
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

    elif call.data == "m3":
        text = """**🔒 م3 - القفل والفتح**
`قفل الروابط` / `فتح الروابط`
`قفل الصور` / `فتح الصور`
`قفل الفيديو` / `فتح الفيديو`
`قفل الملصقات` / `فتح الملصقات`
`قفل الدردشه` / `فتح الدردشه`
`قفل الكل` / `فتح الكل`"""
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

    elif call.data == "m4":
        text = """**👑 م4 - اوامر المطور**
`/اذاعه` - رسالة لكل المجموعات
`/غادر` - خروج البوت"""
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

    elif call.data == "m5":
        text = """**😂 م5 - التسليه**
`رفع هطف` `رفع بثر` - بالرد
`تنزيل هطف` - بالرد
`/زواج` - بالرد"""
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

    elif call.data == "back":
        text = "**القائمة الرئيسية**\nاختر من الاسفل"
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_buttons())

    elif call.data == "cancel":
        bot.delete_message(chat_id, msg_id)
    bot.answer_callback_query(call.id)

print("Tia v3.1 اشتغل")
bot.infinity_polling()
