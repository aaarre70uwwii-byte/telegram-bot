import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import json, os, random, time, re

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

DEVELOPER_ID = 7488375443 # ايديك
CHANNEL_LINK = "https://t.me/eeecxu"
DATA_FILE = "data.json"

# تحميل البيانات
try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except:
    data = {"owners": {}, "active_groups": [], "locks": {}, "whispers": {}, "banned_words": {}}

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def is_admin(user_id, chat_id):
    if user_id == DEVELOPER_ID: return True
    if str(chat_id) in data["owners"] and user_id == data["owners"][str(chat_id)]: return True
    try: return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
    except: return False

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("👮 الادارة", callback_data="m1"), InlineKeyboardButton("⚙️ الاعدادات", callback_data="m2"))
    markup.row(InlineKeyboardButton("🔒 القفل", callback_data="m3"), InlineKeyboardButton("💻 المطور", callback_data="m4"))
    markup.row(InlineKeyboardButton("📢 القناة", url=CHANNEL_LINK))
    return markup

# ===== اوامر التفعيل =====
@bot.message_handler(commands=['تفعيل', 'activate'])
def activate(message):
    if message.chat.type in ['group','supergroup']:
        if message.chat.id not in data["active_groups"]:
            data["active_groups"].append(message.chat.id)
            data["owners"][str(message.chat.id)] = message.from_user.id # صاحب القروب
            save()
            bot.reply_to(message, "✅ تم التفعيل بنجاح\nانا Tia تحت امركم")
        else:
            bot.reply_to(message, "⚠️ البوت مفعل من قبل")

@bot.message_handler(commands=['تعطيل', 'deactivate'])
def deactivate(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if message.chat.id in data["active_groups"]:
        data["active_groups"].remove(message.chat.id)
        if str(message.chat.id) in data["owners"]: del data["owners"][str(message.chat.id)]
        save()
    bot.reply_to(message, "❌ تم تعطيل البوت من هذه المجموعة")

# ===== امر المغادرة للمطور =====
@bot.message_handler(commands=['غادر', 'leave'])
def leave(message):
    if message.from_user.id!= DEVELOPER_ID: return
    if message.chat.type in ['group','supergroup']:
        bot.reply_to(message, "غادرت بامر من المطور 👋")
        time.sleep(1)
        bot.leave_chat(message.chat.id)
        if message.chat.id in data["active_groups"]: data["active_groups"].remove(message.chat.id); save()

# ===== اوامر الرفع والايدي بالصورة للمطور =====
@bot.message_handler(commands=['رفع', 'promote'])
def promote_dev(message):
    if message.from_user.id!= DEVELOPER_ID: return bot.reply_to(message, "❌ للمطور فقط")
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    uid = message.reply_to_message.from_user.id
    data["owners"][str(message.chat.id)] = uid; save()
    bot.reply_to(message, f"✅ تم رفع {message.reply_to_message.from_user.first_name} مالك للمجموعة")

@bot.message_handler(commands=['ايدي', 'id'])
def id_photo(message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/photos/placeholder.jpg" # صورة افتراضية
    try:
        user_photos = bot.get_user_profile_photos(user.id, limit=1)
        if user_photos.total_count > 0:
            file_id = user_photos.photos[0][0].file_id
            caption = f"👤 الاسم: {user.first_name}\n🆔 الايدي: `{user.id}`\n@username: @{user.username or 'لا يوجد'}"
            bot.send_photo(message.chat.id, file_id, caption=caption)
        else:
            bot.reply_to(message, f"👤 الاسم: {user.first_name}\n🆔 الايدي: `{user.id}`\n@username: @{user.username or 'لا يوجد'}")
    except:
        bot.reply_to(message, f"👤 الاسم: {user.first_name}\n🆔 الايدي: `{user.id}`")

# ===== باقي الاوامر =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "مرحبا بك في بوت *Tia* 🤖\nاستخدم /تفعيل في القروب", reply_markup=main_menu())

@bot.message_handler(commands=['ban', 'kick', 'mute', 'unmute'])
def admin_cmds(message):
    if not is_admin(message.from_user.id, message.chat.id): return bot.reply_to(message, "❌ انت مش ادمن")
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    uid = message.reply_to_message.from_user.id
    cmd = message.text.split()[0].replace('/', '')
    try:
        if cmd == 'ban': bot.ban_chat_member(message.chat.id, uid); bot.reply_to(message, "✅ تم الحظر")
        elif cmd == 'kick': bot.ban_chat_member(message.chat.id, uid); bot.unban_chat_member(message.chat.id, uid); bot.reply_to(message, "✅ تم الطرد")
        elif cmd == 'mute': bot.restrict_chat_member(message.chat.id, uid, ChatPermissions()); bot.reply_to(message, "✅ تم الكتم")
        elif cmd == 'unmute': bot.restrict_chat_member(message.chat.id, uid, ChatPermissions(can_send_messages=True)); bot.reply_to(message, "✅ تم فك الكتم")
    except: bot.reply_to(message, "❌ فشلت. تأكد اني ادمن")

@bot.message_handler(commands=['همسه'])
def whisper(message):
    try:
        _, target, *msg = message.text.split()
        data["whispers"][target] = " ".join(msg); save()
        bot.reply_to(message, f"✅ تم ارسال همسة الى {target}. قله يرسل /قرا")
    except: bot.reply_to(message, "الاستخدام: /همسه @اليوزر النص")

@bot.message_handler(commands=['قرا'])
def read_whisper(message):
    user = f"@{message.from_user.username}"
    if user in data["whispers"]:
        bot.reply_to(message, f"📩 همستك: {data['whispers'][user]}")
        del data["whispers"][user]; save()
    else: bot.reply_to(message, "ماعندك همسات")

@bot.message_handler(commands=['stats', 'broadcast'])
def dev(message):
    if message.from_user.id!= DEVELOPER_ID: return
    if message.text.startswith('/broadcast'):
        msg = message.text.replace('/broadcast ', '', 1)
        count = 0
        for gid in data["active_groups"]:
            try: bot.send_message(gid, f"📢 *اذاعة من المطور*\n\n{msg}"); count += 1; time.sleep(0.1)
            except: pass
        bot.reply_to(message, f"✅ تمت الاذاعة لـ {count} مجموعة")
    elif message.text == '/stats':
        bot.reply_to(message, f"📊 *احصائيات Tia:*\nالمجموعات: `{len(data['active_groups'])}`")

print(f"Tia v3.0 اشتغل. المطور: {DEVELOPER_ID}")
bot.infinity_polling()
@bot.message_handler(commands=['حضر'])
def ban(m):
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص اللي تريد تحضره")
    bot.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    bot.reply_to(m, f"🚫 تم حظر {m.reply_to_message.from_user.first_name}")

@bot.message_handler(commands=['طرد'])
def kick(m):
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص اللي تريد تطرده")
    bot.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    bot.unban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    bot.reply_to(m, f"👢 تم طرد {m.reply_to_message.from_user.first_name}")

@bot.message_handler(commands=['كتم'])
def mute(m):
    if not m.reply_to_message: return bot.reply_to(m, "رد على الشخص اللي تريد تكتمه")
    bot.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, can_send_messages=False)
    bot.reply_to(m, f"🔇 تم كتم {m.reply_to_message.from_user.first_name}")
