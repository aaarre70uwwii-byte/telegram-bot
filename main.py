# -*- coding: utf-8 -*-
import telebot, json, os, random, time
from telebot import types

API_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7488375443
BOT_NAME = "𝐓𝐢𝐚"
WELCOME_PHOTO = "https://t.me/eeccvu/2"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
DATA_FILE = "tia_data.json"

def load_data():
    global users, admins, devs, sec_devs, PROTECTION, REPLY_TEXT, locks, toggles, active_groups, bank, ranks, whispers
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
        users=set(data.get("users",[])); admins=set(data.get("admins",[])); devs=set(data.get("devs",[])); sec_devs=set(data.get("sec_devs",[]))
        PROTECTION=data.get("PROTECTION",True); REPLY_TEXT=data.get("REPLY_TEXT","⊱ اهلا بك في الدعم")
        locks={int(k):v for k,v in data.get("locks",{}).items()}; toggles=data.get("toggles",{}); active_groups=set(data.get("active_groups",[])); bank=data.get("bank",{})
        ranks=data.get("ranks",{}); whispers=data.get("whispers",{})
    else: users=set(); admins=set(); devs=set(); sec_devs=set(); PROTECTION=True; REPLY_TEXT="⊱ اهلا بك"; locks={}; toggles={}; active_groups=set(); bank={}; ranks={}; whispers={}
def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"users":list(users),"admins":list(admins),"devs":list(devs),"sec_devs":list(sec_devs),"PROTECTION":PROTECTION,"REPLY_TEXT":REPLY_TEXT,
                   "locks":locks,"toggles":toggles,"active_groups":list(active_groups),"bank":bank,"ranks":ranks,"whispers":whispers}, f, ensure_ascii=False)
load_data()

def is_dev(u): return u==ADMIN_ID or u in admins or u in devs
def is_admin(m):
    if m.chat.type=='private': return False
    try: return bot.get_chat_member(m.chat.id,m.from_user.id).status in ['administrator','creator']
    except: return False
def get_rank(chat_id, user_id):
    return ranks.get(f"{chat_id}_{user_id}", "عضو")

def dev_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("⊱ معلومات التنصيب"))
    markup.row(types.KeyboardButton("⊱ اعدادات البوت"), types.KeyboardButton("⊱ اعدادات الاساسي"))
    markup.row(types.KeyboardButton("⊱ اوامر الاذاعة"), types.KeyboardButton("⊱ الاوامر العامة"))
    markup.row(types.KeyboardButton("⊱ الغاء الامر"))
    return markup

def main_inline():
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(" (1) الاداره ",callback_data="m1"),types.InlineKeyboardButton(" (2) الحمايه ",callback_data="m2"))
    markup.add(types.InlineKeyboardButton(" (3) المطورين ",callback_data="m3"),types.InlineKeyboardButton(" (4) الاعضاء ",callback_data="m4"))
    markup.add(types.InlineKeyboardButton(" (5) الرفع ",callback_data="m5"),types.InlineKeyboardButton(" (6) التحشيش ",callback_data="m6"))
    markup.add(types.InlineKeyboardButton(" (7) المطور ",callback_data="m7"),types.InlineKeyboardButton(" (8) التسليه ",callback_data="m8"))
    markup.add(types.InlineKeyboardButton(" (9) البنك ",callback_data="m9"),types.InlineKeyboardButton(" (10) القفل ",callback_data="m10"))
    markup.add(types.InlineKeyboardButton(" (11) التفعيل ",callback_data="m11"))
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id not in users: users.add(m.from_user.id); save_data()
    txt = f"⊱ مرحبا {m.from_user.first_name} في {BOT_NAME}\n⊱ {REPLY_TEXT}"
    if is_dev(m.from_user.id): bot.send_photo(m.chat.id, WELCOME_PHOTO, caption=txt, reply_markup=dev_keyboard())
    else: bot.send_photo(m.chat.id, WELCOME_PHOTO, caption=txt)

@bot.message_handler(func=lambda m: is_dev(m.from_user.id) and m.chat.type=='private')
def dev_panel(m):
    global PROTECTION, REPLY_TEXT
    if m.text == "⊱ معلومات التنصيب":
        bot.send_message(ADMIN_ID, f"⊱ اسم البوت: {BOT_NAME}\n⊱ المستخدمين: {len(users)}\n⊱ الكروبات: {len(active_groups)}", reply_markup=dev_keyboard())
    elif m.text == "⊱ اعدادات البوت":
        kb=types.ReplyKeyboardMarkup(resize_keyboard=True); kb.row("⊱ 🔒 تفعيل الحماية","⊱ 🔓 تعطيل الحماية"); kb.row("⊱ اضف رد"); kb.row("⊱ الغاء الامر")
        bot.send_message(ADMIN_ID,"⊱ اعدادات البوت:",reply_markup=kb)
    elif m.text == "⊱ اعدادات الاساسي":
        lst="\n".join([f"⊱ `{i}`" for i in admins]) if admins else "⊱ لا يوجد"
        bot.send_message(ADMIN_ID,f"⊱ المطور الاساسي: `{ADMIN_ID}`\n⊱ المطورين:\n{lst}",reply_markup=dev_keyboard())
    elif m.text == "⊱ اوامر الاذاعة": msg=bot.send_message(ADMIN_ID,"⊱ ارسل نص الاذاعة"); bot.register_next_step_handler(msg,broadcast)
    elif m.text == "⊱ الاوامر العامة": bot.send_message(ADMIN_ID,f"⊱ المشتركين: {len(users)}",reply_markup=dev_keyboard())
    elif m.text == "⊱ الغاء الامر": bot.send_message(ADMIN_ID,"⊱ تم الالغاء",reply_markup=dev_keyboard())
    elif m.text == "⊱ 🔒 تفعيل الحماية": PROTECTION=True; save_data(); bot.send_message(ADMIN_ID,"⊱ ✅ تم التفعيل",reply_markup=dev_keyboard())
    elif m.text == "⊱ 🔓 تعطيل الحماية": PROTECTION=False; save_data(); bot.send_message(ADMIN_ID,"⊱ ❌ تم التعطيل",reply_markup=dev_keyboard())
    elif m.text == "⊱ اضف رد": msg=bot.send_message(ADMIN_ID,"⊱ ارسل الرد الجديد"); bot.register_next_step_handler(msg,set_reply)

def set_reply(m): global REPLY_TEXT; REPLY_TEXT=m.text; save_data(); bot.send_message(ADMIN_ID,"⊱ ✅ تم الحفظ",reply_markup=dev_keyboard())

def broadcast(m):
    c=0
    for u in users:
        try:
            bot.send_photo(u,WELCOME_PHOTO,caption=f"⊱ 📢 {BOT_NAME}\n⊱ {m.text}")
            c+=1
        except:
            pass
    bot.send_message(ADMIN_ID,f"⊱ ✅ تم الارسال لـ {c}",reply_markup=dev_keyboard())

@bot.message_handler(func=lambda m: m.text=="الاوامر" and m.chat.type in ['group','supergroup'])
def cmds(m):
    if m.chat.id not in active_groups: return bot.reply_to(m,"❌ اكتب تفعيل البوت اول")
    bot.send_message(m.chat.id,"--━━ 𝐓𝐢𝐚 ━━--",reply_markup=main_inline())

@bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'] and m.text=="تفعيل البوت" and is_admin(m))
def activate(m): active_groups.add(m.chat.id); save_data(); bot.reply_to(m,"✅ تم تفعيل المجموعة")

@bot.callback_query_handler(func=lambda c: True)
def call(c):
    d={"m1":"⊱ M1 الاداره\nرفع ادمن - تنزيل ادمن - تثبيت - الغاء التثبيت",
       "m2":"⊱ M2 الحمايه\nقفل التكرار - قفل الكلايش",
       "m3":"⊱ M3 المطورين\nرفع مطور - تنزيل مطور - قائمة المطورين",
       "m4":"⊱ M4 الاعضاء\nايدي - معلوماتي - رتبتي",
       "m5":"⊱ M5 الرفع\nرفع مميز - تنزيل مميز - رفع مدير - تنزيل مدير - رفع منشئ - تنزيل منشئ",
       "m6":"⊱ M6 التحشيش\nتاج - ملك - نسبه الحب - نسبه الغباء - همسه",
       "m7":"⊱ M7 المطور\nاذاعه - حظر عام - الغاء حظر عام",
       "m8":"⊱ M8 التسليه\nزواج - طلاق - غنيلي - توب",
       "m9":"⊱ M9 البنك\nانشاء حساب - راتب - فلوسي - تحويل",
       "m10":"⊱ M10 القفل\nقفل الروابط الصور الفيديو الملصقات الدردشه المتحركه",
       "m11":"⊱ M11 التفعيل\nتفعيل الرابط - تعطيل الترحيب - تفعيل الردود"}
    bot.edit_message_text(f"{d[c.data]}",c.message.chat.id,c.message.message_id,reply_markup=main_inline())

# ===== M1 الادارة =====
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text in ["رفع ادمن","تنزيل ادمن"] and is_admin(m))
def m1(m):
    if not m.reply_to_message: return bot.reply_to(m,"❌ رد على الشخص")
    t=m.reply_to_message.from_user.id
    if m.text=="رفع ادمن": bot.promote_chat_member(m.chat.id,t,can_delete_messages=True,can_pin_messages=True,can_invite_users=True); bot.reply_to(m,"✅ تم رفع ادمن")
    else: bot.promote_chat_member(m.chat.id,t); bot.reply_to(m,"❌ تم تنزيل ادمن")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="تثبيت" and is_admin(m) and m.reply_to_message)
def pin(m): bot.pin_chat_message(m.chat.id,m.reply_to_message.message_id); bot.reply_to(m,"📌 تم التثبيت")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="الغاء التثبيت" and is_admin(m))
def unpin(m): bot.unpin_chat_message(m.chat.id); bot.reply_to(m,"📌 تم الغاء التثبيت")

# ===== M5 الرفع =====
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text.startswith("رفع ") and is_admin(m))
def up_rank(m):
    if not m.reply_to_message: return bot.reply_to(m,"❌ رد على الشخص")
    t=m.reply_to_message.from_user.id
    rank=m.text.replace("رفع ","")
    ranks[f"{m.chat.id}_{t}"]=rank; save_data()
    bot.reply_to(m,f"⭐ تم رفع {m.reply_to_message.from_user.first_name} الى {rank}")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text.startswith("تنزيل ") and is_admin(m))
def down_rank(m):
    if not m.reply_to_message: return bot.reply_to(m,"❌ رد على الشخص")
    t=m.reply_to_message.from_user.id
    ranks[f"{m.chat.id}_{t}"]="عضو"; save_data()
    bot.reply_to(m,f"❌ تم تنزيل {m.reply_to_message.from_user.first_name} الى عضو")

# ===== M6 التحشيش + الهمسات =====
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="نسبه الحب")
def love(m): bot.reply_to(m,f"❤️ نسبه الحب: {random.randint(70,100)}%")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="نسبه الغباء")
def stupid(m): bot.reply_to(m,f"🤡 نسبه الغباء: {random.randint(80,100)}%")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text in ["تاج","ملك","غبي"])
def fun(m): bot.reply_to(m,{"تاج":"🤴","ملك":"👑","غبي":"🤡"}[m.text])
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text.startswith("همسه ") and is_admin(m))
def whisper(m):
    if not m.reply_to_message: return bot.reply_to(m,"❌ رد على الشخص")
    t=m.reply_to_message.from_user.id
    whispers[f"{m.chat.id}_{t}"]=m.text.replace("همسه ",""); save_data()
    bot.reply_to(m,f"📩 تم ارسال همسه الى {m.reply_to_message.from_user.first_name}")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="الهمسات")
def show_whisper(m):
    key=f"{m.chat.id}_{m.from_user.id}"
    if key in whispers: bot.reply_to(m,f"📩 همستك: {whispers[key]}"); del whispers[key]; save_data()
    else: bot.reply_to(m,"❌ لا توجد همسات لك")

# ===== M10 القفل كامل =====
LOCK_LIST = ["الروابط","الصور","الفيديو","الملصقات","الصوت","الدردشه","المتحركه","البوتات","الكلايش","التكرار"]
@bot.message_handler(func=lambda m: m.chat.id in active_groups and (m.text.startswith("قفل ") or m.text.startswith("فتح ")) and is_admin(m))
def lock_all(m):
    locks.setdefault(m.chat.id,[]); txt = m.text.replace("قفل ","").replace("فتح ","")
    if m.text == "فتح الكل": locks[m.chat.id] = []; save_data(); return bot.reply_to(m,"🔓 تم فتح كل الاقفال")
    if txt not in LOCK_LIST: return bot.reply_to(m,"❌ القفل غير موجود")
    if "قفل" in m.text:
        if txt not in locks[m.chat.id]: locks[m.chat.id].append(txt); save_data()
        bot.reply_to(m,f"🔒 تم قفل {txt}")
    else:
        if txt in locks[m.chat.id]: locks[m.chat.id].remove(txt); save_data()
        bot.reply_to(m,f"🔓 تم فتح {txt}")
@bot.message_handler(func=lambda m: m.chat.id in active_groups)
def check(m):
    for i in locks.get(m.chat.id,[]):
        if i=="الروابط" and "http" in (m.text or "").lower(): bot.delete_message(m.chat.id,m.message_id)
        if i=="الصور" and m.content_type=="photo": bot.delete_message(m.chat.id,m.message_id)
        if i=="الفيديو" and m.content_type=="video": bot.delete_message(m.chat.id,m.message_id)
        if i=="الملصقات" and m.content_type=="sticker": bot.delete_message(m.chat.id,m.message_id)
        if i=="الصوت" and m.content_type=="voice": bot.delete_message(m.chat.id,m.message_id)
        if i=="المتحركه" and m.content_type=="animation": bot.delete_message(m.chat.id,m.message_id)
        if i=="الدردشه": bot.delete_message(m.chat.id,m.message_id)
        if i=="الكلايش" and len(m.text or "") > 400: bot.delete_message(m.chat.id,m.message_id)
        if i=="التكرار" and hasattr(check,'last') and check.last==m.text: bot.delete_message(m.chat.id,m.message_id)
    check.last=m.text

# ===== M3 المطورين =====
@bot.message_handler(func=lambda m: m.text.startswith("رفع مطور") and m.from_user.id==ADMIN_ID)
def updev(m): devs.add(m.reply_to_message.from_user.id); save_data(); bot.reply_to(m,"✅ تم رفع مطور")
@bot.message_handler(func=lambda m: m.text.startswith("تنزيل مطور") and m.from_user.id==ADMIN_ID)
def downdev(m): devs.discard(m.reply_to_message.from_user.id); save_data(); bot.reply_to(m,"❌ تم تنزيل مطور")

# ===== M4 الاعضاء =====
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="ايدي")
def id(m): rank=get_rank(m.chat.id,m.from_user.id); bot.reply_to(m,f"🆔 `{m.from_user.id}`\n👤 {m.from_user.first_name}\n⭐ الرتبه: {rank}")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="رتبتي")
def myrank(m): bot.reply_to(m,f"⭐ رتبتك: {get_rank(m.chat.id,m.from_user.id)}")

# ===== M7 المطور =====
@bot.message_handler(func=lambda m: m.text.startswith("اذاعه ") and is_dev(m.from_user.id))
def bc(m): broadcast(m)
@bot.message_handler(func=lambda m: m.text.startswith("حظر عام ") and is_dev(m.from_user.id))
def gban(m):
    try: uid=int(m.text.split()[2]); bot.kick_chat_member(m.chat.id,uid); bot.reply_to(m,f"⛔ تم حظر {uid} عام")
    except: bot.reply_to(m,"❌ خطأ")

# ===== M8 التسليه =====
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="زواج")
def marry(m): bot.reply_to(m,"💍 تم الزواج")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="طلاق")
def div(m): bot.reply_to(m,"💔 تم الطلاق")

# ===== M9 البنك =====
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="انشاء حساب")
def acc(m): uid=str(m.from_user.id);
    if uid in bank: return bot.reply_to(m,"❌ عندك حساب")
    bank[uid]=500; save_data(); bot.reply_to(m,"💳 تم انشاء حساب 500$")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="راتب")
def sal(m): uid=str(m.from_user.id);
    if uid not in bank: return bot.reply_to(m,"❌ سوي حساب")
    bank[uid]+=500; save_data(); bot.reply_to(m,"💸 +500$")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text=="فلوسي")
def money(m): uid=str(m.from_user.id); bot.reply_to(m,f"💰 رصيدك: {bank.get(uid,0)}$")

# ===== M11 التفعيل =====
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text.startswith("تفعيل ") and is_admin(m))
def on(m): toggles[f"{m.chat.id}_{m.text}"]=True; save_data(); bot.reply_to(m,f"✅ تم {m.text}")
@bot.message_handler(func=lambda m: m.chat.id in active_groups and m.text.startswith("تعطيل ") and is_admin(m))
def off(m): toggles[f"{m.chat.id}_{m.text}"]=False; save_data(); bot.reply_to(m,f"❌ تم {m.text}")

# ===== رسائل الخاص =====
@bot.message_handler(func=lambda m: not is_dev(m.from_user.id) and m.chat.type=='private')
def user_msg(m):
    if not PROTECTION: return
    txt = m.text or m.caption or f"[{m.content_type}]"
    bot.send_message(ADMIN_ID,f"⊱ 📩 رسالة\n⊱ من: {m.from_user.first_name}\n⊱ `{m.from_user.id}`\n⊱ {txt}")

print(f"{BOT_NAME} Started...")
bot.infinity_polling(none_stop=True)
