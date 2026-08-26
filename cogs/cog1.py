import sqlite3
from datetime import datetime
from telebot import types
import time

ID_المطور_الاساسي = 7488375443 # حط ايديك
DB = "bot.db"
LOG_FILE = "log.txt"

الرتب_حسب_القوة = {"عضو": 0, "مميز": 1, "ادمن": 2, "مشرف": 3, "مدير": 4, "منشئ": 5, "مالك": 6, "مالك_اساسي": 7, "مطور": 8, "مطور_اساسي": 9}

def setup(bot, المطور_الاساسي, admins):

    # ========== انشاء قاعدة البيانات ==========
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
        if user_id == ID_المطور_الاساسي: return "مطور_اساسي"
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "creator": return "مالك_اساسي"
            if member.status == "administrator": return "ادمن"
        except: pass
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT role FROM ranks WHERE chat_id =? AND user_id =?",(chat_id, user_id)).fetchone()
        conn.close()
        return result[0] if result else "عضو"

    def يقدر_يتصرف(رتبة_اللي_يتصرف, رتبة_الهدف):
        if رتبة_اللي_يتصرف == "مطور_اساسي": return True
        return الرتب_حسب_القوة.get(رتبة_اللي_يتصرف, 0) > الرتب_حسب_القوة.get(رتبة_الهدف, 0)

    def تحقق_صلاحيات_البوت(chat_id):
        try:
            bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
            return bot_member.status == "administrator"
        except: return False

    # ========== دوال الرتب ==========
    def رفع_رتبة(message, الرتبة_الجديدة):
        chat_id = message.chat.id; user_id = message.from_user.id; رتبتي = جيب_الرتبة(chat_id, user_id)
        if الرتبة_الجديدة in ["مطور","مطور_اساسي"] and رتبتي!= "مطور_اساسي": return bot.reply_to(message, "❌ هذا الامر يخص المطور الاساسي فقط")
        if not يقدر_يتصرف(رتبتي, الرتبة_الجديدة): return bot.reply_to(message, f"❌ صلاحياتك {رتبتي} ما تسمح")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO ranks VALUES (?,?,?)", (chat_id, target_id, الرتبة_الجديدة)); conn.commit(); conn.close()
        سجل_العملية(f"{message.from_user.first_name} رفع {target_name} الى {الرتبة_الجديدة}")
        bot.reply_to(message, f"✅ تم رفع {target_name} الى {الرتبة_الجديدة}")

    def تنزيل_رتبة(message, الرتبة):
        chat_id = message.chat.id; user_id = message.from_user.id; رتبتي = جيب_الرتبة(chat_id, user_id)
        if not يقدر_يتصرف(رتبتي, الرتبة): return bot.reply_to(message, f"❌ صلاحياتك {رتبتي} ما تسمح")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM ranks WHERE chat_id =? AND user_id =? AND role =?", (chat_id, target_id, الرتبة)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم تنزيل {target_name} من {الرتبة}")

    def مسح_كل_الرتب(message):
        chat_id = message.chat.id; user_id = message.from_user.id; رتبتي = جيب_الرتبة(chat_id, user_id)
        if رتبتي not in ["مالك_اساسي", "مطور_اساسي"]: return bot.reply_to(message, "❌ للمالك الاساسي فقط")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id; target_name = message.reply_to_message.from_user.first_name
        if target_id == ID_المطور_الاساسي: return bot.reply_to(message, "❌ ما تقدر تمسح المطور الاساسي")
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM ranks WHERE chat_id =? AND user_id =?", (chat_id, target_id)); conn.commit(); conn.close()
        bot.reply_to(message, f"🗑️ تم مسح جميع الرتب من {target_name}")

    # ========== 1. اوامر الرفع والتنزيل ==========
    @bot.message_handler(commands=['رفع_مالك_اساسي', 'تنزيل_مالك_اساسي'])
    def رفع_مالك_اساسي(message): رفع_رتبة(message, "مالك_اساسي") if "رفع" in message.text else تنزيل_رتبة(message, "مالك_اساسي")
    @bot.message_handler(commands=['رفع_مالك', 'تنزيل_مالك'])
    def رفع_مالك(message): رفع_رتبة(message, "مالك") if "رفع" in message.text else تنزيل_رتبة(message, "مالك")
    @bot.message_handler(commands=['رفع_منشئ', 'تنزيل_منشئ'])
    def رفع_منشئ(message): رفع_رتبة(message, "منشئ") if "رفع" in message.text else تنزيل_رتبة(message, "منشئ")
    @bot.message_handler(commands=['رفع_مدير', 'تنزيل_مدير'])
    def رفع_مدير(message): رفع_رتبة(message, "مدير") if "رفع" in message.text else تنزيل_رتبة(message, "مدير")
    @bot.message_handler(commands=['رفع_مشرف', 'تنزيل_مشرف'])
    def رفع_مشرف(message): رفع_رتبة(message, "مشرف") if "رفع" in message.text else تنزيل_رتبة(message, "مشرف")
    @bot.message_handler(commands=['رفع_ادمن', 'تنزيل_ادمن'])
    def رفع_ادمن(message): رفع_رتبة(message, "ادمن") if "رفع" in message.text else تنزيل_رتبة(message, "ادمن")
    @bot.message_handler(commands=['رفع_مميز', 'تنزيل_مميز'])
    def رفع_مميز(message): رفع_رتبة(message, "مميز") if "رفع" in message.text else تنزيل_رتبة(message, "مميز")
    @bot.message_handler(commands=['تنزيل_الكل'])
    def تنزيل_الكل(message): مسح_كل_الرتب(message)

    # ========== 2. اوامر الطرد والحظر ==========
    @bot.message_handler(commands=['حظر'])
    def حظر(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        if not تحقق_صلاحيات_البوت(message.chat.id): return bot.reply_to(message, "❌ البوت مش ادمن")
        chat_id = message.chat.id; admin_id = message.from_user.id; target_id = message.reply_to_message.from_user.id
        if not يقدر_يتصرف(جيب_الرتبة(chat_id, admin_id), جيب_الرتبة(chat_id, target_id)): return bot.reply_to(message, "❌ ما تقدر تحظره")
        bot.ban_chat_member(chat_id, target_id)
        bot.reply_to(message, f"⛔ تم حظر {message.reply_to_message.from_user.first_name}")
    @bot.message_handler(commands=['الغاء_الحظر'])
    def الغاء_حظر(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.reply_to(message, f"✅ تم فك الحظر عن {message.reply_to_message.from_user.first_name}")
    @bot.message_handler(commands=['طرد'])
    def طرد(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id); bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.reply_to(message, f"👢 تم طرد {message.reply_to_message.from_user.first_name}")
    @bot.message_handler(commands=['كتم'])
    def كتم(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=types.ChatPermissions(can_send_messages=False))
        bot.reply_to(message, f"🔇 تم كتم {message.reply_to_message.from_user.first_name}")
    @bot.message_handler(commands=['الغاء_الكتم'])
    def الغاء_كتم(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=types.ChatPermissions(can_send_messages=True, can_send_media_messages=True))
        bot.reply_to(message, f"🔊 تم فك الكتم عن {message.reply_to_message.from_user.first_name}")
    @bot.message_handler(commands=['تقييد'])
    def تقييد(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=types.ChatPermissions())
        bot.reply_to(message, f"⛓️ تم تقييد {message.reply_to_message.from_user.first_name}")
    @bot.message_handler(commands=['فك_التقييد'])
    def فك_التقييد(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=types.ChatPermissions(can_send_messages=True, can_send_media_messages=True))
        bot.reply_to(message, f"✅ تم فك التقييد عن {message.reply_to_message.from_user.first_name}")
    @bot.message_handler(commands=['تقييد_الوقت'])
    def تقييد_الوقت(message): bot.reply_to(message, "🚧 قيد التطوير - استخدم /تقييد")
    @bot.message_handler(commands=['رفع_القيود'])
    def رفع_القيود(message): bot.reply_to(message, "🚧 قيد التطوير")
    @bot.message_handler(commands=['منع_بالرد', 'الغاء_منع'])
    def منع_بالرد(message): bot.reply_to(message, "🚧 قيد التطوير")
    @bot.message_handler(commands=['طرد_البوتات', 'طرد_المحذوفين', 'كشف_البوتات'])
    def طرد_البوتات(message): bot.reply_to(message, "🚧 قيد التطوير")

    # ========== 3. اوامر المسح ==========
    @bot.message_handler(commands=['مسح_الكل'])
    def مسح_الكل(message):
        if جيب_الرتبة(message.chat.id, message.from_user.id) not in ["مدير","منشئ","مالك","مالك_اساسي","مطور","مطور_اساسي"]: return bot.reply_to(message, "❌ للمدير فما فوق")
        bot.delete_message(message.chat.id, message.message_id)
    @bot.message_handler(commands=['مسح_عدد'])
    def مسح_عدد(message):
        if جيب_الرتبة(message.chat.id, message.from_user.id) not in ["مدير","منشئ","مالك","مالك_اساسي","مطور","مطور_اساسي"]: return bot.reply_to(message, "❌ للمدير فما فوق")
        try:
            num = int(message.text.split()[1])
            for i in range(num + 1): bot.delete_message(message.chat.id, message.message_id - i)
        except: bot.reply_to(message, "⚠️ الاستخدام: /مسح_عدد 10")
    @bot.message_handler(commands=['مسح_بالرد'])
    def مسح_بالرد(message):
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الرسالة")
        bot.delete_message(message.chat.id, message.reply_to_message.message_id); bot.delete_message(message.chat.id, message.message_id)

    # باقي اوامر المسح وهمية لحد نكمل قاعدة البيانات
    @bot.message_handler(commands=['مسح_المنشئين','مسح_المدراء','مسح_المالكين','مسح_الادمنيه','مسح_المميزين','مسح_المحظورين','مسح_المكتومين','مسح_قائمة_المنع','مسح_الردود','مسح_الاوامر','مسح_الايدي','مسح_الترحيب','مسح_الرابط'])
    def مسح_قيد_التطوير(message): bot.reply_to(message, "🚧 هذا الامر قيد البرمجة")

    # ========== امر قائمة 1 ==========
    @bot.message_handler(commands=['م1'])
    def م1(message):
        bot.reply_to(message, """<b>• أهلاً بك في عزي
- قائمة اوامر الادمنيه
━━━━━━━━━━━━
- اوامر الرفع والتنزيل :
• رفع_مالك_اساسي - تنزيل_مالك_اساسي
• رفع_مالك - تنزيل_مالك
• رفع_منشئ - تنزيل_منشئ
• رفع_مدير - تنزيل_مدير
• رفع_مشرف - تنزيل_مشرف
• رفع_ادمن - تنزيل_ادمن
• رفع_مميز - تنزيل_مميز
• تنزيل_الكل

- اوامر المسح :
• مسح_الكل
• مسح_عدد + العدد
• مسح_بالرد
• مسح_المنشئين - مسح_المدراء - مسح_المالكين
• مسح_الادمنيه - مسح_المميزين
• مسح_المحظورين - مسح_المكتومين
• مسح_قائمة_المنع - مسح_الردود - مسح_الاوامر
• مسح_الايدي - مسح_الترحيب - مسح_الرابط

- اوامر الطرد والحظر :
• تقييد_الوقت + الوقت
• حظر - الغاء_الحظر
• طرد
• كتم - الغاء_الكتم
• تقييد - فك_التقييد
• رفع_القيود
• منع_بالرد - الغاء_منع
• طرد_البوتات - طرد_المحذوفين - كشف_البوتات
━━━━━━━━━━━━</b>""", parse_mode="HTML")

    # ========== الاضافات الجديدة ==========
    @bot.message_handler(commands=['start'])
    def start(message):
        name = message.from_user.first_name
        bot.reply_to(message, f"❤️ اهلا <b>{name}</b>\n\nانا البوت <b>𝐓𝐢𝐚</b>\nاستخدم /m1 لعرض اوامر الادمنيه", parse_mode="HTML")

    @bot.message_handler(commands=['help'])
    def help_cmd(message):
        bot.reply_to(message, "📜 استخدم /m1 لعرض قائمة الادمنيه الكاملة")

    print("✅ تم تحميل: cog1.py - ملف الادمنيه كامل")
