import json
import os
import telebot
from telebot.types import ChatPermissions

DB_FILE = 'group_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_chat_data(chat_id):
    db = load_db()
    chat_id = str(chat_id)
    if chat_id not in db:
        db[chat_id] = {
            "owner": None, "admins": [], "mods": [], "vip": [],
            "banned": [], "muted": []
        }
    return db, db[chat_id]

def is_admin(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except:
        return False

def get_target(m):
    if m.reply_to_message:
        return m.reply_to_message.from_user.id
    return None

def register_m1_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
    def m1_handler(m):
        txt = m.text
        if not txt: return

        chat_id = m.chat.id
        user_id = m.from_user.id
        msg_id = m.message_id
        db, data = get_chat_data(chat_id)

        if not is_admin(bot, chat_id, user_id):
            return

        target = get_target(m)

        # ========== اوامر الرفع والتنزيل ==========
        if txt == "رفع مالك اساسي" and target:
            data["owner"] = target
            save_db(db)
            bot.reply_to(m, "✅ تم رفع العضو مالك اساسي")

        elif txt == "تنزيل مالك اساسي" and target:
            if data["owner"] == target: data["owner"] = None
            save_db(db)
            bot.reply_to(m, "✅ تم تنزيل العضو من مالك اساسي")

        elif txt == "رفع مالك" and target:
            data["owner"] = target
            save_db(db)
            bot.reply_to(m, "✅ تم رفع العضو مالك")

        elif txt == "تنزيل مالك" and target:
            if data["owner"] == target: data["owner"] = None
            save_db(db)
            bot.reply_to(m, "✅ تم تنزيل العضو من مالك")

        elif txt == "رفع مدير" and target:
            if target not in data["mods"]: data["mods"].append(target)
            save_db(db)
            bot.reply_to(m, "✅ تم رفع العضو مدير")

        elif txt == "تنزيل مدير" and target:
            if target in data["mods"]: data["mods"].remove(target)
            save_db(db)
            bot.reply_to(m, "✅ تم تنزيل العضو من مدير")

        elif txt == "رفع ادمن" and target:
            if target not in data["admins"]: data["admins"].append(target)
            save_db(db)
            bot.reply_to(m, "✅ تم رفع العضو ادمن")

        elif txt == "تنزيل ادمن" and target:
            if target in data["admins"]: data["admins"].remove(target)
            save_db(db)
            bot.reply_to(m, "✅ تم تنزيل العضو من ادمن")

        elif txt == "رفع مميز" and target:
            if target not in data["vip"]: data["vip"].append(target)
            save_db(db)
            bot.reply_to(m, "✅ تم رفع العضو مميز")

        elif txt == "تنزيل مميز" and target:
            if target in data["vip"]: data["vip"].remove(target)
            save_db(db)
            bot.reply_to(m, "✅ تم تنزيل العضو من مميز")

        elif txt == "تنزيل الكل":
            data["owner"] = None; data["admins"] = []; data["mods"] = []; data["vip"] = []
            save_db(db)
            bot.reply_to(m, "✅ تم تنزيل الكل من الرتب")

        # ========== اوامر المسح ==========
        elif txt == "مسح الكل":
            for i in range(100):
                try: bot.delete_message(chat_id, msg_id - i)
                except: pass

        elif txt == "مسح المدراء":
            data["mods"] = []
            save_db(db)
            bot.reply_to(m, "✅ تم مسح قائمة المدراء")

        elif txt == "مسح المالكين":
            data["owner"] = None
            save_db(db)
            bot.reply_to(m, "✅ تم مسح المالك")

        elif txt == "مسح المحظورين":
            for user in data["banned"][:]:
                try: bot.unban_chat_member(chat_id, user)
                except: pass
            data["banned"] = []
            save_db(db)
            bot.reply_to(m, "✅ تم مسح قائمة المحظورين")

        elif txt == "مسح المكتومين":
            for user in data["muted"][:]:
                try: bot.restrict_chat_member(chat_id, user, ChatPermissions(can_send_messages=True, can_send_media_messages=True))
                except: pass
            data["muted"] = []
            save_db(db)
            bot.reply_to(m, "✅ تم مسح قائمة المكتومين")

        elif txt == "مسح الردود":
            db_file = 'dev_db.json'
            if os.path.exists(db_file):
                with open(db_file, 'r', encoding='utf-8') as f: dev_db = json.load(f)
                dev_db["replies"] = {}
                with open(db_file, 'w', encoding='utf-8') as f: json.dump(dev_db, f, ensure_ascii=False, indent=2)
            else:
                with open(db_file, 'w', encoding='utf-8') as f: json.dump({"replies": {}}, f)
            bot.reply_to(m, "✅ تم مسح الردود")

        elif txt.startswith("مسح ") and len(txt.split()) > 1 and txt.split()[1].isdigit():
            num = int(txt.split()[1])
            for i in range(num + 1):
                try: bot.delete_message(chat_id, msg_id - i)
                except: pass

        elif txt == "مسح بالرد" and target:
            try:
                bot.delete_message(chat_id, m.reply_to_message.message_id)
                bot.delete_message(chat_id, msg_id)
            except: pass

        elif txt == "مسح الايدي":
            bot.reply_to(m, "✅ تم مسح الايدي", reply_markup=telebot.types.ReplyKeyboardRemove())

        elif txt == "مسح الرابط":
            try:
                bot.export_chat_invite_link(chat_id)
                bot.revoke_chat_invite_link(chat_id)
            except: pass
            bot.reply_to(m, "✅ تم مسح رابط المجموعة")

        # ========== اوامر الطرد والحظر ==========
        elif txt == "حظر" and target:
            bot.ban_chat_member(chat_id, target)
            if target not in data["banned"]: data["banned"].append(target)
            save_db(db)
            bot.reply_to(m, "⛔️ تم حظر العضو")

        elif txt == "طرد" and target:
            bot.ban_chat_member(chat_id, target)
            bot.unban_chat_member(chat_id, target)
            bot.reply_to(m, "👢 تم طرد العضو")

        elif txt == "كتم" and target:
            bot.restrict_chat_member(chat_id, target, ChatPermissions(can_send_messages=False))
            if target not in data["muted"]: data["muted"].append(target)
            save_db(db)
            bot.reply_to(m, "🔇 تم كتم العضو")

        elif txt == "تقييد" and target:
            bot.restrict_chat_member(chat_id, target, ChatPermissions())
            bot.reply_to(m, "🔒 تم تقييد العضو")

        elif txt == "الغاء الحظر" and target:
            bot.unban_chat_member(chat_id, target)
            if target in data["banned"]: data["banned"].remove(target)
            save_db(db)
            bot.reply_to(m, "✅ تم الغاء حظر العضو")

        elif txt == "الغاء الكتم" and target:
            bot.restrict_chat_member(chat_id, target, ChatPermissions(can_send_messages=True, can_send_media_messages=True))
            if target in data["muted"]: data["muted"].remove(target)
            save_db(db)
            bot.reply_to(m, "🔊 تم الغاء كتم العضو")

        elif txt == "فك التقييد" and target:
            bot.restrict_chat_member(chat_id, target, ChatPermissions(can_send_messages=True, can_send_media_messages=True))
            bot.reply_to(m, "🔓 تم فك التقييد")

        elif txt == "رفع القيود":
            bot.set_chat_permissions(chat_id, ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_polls=True, can_send_other_messages=True
            ))
            bot.reply_to(m, "✅ تم رفع جميع القيود")
