import sqlite3
import os
import time
from datetime import datetime
from telebot import types

ID_المطور_الاساسي = 7488375443 # ايديك
DB = "bot.db"
LOG_FILE = "log.txt"

الرتب_حسب_القوة = {"عضو": 0, "ادمن": 1, "مدير": 2, "مالك": 3, "مالك_اساسي": 4, "مطور": 5, "مطور_اساسي": 6}

def setup(bot, المطور_الاساسي, admins):

    # ========== انشاء قاعدة البيانات اول مرة ==========
    def انشاء_قاعدة_البيانات():
        conn = sqlite3.connect(DB)
        conn.execute('''CREATE TABLE IF NOT EXISTS ranks
                        (chat_id INTEGER, user_id INTEGER, role TEXT, PRIMARY KEY(chat_id, user_id, role))''')
        conn.commit()
        conn.close()
    انشاء_قاعدة_البيانات()

    # ========== دوال مساعدة ==========
    def سجل_العملية(نص):
        وقت = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{وقت}] {نص}\n")

    def جيب_الرتبة(chat_id, user_id):
        if user_id == ID_المطور_الاساسي:
            return "مطور_اساسي"
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "creator":
                return "مالك_اساسي"
        except: pass
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT role FROM ranks WHERE chat_id =? AND user_id =?",(chat_id, user_id)).fetchone()
        conn.close()
        return result[0] if result else "عضو"

    def يقدر_يتصرف(رتبة_اللي_يتصرف, رتبة_الهدف):
        if رتبة_اللي_يتصرف == "مطور_اساسي": return True
        return الرتب_حسب_القوة.get(رتبة_اللي_يتصرف, 0) > الرتب_حسب_القوة.get(رتبة_الهدف, 0)

    # ========== دوال الرتب ==========
    def رفع_رتبة(message, الرتبة_الجديدة):
        chat_id = message.chat.id; user_id = message.from_user.id; رتبتي = جيب_الرتبة(chat_id, user_id)
        if الرتبة_الجديدة == "مطور" and رتبتي!= "مطور_اساسي":
            return bot.reply_to(message, "❌ هذا الامر يخص المطور الاساسي فقط")
        if not يقدر_يتصرف(رتبتي, الرتبة_الجديدة):
            return bot.reply_to(message, f"❌ صلاحياتك {رتبتي} ما تسمح")
        if not message.reply_to_message:
            return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
        admin_name = message.from_user.first_name
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO ranks VALUES (?,?,?)", (chat_id, target_id, الرتبة_الجديدة)); conn.commit(); conn.close()
        سجل_العملية(f"{admin_name} رفع {target_name} الى {الرتبة_الجديدة} في قروب {chat_id}")
        bot.reply_to(message, f"✅ تم رفع {target_name} الى {الرتبة_الجديدة}")

    def تنزيل_رتبة(message, الرتبة):
        chat_id = message.chat.id; user_id = message.from_user.id; رتبتي = جيب_الرتبة(chat_id, user_id)
        if not يقدر_يتصرف(رتبتي, الرتبة): return bot.reply_to(message, f"❌ صلاحياتك {رتبتي} ما تسمح")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name; admin_name = message.from_user.first_name
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM ranks WHERE chat_id =? AND user_id =? AND role =?", (chat_id, target_id, الرتبة)); conn.commit(); conn.close()
        سجل_العملية(f"{admin_name} نزل {target_name} من {الرتبة} في قروب {chat_id}")
        bot.reply_to(message, f"✅ تم تنزيل {target_name} من {الرتبة}")

    def مسح_كل_الرتب(message):
        chat_id = message.chat.id; user_id = message.from_user.id; رتبتي = جيب_الرتبة(chat_id, user_id)
        if رتبتي not in ["مالك_اساسي", "مطور_اساسي"]: return bot.reply_to(message, "❌ للمالك الاساسي فقط")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name; admin_name = message.from_user.first_name
        if target_id == ID_المطور_الاساسي: return bot.reply_to(message, "❌ ما تقدر تمسح المطور الاساسي")
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM ranks WHERE chat_id =? AND user_id =?", (chat_id, target_id)); conn.commit(); conn.close()
        سجل_العملية(f"{admin_name} مسح كل الرتب من {target_name} في قروب {chat_id}")
        bot.reply_to(message, f"🗑️ تم مسح جميع الرتب من {target_name}")

    # ========== اوامر الادارة ==========
    @bot.message_handler(commands=['طرد'])
    def طرد(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        chat_id = message.chat.id; admin_id = message.from_user.id; target_id = message.reply_to_message.from_user.id
        if not يقدر_يتصرف(جيب_الرتبة(chat_id, admin_id), جيب_الرتبة(chat_id, target_id)): return bot.reply_to(message, "❌ ما تقدر تطرده")
        bot.ban_chat_member(chat_id, target_id); bot.unban_chat_member(chat_id, target_id)
        سجل_العملية(f"{message.from_user.first_name} طرد {message.reply_to_message.from_user.first_name}")
        bot.reply_to(message, f"👢 تم طرد {message.reply_to_message.from_user.first_name}")

    @bot.message_handler(commands=['حظر'])
    def حظر(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        chat_id = message.chat.id; admin_id = message.from_user.id; target_id = message.reply_to_message.from_user.id
        if not يقدر_يتصرف(جيب_الرتبة(chat_id, admin_id), جيب_الرتبة(chat_id, target_id)): return bot.reply_to(message, "❌ ما تقدر تحظره")
        bot.ban_chat_member(chat_id, target_id)
        سجل_العملية(f"{message.from_user.first_name} حظر {message.reply_to_message.from_user.first_name}")
        bot.reply_to(message, f"⛔ تم حظر {message.reply_to_message.from_user.first_name}")

    @bot.message_handler(commands=['الغاء_الحظر'])
    def الغاء_حظر(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        chat_id = message.chat.id; admin_id = message.from_user.id
        if جيب_الرتبة(chat_id, admin_id) == "عضو": return bot.reply_to(message, "❌ ما عندك صلاحية")
        target_id = message.reply_to_message.from_user.id
        bot.unban_chat_member(chat_id, target_id)
        سجل_العملية(f"{message.from_user.first_name} فك حظر {message.reply_to_message.from_user.first_name}")
        bot.reply_to(message, f"✅ تم فك الحظر عن {message.reply_to_message.from_user.first_name}")

    @bot.message_handler(commands=['كتم'])
    def كتم(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        chat_id = message.chat.id; admin_id = message.from_user.id; target_id = message.reply_to_message.from_user.id
        if not يقدر_يتصرف(جيب_الرتبة(chat_id, admin_id), جيب_الرتبة(chat_id, target_id)): return bot.reply_to(message, "❌ ما تقدر تكتمه")
        bot.restrict_chat_member(chat_id, target_id, permissions=types.ChatPermissions(can_send_messages=False))
        سجل_العملية(f"{message.from_user.first_name} كتم {message.reply_to_message.from_user.first_name}")
        bot.reply_to(message, f"🔇 تم كتم {message.reply_to_message.from_user.first_name}")

    @bot.message_handler(commands=['الغاء_الكتم'])
    def الغاء_كتم(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        chat_id = message.chat.id; admin_id = message.from_user.id
        if جيب_الرتبة(chat_id, admin_id) == "عضو": return bot.reply_to(message, "❌ ما عندك صلاحية")
        target_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(chat_id, target_id, permissions=types.ChatPermissions(can_send_messages=True, can_send_media_messages=True))
        سجل_العملية(f"{message.from_user.first_name} فك كتم {message.reply_to_message.from_user.first_name}")
        bot.reply_to(message, f"🔊 تم فك الكتم عن {message.reply_to_message.from_user.first_name}")

    @bot.message_handler(commands=['كشف_الرتبة'])
    def كشف_رتبة(message):
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        رتبة = جيب_الرتبة(message.chat.id, target.id)
        bot.reply_to(message, f"👤 {target.first_name}\nرتبته: {رتبة}")

    # ========== اوامر الرتب ==========
    @bot.message_handler(commands=['مسح_الرتب'])
    def امر_المسح(message): مسح_كل_الرتب(message)

    @bot.message_handler(commands=['رفع_مطور', 'تنزيل_مطور','رفع_مالك_اساسي', 'تنزيل_مالك_اساسي','رفع_مالك', 'تنزيل_مالك','رفع_مدير', 'تنزيل_مدير','رفع_ادمن', 'تنزيل_ادمن'])
    def الاوامر(message):
        cmd = message.text.replace("/", "")
        if "مطور" in cmd: رفع_رتبة(message, "مطور") if "رفع" in cmd else تنزيل_رتبة(message, "مطور")
        elif "مالك_اساسي" in cmd: رفع_رتبة(message, "مالك_اساسي") if "رفع" in cmd else تنزيل_رتبة(message, "مالك_اساسي")
        elif "مالك" in cmd: رفع_رتبة(message, "مالك") if "رفع" in cmd else تنزيل_رتبة(message, "مالك")
        elif "مدير" in cmd: رفع_رتبة(message, "مدير") if "رفع" in cmd else تنزيل_رتبة(message, "مدير")
        elif "ادمن" in cmd: رفع_رتبة(message, "ادمن") if "رفع" in cmd else تنزيل_رتبة(message, "ادمن")

    print("✅ تم تحميل: cog1.py - نظام الرتب")
