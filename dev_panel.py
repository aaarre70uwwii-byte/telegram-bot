# dev_panel.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import os, sys, json

DEV_ID = 7488375443

# ملفات التخزين
DB_FILE = 'dev_db.json'

def load_db():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {"gban": [], "gmute": [], "bot_name": "بوت الخدمي", "channel": "", "welcome": "", "devs": [DEV_ID], "service": True, "contact": True, "replies": {}}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)

db = load_db()

def is_dev(user_id):
    return user_id in db["devs"]

def dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton("أعدادات ألبوت"), KeyboardButton("قائمة ألعام"))
    markup.row(KeyboardButton("تغير المطور الاساسي"), KeyboardButton("أضف رد عام"))
    markup.row(KeyboardButton("تغير أسم البوت"), KeyboardButton("مسح رد عام"))
    markup.row(KeyboardButton("تفعيل ألبوت"), KeyboardButton("تحديث الملفات"))
    markup.row(KeyboardButton("أضف الترحيب نص+بصوره"), KeyboardButton("جلب ألنسخه الأحتياطيه"))
    markup.row(KeyboardButton("تعطيل البوت ألخدمي"), KeyboardButton("تفعيل البوت ألخدمي"))
    markup.row(KeyboardButton("تعطيل التواصل"), KeyboardButton("تفعيل التواصل"))
    markup.row(KeyboardButton("الاحصايات"), KeyboardButton("الاذاعه خاص+مجموعات"))
    markup.row(KeyboardButton("ألمطورين"), KeyboardButton("تغير قناه البوت"))
    markup.row(KeyboardButton("اخفاء قائمة البوت"), KeyboardButton("المساعد"))
    return markup

def register_dev_handlers(bot):
    temp = {} # لتخزين الحالات

    @bot.message_handler(commands=['start'])
    def start_pm(m):
        if m.chat.type == 'private' and is_dev(m.from_user.id):
            bot.send_message(m.chat.id, "مرحبا المطور 👑\nاهلا بك في لوحة التحكم", reply_markup=dev_keyboard())

    @bot.message_handler(func=lambda m: m.chat.type == 'private' and is_dev(m.from_user.id))
    def dev_panel(m):
        txt = m.text
        cid = m.chat.id

        # 1
        if txt == "أعدادات ألبوت":
            msg = f"📜 اعدادات البوت:\n- اسم البوت: {db['bot_name']}\n- قناة البوت: @{db['channel']}\n- البوت الخدمي: {'مفعل' if db['service'] else 'معطل'}\n- التواصل: {'مفعل' if db['contact'] else 'معطل'}\n- المطورين: {len(db['devs'])}"
            bot.send_message(cid, msg, reply_markup=dev_keyboard())

        # 2
        elif txt == "قائمة ألعام":
            msg = f"🚫 محظورين عام: {len(db['gban'])}\n🔇 مكتومين عام: {len(db['gmute'])}"
            bot.send_message(cid, msg, reply_markup=dev_keyboard())

        # 3
        elif txt == "تغير المطور الاساسي":
            msg = bot.send_message(cid, "ارسل ايدي المطور الجديد")
            bot.register_next_step_handler(msg, set_dev)

        # 4
        elif txt == "أضف رد عام":
            msg = bot.send_message(cid, "ارسل الكلمة")
            bot.register_next_step_handler(msg, get_reply_key)

        # 5
        elif txt == "مسح رد عام":
            msg = bot.send_message(cid, "ارسل الكلمة اللي تريد مسحها")
            bot.register_next_step_handler(msg, del_reply)

        # 6
        elif txt == "تغير أسم البوت":
            msg = bot.send_message(cid, "ارسل الاسم الجديد للبوت")
            bot.register_next_step_handler(msg, set_name)

        # 7
        elif txt == "تفعيل ألبوت":
            bot.send_message(cid, "✅ تم تفعيل البوت", reply_markup=dev_keyboard())

        # 8
        elif txt == "تحديث الملفات":
            global db; db = load_db()
            bot.send_message(cid, "✅ تم تحديث الملفات واعادة تحميل قاعدة البيانات", reply_markup=dev_keyboard())

        # 9
        elif txt == "أضف الترحيب نص+بصوره":
            msg = bot.send_message(cid, "ارسل رسالة الترحيب")
            bot.register_next_step_handler(msg, set_welcome)

        # 10
        elif txt == "جلب ألنسخه الأحتياطيه":
            if os.path.exists(DB_FILE):
                with open(DB_FILE, 'rb') as f: bot.send_document(cid, f, caption="📦 النسخة الاحتياطية", reply_markup=dev_keyboard())
            else: bot.send_message(cid, "لا يوجد نسخة", reply_markup=dev_keyboard())

        # 11
        elif txt == "تعطيل البوت ألخدمي":
            db["service"] = False; save_db(db)
            bot.send_message(cid, "⛔️ تم تعطيل البوت الخدمي", reply_markup=dev_keyboard())

        # 12
        elif txt == "تفعيل البوت ألخدمي":
            db["service"] = True; save_db(db)
            bot.send_message(cid, "✅ تم تفعيل البوت الخدمي", reply_markup=dev_keyboard())

        # 13
        elif txt == "تعطيل التواصل":
            db["contact"] = False; save_db(db)
            bot.send_message(cid, "⛔️ تم تعطيل التواصل", reply_markup=dev_keyboard())

        # 14
        elif txt == "تفعيل التواصل":
            db["contact"] = True; save_db(db)
            bot.send_message(cid, "✅ تم تفعيل التواصل", reply_markup=dev_keyboard())

        # 15
        elif txt == "الاحصايات":
            msg = f"📊 الاحصائيات:\nالمطورين: {len(db['devs'])}\nالمحظورين: {len(db['gban'])}\nالمكتومين: {len(db['gmute'])}\nالردود: {len(db['replies'])}"
            bot.send_message(cid, msg, reply_markup=dev_keyboard())

        # 16
        elif txt == "الاذاعه خاص+مجموعات":
            msg = bot.send_message(cid, "📢 ارسل الان الاذاعة للكل")
            bot.register_next_step_handler(msg, broadcast)

        # 17
        elif txt == "ألمطورين":
            devs = '\n'.join([str(i) for i in db['devs']])
            bot.send_message(cid, f"👑 قائمة المطورين:\n{devs}", reply_markup=dev_keyboard())

        # 18
        elif txt == "تغير قناه البوت":
            msg = bot.send_message(cid, "ارسل يوزر القناة بدون @")
            bot.register_next_step_handler(msg, set_channel)

        # 19
        elif txt == "اخفاء قائمة البوت":
            bot.send_message(cid, "✅ تم اخفاء القائمة", reply_markup=ReplyKeyboardRemove())

        # 20
        elif txt == "المساعد":
            bot.send_message(cid, "🤖 اوامر المساعد كلها من الازرار\nاختر من القائمة", reply_markup=dev_keyboard())

    # دوال الخطوات التالية
    def set_dev(m):
        try:
            db["devs"] = [int(m.text)]; save_db(db)
            bot.send_message(m.chat.id, f"✅ تم تغير المطور الى: {m.text}", reply_markup=dev_keyboard())
        except: bot.send_message(m.chat.id, "❌ ايدي غلط", reply_markup=dev_keyboard())

    def get_reply_key(m):
        temp[m.chat.id] = {"key": m.text}
        msg = bot.send_message(m.chat.id, "الان ارسل الرد")
        bot.register_next_step_handler(msg, save_reply)

    def save_reply(m):
        key = temp[m.chat.id]["key"]
        db["replies"][key] = m.text; save_db(db)
        bot.send_message(m.chat.id, f"✅ تم حفظ الرد على: {key}", reply_markup=dev_keyboard())

    def del_reply(m):
        if m.text in db["replies"]:
            del db["replies"][m.text]; save_db(db)
            bot.send_message(m.chat.id, f"✅ تم مسح الرد: {m.text}", reply_markup=dev_keyboard())
        else: bot.send_message(m.chat.id, "❌ الكلمة غير موجودة", reply_markup=dev_keyboard())

    def set_name(m):
        db["bot_name"] = m.text; save_db(db)
        bot.send_message(m.chat.id, f"✅ تم تغير اسم البوت الى: {m.text}", reply_markup=dev_keyboard())

    def set_channel(m):
        db["channel"] = m.text; save_db(db)
        bot.send_message(m.chat.id, f"✅ تم تغير قناة البوت الى: @{m.text}", reply_markup=dev_keyboard())

    def set_welcome(m):
        db["welcome"] = m.text; save_db(db)
        bot.send_message(m.chat.id, "✅ تم حفظ رسالة الترحيب", reply_markup=dev_keyboard())

    def broadcast(m):
        bot.send_message(m.chat.id, f"✅ تم استلام الاذاعة\nنص: {m.text}\nملاحظة: اربطها بقائمة المجموعات عندك", reply_markup=dev_keyboard())

# في ملفك الرئيسي m5.py استدعيها كذا:
# from dev_panel import register_dev_handlers
# register_dev_handlers(bot)
