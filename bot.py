import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import json
import os
import random
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

DEVELOPER_ID = 7488375443
CHANNEL_ID = -1003712880955
CHANNEL_LINK = "https://t.me/eeecxu"

DATA_FILE = "data.json"
try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: 
        data = json.load(f)
except:
    data = {"devs": [DEVELOPER_ID], "owners": {}, "active_groups": [], "locks": {}}

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
        data["active_groups"].append(chat_id)
        save()
        bot.send_message(chat_id, f"تم تعيين {message.from_user.first_name} كمالك للمجموعة ✅")

# ===== ازرار القائمة =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cid = call.message.chat.id
    mid = call.message_id
    
    if call.data == "main_menu":
        bot.edit_message_text("أهلاً بك في Tia 🤖\nاختر القسم:", cid, mid, reply_markup=main_menu_keyboard())
    
    elif call.data == "m1":
        txt = "👮 **أوامر الإدارة**\n\n/حظر @الرد\n/طرد @الرد\n/كتم @الرد 5د\n/الغاء_الكتم @الرد"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button())
    elif call.data == "m2":
        txt = "⚙️ **أوامر الإعدادات**\n\n/وضع_الرابط\n/الترحيب رسالتك"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button())
    elif call.data == "m3":
        txt = "🔒 **أوامر القفل**\n\n/قفل_الصور\n/قفل_الروابط\n/قفل_الملصقات\n/فتح_الكل"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button())
    elif call.data == "m4":
        if call.from_user.id == DEVELOPER_ID:
            txt = "💻 **لوحة المطور**\n\n/اذاعة رسالتك\n/احصائيات\n/حظر_عام @id"
            bot.edit_message_text(txt, cid, mid, reply_markup=back_button())
        else:
            bot.answer_callback_query(call.id, "❌ هذا الأمر للمطور فقط")
    elif call.data == "m5":
        txt = "🎯 **أوامر التسلية**\n\n/نكتة\n/توقع\n/لعبة"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button())
    elif call.data == "m6":
        txt = "🛠️ **الأوامر الخدمية**\n\n/ايدي\n/معلومات\n/القناة"
        bot.edit_message_text(txt, cid, mid, reply_markup=back_button())

# ===== م1: اوامر الادارة =====
@bot.message_handler(commands=['حظر'])
def ban(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    user_id = message.reply_to_message.from_user.id
    bot.ban_chat_member(message.chat.id, user_id)
    bot.reply_to(message, "✅ تم الحظر")

@bot.message_handler(commands=['طرد'])
def kick(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    user_id = message.reply_to_message.from_user.id
    bot.ban_chat_member(message.chat.id, user_id)
    bot.unban_chat_member(message.chat.id, user_id)
    bot.reply_to(message, "✅ تم الطرد")

@bot.message_handler(commands=['كتم'])
def mute(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    user_id = message.reply_to_message.from_user.id
    bot.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
    bot.reply_to(message, "✅ تم الكتم")

@bot.message_handler(commands=['الغاء_الكتم'])
def unmute(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    if not message.reply_to_message: return bot.reply_to(message, "رد على العضو")
    user_id = message.reply_to_message.from_user.id
    bot.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=True))
    bot.reply_to(message, "✅ تم فك الكتم")

# ===== م3: اوامر القفل =====
@bot.message_handler(commands=['قفل_الصور'])
def lock_photo(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    data["locks"][str(message.chat.id)] = data["locks"].get(str(message.chat.id), {})
    data["locks"][str(message.chat.id)]["photo"] = True
    save()
    bot.reply_to(message, "✅ تم قفل الصور")

@bot.message_handler(commands=['قفل_الروابط'])
def lock_link(message):
    if not is_admin(message.from_user.id, message.chat.id): return
    data["locks"][str(message.chat.id)] = data["locks"].get(str(message.chat.id), {})
    data["locks"][str(message.chat.id)]["link"] = True
    save()
    bot.reply_to(message, "✅ تم قفل الروابط")

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
        if message.content_type == 'photo' and data["locks"][chat_id].get("photo"):
            bot.delete_message(chat_id, message.message_id)
        if message.content_type == 'text' and 'http' in message.text and data["locks"][chat_id].get("link"):
            bot.delete_message(chat_id, message.message_id)
        if message.content_type == 'sticker' and data["locks"][chat_id].get("sticker"):
            bot.delete_message(chat_id, message.message_id)

# ===== م4: اوامر المطور =====
@bot.message_handler(commands=['اذاعة'])
def broadcast(message):
    if message.from_user.id != DEVELOPER_ID: return
    msg = message.text.replace('/اذاعة ', '')
    for gid in data["active_groups"]:
        try: bot.send_message(gid, f"📢 اذاعة من المطور:\n\n{msg}")
        except: pass
    bot.reply_to(message, "✅ تمت الاذاعة")

@bot.message_handler(commands=['احصائيات'])
def stats(message):
    if message.from_user.id != DEVELOPER_ID: return
    bot.reply_to(message, f"📊 الاحصائيات:\nالمجموعات: {len(data['active_groups'])}\nالمطورين: {len(data['devs'])}")

# ===== م5: اوامر التسلية =====
jokes = ["واحد محش دخل الامتحان...","مرة واحد بخيل اتصل بالاسعاف..."]
@bot.message_handler(commands=['نكتة'])
def joke(message):
    bot.reply_to(message, random.choice(jokes))

# ===== م6: اوامر خدمية =====
@bot.message_handler(commands=['ايدي'])
def my_id(message):
    bot.reply_to(message, f"🆔 ايديك: {message.from_user.id}\nايدي القروب: {message.chat.id}")

print("Tia شغال للمطور", DEVELOPER_ID)
bot.polling(none_stop=True)
