import json
import os
import telebot

DB_FILE = 'group_db.json'
SETTINGS_FILE = 'group_settings.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_chat_data(chat_id):
    db = load_db()
    chat_id = str(chat_id)
    if chat_id not in db:
        db[chat_id] = {"owner": None, "admins": [], "mods": [], "vip": [], "banned": [], "muted": []}
        save_db(db) # اضفت الحفظ هنا
    return db, db[chat_id]

def get_chat_settings(chat_id):
    settings = load_settings()
    chat_id = str(chat_id)
    if chat_id not in settings:
        settings[chat_id] = {"link": None, "welcome": "اهلا بك", "rules": "لا يوجد", "channel": None, "download": True}
        save_settings(settings) # اضفت الحفظ هنا
    return settings, settings[chat_id]

def is_admin(bot, chat_id, user_id):
    try: return bot.get_chat_member(chat_id, user_id).status in ['creator', 'administrator']
    except: return False

def register_m2_handlers(bot):
    @bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
    def m2_handler(m):
        txt = m.text.strip() if m.text else ""
        if not txt: return
        chat_id, user_id = m.chat.id, m.from_user.id
        db, data = get_chat_data(chat_id)
        settings, s = get_chat_settings(chat_id)
        if not is_admin(bot, chat_id, user_id): return

        # رؤية
        if txt == "الرابط": bot.reply_to(m, f"🔗 {s.get('link') or 'لا يوجد رابط محفوظ'}")
        elif txt == "المالكين الاساسين": bot.reply_to(m, f"👑 {data.get('owner') or 'لا يوجد'}")
        elif txt == "الادمنيه": bot.reply_to(m, f"👨‍💼 عدد الادمنيه: {len(data.get('admins',[]))}")
        elif txt == "المدراء": bot.reply_to(m, f"👮 عدد المدراء: {len(data.get('mods',[]))}")
        elif txt == "المميزين": bot.reply_to(m, f"⭐ عدد المميزين: {len(data.get('vip',[]))}")
        elif txt == "المحظورين": bot.reply_to(m, f"⛔️ عدد المحظورين: {len(data.get('banned',[]))}")
        elif txt == "المكتومين": bot.reply_to(m, f"🔇 عدد المكتومين: {len(data.get('muted',[]))}")
        elif txt == "القوانين": bot.reply_to(m, f"📜 القوانين:\n{s.get('rules')}")
        elif txt == "الترحيب": bot.reply_to(m, f"👋 رسالة الترحيب:\n{s.get('welcome')}")
        elif txt == "معلوماتي": bot.reply_to(m, f"🆔 الاسم: {m.from_user.first_name}\n🆔 الايدي: `{user_id}`", parse_mode="Markdown")
        elif txt == "المجموعه": bot.reply_to(m, f"👥 اسم المجموعه: {bot.get_chat(chat_id).title}\n🆔 ايدي المجموعه: `{chat_id}`", parse_mode="Markdown")

        # وضع
        elif txt.startswith("اضف رابط"):
            parts = txt.split(" ", 2)
            if len(parts) < 3: bot.reply_to(m,"❌ ارسل: اضف رابط + الرابط"); return
            s["link"]=parts[2]; save_settings(settings); bot.reply_to(m,"✅ تم حفظ الرابط")
        elif txt == "مسح الرابط": s["link"]=None; save_settings(settings); bot.reply_to(m,"✅ تم مسح الرابط")
        elif txt == "انشاء رابط":
            try:
                s["link"]=bot.export_chat_invite_link(chat_id); save_settings(settings); bot.reply_to(m,f"✅ تم انشاء الرابط:\n{s['link']}")
            except: bot.reply_to(m,"❌ فشلت. تأكد ان البوت ادمن وعنده صلاحية اضافة اعضاء")
        elif txt.startswith("ضع قوانين"): s["rules"]=txt.replace("ضع قوانين","",1).strip(); save_settings(settings); bot.reply_to(m,"✅ تم حفظ القوانين")
        elif txt.startswith("ضع الترحيب"): s["welcome"]=txt.replace("ضع الترحيب","",1).strip(); save_settings(settings); bot.reply_to(m,"✅ تم حفظ الترحيب")

        # تحميل
        elif txt == "تفعيل التحميل": s["download"]=True; save_settings(settings); bot.reply_to(m,"✅ تم تفعيل التحميل")
        elif txt == "تعطيل التحميل": s["download"]=False; save_settings(settings); bot.reply_to(m,"✅ تم تعطيل التحميل")
