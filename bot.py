import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import json
import os
import random
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    print("ERROR: BOT_TOKEN not found in Variables!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

DEVELOPER_ID = 7488375443
CHANNEL_ID = -1003712880955
CHANNEL_LINK = "https://t.me/eeecxu"

DATA_FILE = "data.json"
# انشاء الملف لو مش موجود
try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"devs": [DEVELOPER_ID], "owners": {}, "active_groups": [], "locks": {}}
    save()

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_admin(user_id, chat_id):
    if user_id == DEVELOPER_ID: return True
    if str(chat_id) in data["owners"] and user_id == data["owners"][str(chat_id)]: return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except: return False

# ===== الكيبورد =====
def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("👮 أوامر الإدارة (م1)", callback_data="m1"),
               InlineKeyboardButton("⚙️ أوامر الإعدادات (م2)", callback_data="m2"))
    markup.row(InlineKeyboardButton("🔒 أوامر القفل (م3)", callback_data="m3"),
               InlineKeyboardButton("💻 أوامر المطور (م4)", callback_data="m4"))
    markup.row(InlineKeyboardButton("🎯 أوامر التسلية (م5)", callback_data="m5"),
               InlineKeyboardButton("🛠️ الأوامر الخدمية (م6)", callback_data="m6"))
    markup.row(InlineKeyboardButton("📢 قناة التحديثات", url=CHANNEL_LINK))
    return markup

def back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu"))
    return markup

# ===== اوامر البداية =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "أهلاً بك في بوت Tia 🤖\nاختر القسم اللي تريده:", reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['channel', 'قناه'])
def send_channel(message):
    bot.send_message(message.chat.id, f"📢 قناة تحديثات البوت:\n{CHANNEL_LINK}")

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    chat_id = message.chat.id
    if str(chat_id) not in data["owners"]:
        data["owners"][str(chat_id)] = message.from_user.id
    if chat_id not in data["active_groups"]: # تم التعديل هنا
        data["active_groups"].append(chat_id)
        save()
        bot.send_message(chat_id, f"تم تعيين {message.from_user.first_name} كمالك للمجموعة ✅")

# ===== ازرار القائمة =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)
    if not call.message: return

    cid = call.message.chat.id
    mid = call.message.message_id

    if call.data == "main_menu":
        bot.edit_message_text("أهلاً بك في Tia 🤖\nاختر القسم:", cid, mid, reply_markup=main_menu_keyboard())
    elif call.data == "m1":
        txt = "👮 **أوامر الإدارة**\n\n`/حظر` بالرد\n`/طرد` بالرد\n`/كتم` بالرد\n`/الغاء_الكتم` بالرد"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button(), parse_mode="Markdown")
    elif call.data == "m2":
        txt = "⚙️ **أوامر الإعدادات**\n\n`/وضع_الرابط`\n`/الترحيب` رسالتك"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button(), parse_mode="Markdown")
    elif call.data == "m3":
        txt = "🔒 **أوامر القفل**\n\n`/قفل_الصور`\n`/قفل_الروابط`\n`/قفل_الملصقات`\n`/فتح_الكل`"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button(), parse_mode="Markdown")
    elif call.data == "m4":
        if call.from_user.id == DEVELOPER_ID:
            txt = "💻 **لوحة المطور**\n\n`/اذاعة` رسالتك\n`/احصائيات`"
            bot.edit_message_text(txt, cid, mid, reply_markup=back_button(), parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ هذا الأمر للمطور فقط", show_alert=True)
    elif call.data == "m5":
        txt = "🎯 **أوامر التسلية**\n\n`/نكتة`"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button(), parse_mode="Markdown")
    elif call.data == "m6":
        txt = "🛠️ **الأوامر الخدمية**\n\n`/ايدي`\n`/القناة`"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button(), parse_mode="Markdown")

# ===== م1: اوامر الادارة =====
@bot.message_handler(commands=['حظر'])
def ban(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    try:
        bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.reply_to(message, "✅ تم الحظر")
    except: bot.reply_to(message, "❌ ما اقدر احظر. تأكد اني ادمن")

@bot.message_handler(commands=['طرد'])
def kick(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    try:
        uid = message.reply_to_message.from_user.id
        bot.ban_chat_member(message.chat.id, uid)
        bot.unban_chat_member(message.chat.id, uid)
        bot.reply_to(message, "✅ تم الطرد")
    except: bot.reply_to(message, "❌ ما اقدر اطرد. تأكد اني ادمن")

@bot.message_handler(commands=['كتم'])
def mute(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    try:
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, ChatPermissions(can_send_messages=False))
        bot.reply_to(message, "✅ تم الكتم")
    except: bot.reply_to(message, "❌ ما اقدر اكتم. تأكد اني ادمن")

@bot.message_handler(commands=['الغاء_الكتم'])
def unmute(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    try:
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, ChatPermissions(can_send_messages=True))
        bot.reply_to(message, "✅ تم فك الكتم")
    except: bot.reply_to(message, "❌ ما اقدر افك الكتم. تأكد اني ادمن")

# ===== م3: اوامر القفل =====
@bot.message_handler(commands=['قفل_الصور', 'قفل_الروابط', 'قفل_الملصقات'])
def lock_cmd(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    cmd = message.text.replace('/', '').replace('قفل_', '')
    data["locks"][str(message.chat.id)] = data["locks"].get(str(message.chat.id), {})
    data["locks"][str(message.chat.id)][cmd] = True
    save()
    bot.reply_to(message, f"✅ تم قفل {cmd}")

@bot.message_handler(commands=['فتح_الكل'])
def unlock_all(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    data["locks"][str(message.chat.id)] = {}
    save()
    bot.reply_to(message, "✅ تم فتح كل شي")

@bot.message_handler(content_types=['photo', 'text', 'sticker'])
def check_locks(message):
    chat_id = str(message.chat.id)
    if chat_id in data["locks"]:
        try:
            if message.content_type == 'photo' and data["locks"][chat_id].get("photo"): bot.delete_message(chat_id, message.message_id)
            if message.content_type == 'text' and message.text and 'http' in message.text and data["locks"][chat_id].get("link"): bot.delete_message(chat_id, message.message_id)
            if message.content_type == 'sticker' and data["locks"][chat_id].get("sticker"): bot.delete_message(chat_id, message.message_id)
        except: pass

# ===== م4: اوامر المطور =====
@bot.message_handler(commands=['اذاعة'])
def broadcast(message):
    if message.from_user.id!= DEVELOPER_ID: return
    msg = message.text.replace('/اذاعة ', '', 1)
    count = 0
    for gid in data["active_groups"]:
        try: bot.send_message(gid, f"📢 اذاعة من المطور:\n\n{msg}"); count += 1
        except: pass
    bot.reply_to(message, f"✅ تمت الاذاعة لـ {count} مجموعة")

@bot.message_handler(commands=['احصائيات'])
def stats(message):
    if message.from_user.id!= DEVELOPER_ID: return
    bot.reply_to(message, f"📊 الاحصائيات:\nالمجموعات: {len(data['active_groups'])}\nالمطورين: {len(data['devs'])}")

# ===== م5: اوامر التسلية =====
jokes = ["واحد محش دخل الامتحان...","مرة واحد بخيل اتصل بالاسعاف...","محش سألوه 2+2 كم؟ قال 22"]
@bot.message_handler(commands=['نكتة'])
def joke(message):
    bot.reply_to(message, random.choice(jokes))

# ===== م6: اوامر خدمية =====
@bot.message_handler(commands=['ايدي'])
def my_id(message):
    bot.reply_to(message, f"🆔 ايديك: `{message.from_user.id}`\nايدي القروب: `{message.chat.id}`", parse_mode="Markdown")

print("Tia شغال للمطور", DEVELOPER_ID)
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
