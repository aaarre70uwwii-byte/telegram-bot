import telebot, os, json, time, sys, random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
DEVELOPER_ID = 7488375443
DB_FILE = "data.json"
votes = {}

def load_data():
    global data
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"groups": {}, "locks": {}, "settings": {}, "gban": [], "gmuted": [], "devs": [DEVELOPER_ID], "fun": {}, "marry": {}}

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

load_data()

def get_group(gid):
    gid = str(gid)
    if gid not in data["groups"]: data["groups"][gid] = {"owners":[], "admins":[], "mods":[], "creators":[], "vip":[]}
    if gid not in data["settings"]: data["settings"][gid] = {"link":"", "welcome":"", "rules":"", "channel":"", "download":False, "fun_on":True}
    if gid not in data["locks"]: data["locks"][gid] = {}
    if gid not in data["fun"]: data["fun"][gid] = {}
    return data["groups"][gid]

def get_settings(gid): return data["settings"].setdefault(str(gid), {"fun_on":True})
def get_locks(gid): return data["locks"].setdefault(str(gid), {})
def get_fun(gid): return data["fun"].setdefault(str(gid), {})

def is_admin(m):
    g = get_group(m.chat.id)
    uid = m.from_user.id
    if uid == DEVELOPER_ID or uid in data["devs"]: return True
    if uid in g["owners"] or uid in g["admins"] or uid in g["mods"] or uid in g["creators"]: return True
    try:
        if bot.get_chat_member(m.chat.id, uid).status in ["creator", "administrator"]: return True
    except: pass
    return False

def is_dev(m): return m.from_user.id == DEVELOPER_ID or m.from_user.id in data["devs"]
def get_user_name(user): return f"[{user.first_name}](tg://user?id={user.id})"

def main_panel():
    k = InlineKeyboardMarkup(row_width=3)
    k.row(InlineKeyboardButton("①", callback_data="m1"), InlineKeyboardButton("②", callback_data="m2"), InlineKeyboardButton("③", callback_data="m3"))
    k.row(InlineKeyboardButton("Dev اوامر", callback_data="m4"), InlineKeyboardButton("اوامر التسليه", callback_data="m5"))
    k.row(InlineKeyboardButton("⭐ اوامر خدميه", callback_data="m6"))
    k.row(InlineKeyboardButton("👑 الادمن", callback_data="admins_list"))
    return k

def get_back_button():
    k = InlineKeyboardMarkup()
    k.row(InlineKeyboardButton("🔙 الرجوع", callback_data="back"))
    return k

def show_menu(chat_id):
    text = "**AISED**\n\n- أهلاً بك عزي في قائمة الاوامر :\n━━━━━━━━━━━━━━━\n◀️ م1 : اوامر الادمنيه\n◀️ م2 : اوامر الاعدادات\n◀️ م3 : اوامر القفل - الفتح\n◀️ م4 : اوامر التسليه\n◀️ م5 : Dev اوامر\n◀️ م6 : الاوامر الخدميه\n━━━━━━━━━━━━━━━"
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_panel())

# فلتر الرسائل
@bot.message_handler(content_types=['text','photo','video','sticker','animation','forward'], func=lambda m: True)
def filter_messages(m):
    if m.chat.type not in ["group","supergroup"] or is_admin(m): return
    locks = get_locks(m.chat.id)
    if locks.get("links") and m.entities:
        if any(e.type in ["url","text_link"] for e in m.entities): bot.delete_message(m.chat.id, m.message_id)
    if locks.get("photo") and m.content_type == "photo": bot.delete_message(m.chat.id, m.message_id)

# الاوامر
@bot.message_handler(func=lambda m: True)
def catch_word(m):
    if not m.text: return
    text = m.text.strip()
    if m.chat.type in ["group","supergroup"]:
        g = get_group(m.chat.id); s = get_settings(m.chat.id); locks = get_locks(m.chat.id); fun = get_fun(m.chat.id)
    target = m.reply_to_message; uid = target.from_user.id if target else None

    if text in ["الاوامر","القائمة","menu"]: show_menu(m.chat.id); return

    # م1
    if is_admin(m):
        if text == "رفع ادمن" and target:
            if uid not in g["admins"]: g["admins"].append(uid); save_data()
            bot.reply_to(m, f"✅ تم رفع {get_user_name(target.from_user)} ادمن", parse_mode="Markdown")
        elif text == "حظر" and target: bot.ban_chat_member(m.chat.id, uid); bot.reply_to(m, "🚫 تم الحظر")
        elif text.startswith("مسح "):
            try:
                for i in range(int(text.split()[1])+1): bot.delete_message(m.chat.id, m.message_id-i)
            except: pass

    # م2
    if is_admin(m):
        if text == "الرابط": bot.reply_to(m, f"🔗 {s['link']}" if s["link"] else "❌ لا يوجد رابط")
        elif text.startswith("ضع رابط "): s["link"] = text[9:]; save_data(); bot.reply_to(m, "✅ تم حفظ الرابط")

    # م3
    if is_admin(m):
        if text == "قفل الروابط": locks["links"]=True; save_data(); bot.reply_to(m, "🔒 تم قفل الروابط")
        elif text == "فتح الروابط": locks["links"]=False; save_data(); bot.reply_to(m, "🔓 تم فتح الروابط")

    # م4
    if is_dev(m):
        if text == "رفع Dev" and target:
            if uid not in data["devs"]: data["devs"].append(uid); save_data()
            bot.reply_to(m, "👑 تم رفع مطور ثانوي", parse_mode="Markdown")
        elif text == "حظر عام" and target:
            if uid not in data["gban"]: data["gban"].append(uid); save_data()
            bot.reply_to(m, "🚫 تم الحظر العام")
        elif text.startswith("ذيع "):
            for gid in data["groups"]:
                try: bot.send_message(int(gid), f"📢 {text[4:]}")
                except: pass
            bot.reply_to(m, "✅ تمت الاذاعة")
        elif text == "اعاده تشغيل": bot.reply_to(m, "🔄"); os.execv(sys.executable, ['python'] + sys.argv)

    # م5
    if s.get("fun_on", True):
        RANK = {"هطف":"الهطوف","حمار":"الحمير","كلب":"الكلاب"}
        for r,p in RANK.items():
            if text == f"رفع {r}" and target:
                fun.setdefault(r,[]);
                if uid not in fun[r]: fun[r].append(uid); save_data()
                bot.reply_to(m, f"✅ تم رفع {get_user_name(target.from_user)} {p}", parse_mode="Markdown")
        if text == "رتب التسليه":
            txt = "**رتب التسليه:**\n"+"\n".join([f"{p}: {len(fun.get(r,[]))}" for r,p in RANK.items()])
            bot.reply_to(m, txt, parse_mode="Markdown")
        if text == "تتزوجني" and target:
            if m.from_user.id not in data["marry"] and target.from_user.id not in data["marry"]:
                data["marry"][m.from_user.id]=target.from_user.id; data["marry"][target.from_user.id]=m.from_user.id; save_data()
                bot.reply_to(m, "💍 مبروك تم الزواج", parse_mode="Markdown")

# الازرار
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "back": show_menu(call.message.chat.id)
    elif call.data == "m1": bot.edit_message_text("**م1 - الادمنية**\nرفع ادمن - حظر - مسح", call.message.chat.id, call.message_id, parse_mode="Markdown", reply_markup=get_back_button())
    elif call.data == "m2": bot.edit_message_text("**م2 - الاعدادات**\nالرابط - ضع رابط", call.message.chat.id, call.message_id, parse_mode="Markdown", reply_markup=get_back_button())
    elif call.data == "m3": bot.edit_message_text("**م3 - القفل**\nقفل الروابط", call.message.chat.id, call.message_id, parse_mode="Markdown", reply_markup=get_back_button())
    elif call.data == "m4": bot.edit_message_text("**م4 - Dev**\nرفع Dev - حظر عام - ذيع", call.message.chat.id, call.message_id, parse_mode="Markdown", reply_markup=get_back_button())
    elif call.data == "m5": bot.edit_message_text("**م5 - التسليه**\nرفع هطف - رتب التسليه - تزوج", call.message.chat.id, call.message_id, parse_mode="Markdown", reply_markup=get_back_button())
    bot.answer_callback_query(call.id)

print("Tia Panel v11.0 كامل اشتغل")
bot.infinity_polling()
