from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json, os, sys
import menu

FILE_DEV = 'dev.json'
FILE_BROADCAST = 'broadcast.json'
FILE_SETTINGS = 'settings.json'

DEVS = [7488375443]

devs = []
gban_list = {}
gmute_list = {}
broadcast_status = {'groups': []}
settings = {}

def load_dev_data():
    global devs, gban_list, gmute_list, broadcast_status, settings
    for f, data in [(FILE_DEV, []), (FILE_BROADCAST, {'groups': []}), (FILE_SETTINGS, {})]:
        if not os.path.exists(f):
            with open(f, 'w', encoding='utf-8') as file: json.dump(data, file)
    devs = json.load(open(FILE_DEV, 'r', encoding='utf-8'))
    gban_list = json.load(open('gban.json', 'r', encoding='utf-8'))
    gmute_list = json.load(open('gmute.json', 'r', encoding='utf-8'))
    broadcast_status = json.load(open(FILE_BROADCAST, 'r', encoding='utf-8'))
    settings = json.load(open(FILE_SETTINGS, 'r', encoding='utf-8'))

def save_dev_data():
    with open(FILE_DEV, 'w', encoding='utf-8') as f: json.dump(devs, f)
    with open('gban.json', 'w', encoding='utf-8') as f: json.dump(gban_list, f)
    with open('gmute.json', 'w', encoding='utf-8') as f: json.dump(gmute_list, f)
    with open(FILE_BROADCAST, 'w', encoding='utf-8') as f: json.dump(broadcast_status, f)
    with open(FILE_SETTINGS, 'w', encoding='utf-8') as f: json.dump(settings, f)

load_dev_data()

def dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("اذاعة"), KeyboardButton("قائمه العام"))
    markup.add(KeyboardButton("مسح المحظورين عام"), KeyboardButton("اعاده تشغيل"))
    markup.add(KeyboardButton("رجوع للقائمة"))
    return markup

def is_dev(user_id): return user_id in DEVS or str(user_id) in devs

def register_handlers(bot):

    # لازم يكون اول واحد
    @bot.message_handler(func=lambda m: m.chat.type == 'private' and is_dev(m.from_user.id))
    def dev_keyboard_commands(m):
        txt = m.text
        if txt == "اذاعة":
            msg = bot.send_message(m.chat.id, "ارسل الاذاعة")
            bot.register_next_step_handler(msg, lambda x: broadcast_msg(bot, x))
        elif txt == "قائمه العام":
            bot.send_message(m.chat.id, f"🚫 {len(gban_list)} | 🔇 {len(gmute_list)}", reply_markup=dev_keyboard())
        elif txt == "مسح المحظورين عام":
            gban_list.clear(); gmute_list.clear(); save_dev_data()
            bot.send_message(m.chat.id, "✅ تم المسح", reply_markup=dev_keyboard())
        elif txt == "اعاده تشغيل":
            bot.send_message(m.chat.id, "🔄"); os.execl(sys.executable, sys.executable, *sys.argv)
        elif txt == "رجوع للقائمة":
            menu.show_menu(bot, m.chat.id)

    @bot.message_handler(commands=['start'])
    def start_pm(m):
        if m.chat.type == 'private' and is_dev(m.from_user.id):
            bot.send_message(m.chat.id, "مرحبا المطور", reply_markup=dev_keyboard())

    def broadcast_msg(bot, m):
        count = 0
        for chat_id in broadcast_status.get('groups', []):
            try: bot.send_message(chat_id, m.text); count += 1
            except: pass
        bot.send_message(m.chat.id, f"✅ تم الارسال لـ {count}", reply_markup=dev_keyboard())
