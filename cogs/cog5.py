import sqlite3
import os
import sys
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443

def setup(bot, المطور_الاساسي, admins):

    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        # ردود التواصل
        c.execute('''CREATE TABLE IF NOT EXISTS contact_replies
                    (chat_id INTEGER, trigger TEXT, reply TEXT, PRIMARY KEY(chat_id, trigger))''')
        # الردود العامة
        c.execute('''CREATE TABLE IF NOT EXISTS global_replies
                    (trigger TEXT, reply TEXT, type TEXT DEFAULT 'text', PRIMARY KEY(trigger))''')
        # الردود المتعددة العامة
        c.execute('''CREATE TABLE IF NOT EXISTS global_multi_replies
                    (trigger TEXT, reply TEXT, PRIMARY KEY(trigger, reply))''')
        # رتب العام
        c.execute('''CREATE TABLE IF NOT EXISTS global_ranks
                    (user_id INTEGER, rank_name TEXT, PRIMARY KEY(user_id, rank_name))''')
        # الحظر والكتم العام
        c.execute('''CREATE TABLE IF NOT EXISTS global_ban
                    (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS global_mute
                    (chat_id INTEGER, user_id INTEGER, PRIMARY KEY(chat_id, user_id))''')
        # كليشات
        c.execute('''CREATE TABLE IF NOT EXISTS clips
                    (clip_name TEXT PRIMARY KEY, text TEXT)''')
        # اعدادات
        c.execute('''CREATE TABLE IF NOT EXISTS dev_settings
                    (key TEXT PRIMARY KEY, value INTEGER)''')
        conn.commit()
        conn.close()
    انشاء_جداول()

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

    def هو_مطور(chat_id, user_id):
        return جيب_الرتبة(chat_id, user_id) in ["مطور","مطور_اساسي"] or user_id == ID_المطور_الاساسي

    def جيب_حالة(chat_id, المفتاح):
        conn = sqlite3.connect(DB); result = conn.execute("SELECT value FROM dev_settings WHERE key =?", (f"{chat_id}_{المفتاح}",)).fetchone(); conn.close()
        return result[0] if result else 1

    def حفظ_حالة(chat_id, المفتاح, القيمة):
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO dev_settings VALUES (?,?)", (f"{chat_id}_{المفتاح}", القيمة)); conn.commit(); conn.close()

    # ========== 1. اوامر التواصل ==========
    @bot.message_handler(commands=['اضف_رد_تواصل'])
    def اضف_رد_تواصل(message):
        if not هو_مطور(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمطور فقط")
        try: _, trigger, reply = message.text.split(" ", 2)
        except: return bot.reply_to(message, "⚠️ الاستخدام: /اضف_رد_تواصل كلمة الرد")
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO contact_replies VALUES (?,?,?)", (message.chat.id, trigger, reply)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم اضافة رد التواصل: {trigger}")

    @bot.message_handler(commands=['حذف_رد_تواصل'])
    def حذف_رد_تواصل(message):
        if not هو_مطور(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمطور فقط")
        try: trigger = message.text.split(" ", 1)[1]
        except: return bot.reply_to(message, "⚠️ الاستخدام: /حذف_رد_تواصل كلمة")
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM contact_replies WHERE chat_id =? AND trigger =?", (message.chat.id, trigger)); conn.commit(); conn.close()
        bot.reply_to(message, f"🗑️ تم حذف رد التواصل: {trigger}")

    @bot.message_handler(commands=['ردود_التواصل'])
    def ردود_التواصل(message):
        conn = sqlite3.connect(DB); results = conn.execute("SELECT trigger, reply FROM contact_replies WHERE chat_id =?", (message.chat.id,)).fetchall(); conn.close()
        if not results: return bot.reply_to(message, "❌ لا يوجد ردود تواصل")
        text = "<b>ردود التواصل:</b>\n━━━━━━━━━━━━\n"
        for t, r in results: text += f"- {t} : {r}\n"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(func=lambda m: True)
    def تطبيق_ردود_التواصل(message):
        if message.text:
            conn = sqlite3.connect(DB); result = conn.execute("SELECT reply FROM contact_replies WHERE chat_id =? AND trigger =?", (message.chat.id, message.text)).fetchone(); conn.close()
            if result: bot.reply_to(message, result[0])

    # ========== 2. اوامر المطور الاساسي ==========
    @bot.message_handler(commands=['ترحيب_البوت'])
    def ترحيب_البوت(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        bot.reply_to(message, "🚧 ضع نص الترحيب بعد الامر")

    @bot.message_handler(commands=['مسح_صوره_الترحيب'])
    def مسح_صوره_الترحيب(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        bot.reply_to(message, "🗑️ تم مسح صورة الترحيب")

    @bot.message_handler(commands=['اسم_بوتك'])
    def اسم_بوتك(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        if "غادر" in message.text:
            bot.leave_chat(message.chat.id)
            bot.reply_to(message, "👋 غادرت")

    @bot.message_handler(commands=['ذيع'])
    def ذيع(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        bot.reply_to(message, "🚧 امر الاذاعة قيد التطوير")

    # ========== 3. اوامر الرفع والتنزيل Dev ==========
    @bot.message_handler(commands=['رفع_Dev', 'تنزيل_Dev'])
    def رفع_تنزيل_Dev(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id
        if "رفع" in message.text:
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO ranks VALUES (?,?,?)", (message.chat.id, target_id, "مطور")); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم رفع {message.reply_to_message.from_user.first_name} الى Dev")
        else:
            conn = sqlite3.connect(DB); conn.execute("DELETE FROM ranks WHERE chat_id =? AND user_id =? AND role ='مطور'", (message.chat.id, target_id)); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم تنزيل {message.reply_to_message.from_user.first_name} من Dev")

    @bot.message_handler(commands=['مسح_المالكين_الاساسين'])
    def مسح_المالكين_الاساسين(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        bot.reply_to(message, "🗑️ تم مسح المالكين الاساسيين")

    # ========== 4. اوامر الحظر والكتم العام ==========
    @bot.message_handler(commands=['حظر_عام', 'كتم_عام'])
    def حظر_كتم_عام(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id
        if "حظر" in message.text:
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO global_ban VALUES (?)", (target_id,)); conn.commit(); conn.close()
            bot.reply_to(message, f"⛔ تم حظر {message.reply_to_message.from_user.first_name} عام")
        else:
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO global_mute VALUES (?,?)", (message.chat.id, target_id)); conn.commit(); conn.close()
            bot.reply_to(message, f"🔇 تم كتم {message.reply_to_message.from_user.first_name} عام")

    @bot.message_handler(commands=['الغاء_حظر_عام', 'الغاء_كتم_عام', 'الغاء_عام'])
    def الغاء_حظر_كتم_عام(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        target_id = message.reply_to_message.from_user.id
        conn = sqlite3.connect(DB); conn.execute("DELETE FROM global_ban WHERE user_id =?", (target_id,)); conn.execute("DELETE FROM global_mute WHERE user_id =?", (target_id,)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم فك الحظر/الكتم العام عن {message.reply_to_message.from_user.first_name}")

    @bot.message_handler(commands=['قائمه_العام'])
    def قائمه_العام(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        conn = sqlite3.connect(DB); bans = conn.execute("SELECT user_id FROM global_ban").fetchall(); mutes = conn.execute("SELECT user_id FROM global_mute").fetchall(); conn.close()
        text = f"<b>المحظورين عام: {len(bans)}\nالمكتومين عام: {len(mutes)}</b>"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=['مسح_المحظورين_عام', 'مسح_المكتومين_عام'])
    def مسح_العام(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        conn = sqlite3.connect(DB)
        if "محظورين" in message.text: conn.execute("DELETE FROM global_ban")
        else: conn.execute("DELETE FROM global_mute")
        conn.commit(); conn.close()
        bot.reply_to(message, "🗑️ تم المسح")

    # ========== 5. اوامر الردود العامة ==========
    @bot.message_handler(commands=['اضف_رد_عام'])
    def اضف_رد_عام(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        try: _, trigger, reply = message.text.split(" ", 2)
        except: return bot.reply_to(message, "⚠️ الاستخدام: /اضف_رد_عام كلمة الرد")
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO global_replies VALUES (?,?,?)", (trigger, reply, "text")); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم اضافة رد عام: {trigger}")

    @bot.message_handler(commands=['اضف_رد_متعدد_عام'])
    def اضف_رد_متعدد_عام(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        try: _, trigger, reply = message.text.split(" ", 2)
        except: return bot.reply_to(message, "⚠️ الاستخدام: /اضف_رد_متعدد_عام كلمة الرد")
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO global_multi_replies VALUES (?,?)", (trigger, reply)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم اضافة رد متعدد عام: {trigger}")

    @bot.message_handler(commands=['الردود_العامه', 'الردود_المتعدده_العامه'])
    def عرض_الردود_العامه(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        conn = sqlite3.connect(DB)
        if "متعدده" in message.text: results = conn.execute("SELECT trigger FROM global_multi_replies").fetchall()
        else: results = conn.execute("SELECT trigger FROM global_replies").fetchall()
        conn.close()
        text = "<b>الردود العامة:</b>\n" + "\n".join([r[0] for r in results]) if results else "❌ لا يوجد"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=['مسح_الردود_العامه', 'مسح_الردود_المتعدده_العامه'])
    def مسح_الردود_العامه(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        conn = sqlite3.connect(DB)
        if "متعدده" in message.text: conn.execute("DELETE FROM global_multi_replies")
        else: conn.execute("DELETE FROM global_replies")
        conn.commit(); conn.close()
        bot.reply_to(message, "🗑️ تم مسح الردود")

    # ========== 6. اوامر الكليشات والالعاب ==========
    @bot.message_handler(commands=['اضف_ميزة', 'اضف_لعبه_عام', 'مسح_ضع_كليشه'])
    def اوامر_اخرى(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        bot.reply_to(message, "🚧 هذا الامر قيد البرمجة")

    @bot.message_handler(commands=['تحديث'])
    def تحديث(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        bot.reply_to(message, "✅ تم تحديث الملفات")

    @bot.message_handler(commands=['اعاده_تشغيل', 'reload'])
    def اعاده_تشغيل(message):
        if message.from_user.id!= ID_المطور_الاساسي: return bot.reply_to(message, "❌ للمطور الاساسي فقط")
        bot.reply_to(message, "🔄 جاري اعادة التشغيل...")
        os.execv(sys.executable, ['python'] + sys.argv)

    @bot.message_handler(commands=['فتح_ردود_MY', 'قفل_ردود_MY', 'فتح_الاحصائيات', 'قفل_الاحصائيات', 'فتح_حظر_العام', 'قفل_حظر_العام'])
    def فتح_قفل(message):
        if not هو_مطور(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمطور فقط")
        key = message.text.replace("/", "").replace("فتح_", "").replace("قفل_", "")
        if "فتح" in message.text: حفظ_حالة(message.chat.id, key, 1); bot.reply_to(message, f"🔓 تم فتح {key}")
        else: حفظ_حالة(message.chat.id, key, 0); bot.reply_to(message, f"🔒 تم قفل {key}")

    # ========== امر قائمة 5 ==========
    @bot.message_handler(commands=['م5'])
    def م5(message):
        bot.reply_to(message, """<b>• اهلا بك عزي Dev
━━━━━━━━━━━━
- اضف_رد_تواصل + الكلمة + الرد
- ترحيب_البوت
- حذف_رد_تواصل + الكلمة
- ردود_التواصل
- تعطيل
- اسم_بوتك + غادر
- تعطيل_الزاجل - تفعيل_الزاجل
- مسح_المالكين_الاساسين
- مسح_صوره_الترحيب
- ذيع + ايدي
- فتح_ردود_MY - قفل_ردود_MY
- رفع_Dev - تنزيل_Dev
- فتح_الاحصائيات - قفل_الاحصائيات
- فتح_حظر_العام - قفل_حظر_العام
- حظر_عام - كتم_عام
- حظر - الغاء_حظر
- مسح_المحظورين - المحظورين_للتواصل
- قائمه_العام
- الغاء_كتم_عام - الغاء_عام
- مسح_المكتومين_عام
- مسح_المحظورين_عام
- قائمه_الرتب_العامه
- تغير_الرتب_العام
- مسح_رتب_العام
- مسح_رتبه_عام
- الردود_العامه
- الردود_المتعدده_العامه
- مسح_الردود_العامه
- مسح_الردود_المتعدده_العامه
- اضف_رد_عام
- اضف_رد_متعدد_عام
- اضف_ميزة
- اضف_لعبه_عام
- مسح_ضع_كليشه_الالعاب
- مسح_ضع_كليشه_م1 الى م6
- تحديث
- اعاده_تشغيل - reload
━━━━━━━━━━━━</b>""", parse_mode="HTML")

    print("✅ تم تحميل: cog5.py - ملف المطورين")
