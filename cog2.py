import sqlite3
import requests
from datetime import datetime
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443

def setup(bot, المطور_الاساسي, admins):

    # ========== انشاء جداول قاعدة البيانات ==========
    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        # جدول الاعدادات العامة للقروب
        c.execute('''CREATE TABLE IF NOT EXISTS group_settings
                    (chat_id INTEGER PRIMARY KEY,
                    welcome TEXT,
                    rules TEXT,
                    link TEXT,
                    channel TEXT,
                    download_enabled INTEGER DEFAULT 1)''')
        # جدول الاوامر المضافة
        c.execute('''CREATE TABLE IF NOT EXISTS custom_commands
                    (chat_id INTEGER, command TEXT, reply TEXT, PRIMARY KEY(chat_id, command))''')
        conn.commit()
        conn.close()
    انشاء_جداول()

    # ========== دوال مساعدة ==========
    def جيب_الاعدادات(chat_id):
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT * FROM group_settings WHERE chat_id =?", (chat_id,)).fetchone()
        conn.close()
        if result:
            return {"welcome": result[1], "rules": result[2], "link": result[3], "channel": result[4], "download": result[5]}
        return {"welcome": None, "rules": None, "link": None, "channel": None, "download": 1}

    def حفظ_الاعدادات(chat_id, key, value):
        conn = sqlite3.connect(DB)
        conn.execute("INSERT OR IGNORE INTO group_settings (chat_id) VALUES (?)", (chat_id,))
        conn.execute(f"UPDATE group_settings SET {key} =? WHERE chat_id =?", (value, chat_id))
        conn.commit()
        conn.close()

    def جيب_الاعضاء_حسب_الرتبة(chat_id, الرتبة):
        conn = sqlite3.connect(DB)
        results = conn.execute("SELECT user_id FROM ranks WHERE chat_id =? AND role =?", (chat_id, الرتبة)).fetchall()
        conn.close()
        return [r[0] for r in results]

    # ========== 1. اوامر رؤية الاعدادات ==========
    @bot.message_handler(commands=['الرابط'])
    def الرابط(message):
        settings = جيب_الاعدادات(message.chat.id)
        if settings['link']: bot.reply_to(message, f"🔗 رابط القروب:\n{settings['link']}")
        else: bot.reply_to(message, "❌ لا يوجد رابط محفوظ. استخدم /انشاء_رابط")

    @bot.message_handler(commands=['المالكين', 'المالكين_الاساسين', 'المنشئين', 'الادمنيه', 'المدراء', 'المميزين'])
    def عرض_الرتب(message):
        الرتبة = message.text.replace("/", "")
        if الرتبة == "المالكين_الاساسين": الرتبة = "مالك_اساسي"
        elif الرتبة == "الادمنيه": الرتبة = "ادمن"
        elif الرتبة == "المدراء": الرتبة = "مدير"
        elif الرتبة == "المنشئين": الرتبة = "منشئ"
        elif الرتبة == "المميزين": الرتبة = "مميز"

        ids = جيب_الاعضاء_حسب_الرتبة(message.chat.id, الرتبة)
        if not ids: return bot.reply_to(message, f"❌ لا يوجد {message.text}")
        text = f"<b>قائمة {message.text}:</b>\n"
        for uid in ids:
            try: text += f"- {bot.get_chat_member(message.chat.id, uid).user.first_name}\n"
            except: text += f"- {uid}\n"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=['القوانين'])
    def القوانين(message):
        settings = جيب_الاعدادات(message.chat.id)
        if settings['rules']: bot.reply_to(message, f"📜 القوانين:\n{settings['rules']}")
        else: bot.reply_to(message, "❌ لم يتم وضع قوانين")

    @bot.message_handler(commands=['المحظورين'])
    def المحظورين(message):
        bot.reply_to(message, "🚧 هذا الامر يحتاج صلاحيات ادمن. استخدمه بعد ما اخلي البوت ادمن")

    @bot.message_handler(commands=['المكتومين'])
    def المكتومين(message):
        bot.reply_to(message, "🚧 هذا الامر يحتاج صلاحيات ادمن. استخدمه بعد ما اخلي البوت ادمن")

    @bot.message_handler(commands=['معلوماتي'])
    def معلوماتي(message):
        user = message.from_user
        bot.reply_to(message, f"""<b>معلوماتك:
━━━━━━━━━━━━
الاسم: {user.first_name}
اليوزر: @{user.username if user.username else "لا يوجد"}
الايدي: {user.id}</b>""", parse_mode="HTML")

    @bot.message_handler(commands=['الحمايه', 'الاعدادت'])
    def الحمايه(message):
        settings = جيب_الاعدادات(message.chat.id)
        حالة_التحميل = "مفعل" if settings['download'] == 1 else "معطل"
        bot.reply_to(message, f"""<b>اعدادات الحماية:
━━━━━━━━━━━━
التحميل: {حالة_التحميل}
القناة: {settings['channel'] if settings['channel'] else "غير محددة"}</b>""", parse_mode="HTML")

    @bot.message_handler(commands=['المجموعه'])
    def المجموعه(message):
        try:
            chat = bot.get_chat(message.chat.id)
            bot.reply_to(message, f"""<b>معلومات المجموعة:
━━━━━━━━━━━━
الاسم: {chat.title}
الاعضاء: {bot.get_chat_members_count(message.chat.id)}
الايدي: {chat.id}</b>""", parse_mode="HTML")
        except: bot.reply_to(message, "❌ خطأ في جلب المعلومات")

    # ========== 2. اوامر وضع الاعدادات ==========
    @bot.message_handler(commands=['انشاء_رابط'])
    def انشاء_رابط(message):
        if not bot.get_chat_member(message.chat.id, bot.get_me().id).status == "administrator": return bot.reply_to(message, "❌ البوت مش ادمن")
        try:
            link = bot.export_chat_invite_link(message.chat.id)
            حفظ_الاعدادات(message.chat.id, "link", link)
            bot.reply_to(message, f"✅ تم انشاء الرابط وحفظه:\n{link}")
        except: bot.reply_to(message, "❌ فشل انشاء الرابط. تاكد ان البوت ادمن")

    @bot.message_handler(commands=['اضف_رابط', 'ضع_رابط'])
    def اضف_رابط(message):
        try:
            link = message.text.split(" ", 1)[1]
            حفظ_الاعدادات(message.chat.id, "link", link)
            bot.reply_to(message, "✅ تم حفظ الرابط")
        except: bot.reply_to(message, "⚠️ الاستخدام: /اضف_رابط https://t.me/...")

    @bot.message_handler(commands=['مسح_الرابط'])
    def مسح_الرابط(message):
        حفظ_الاعدادات(message.chat.id, "link", None)
        bot.reply_to(message, "🗑️ تم مسح الرابط")

    @bot.message_handler(commands=['ضع_الترحيب'])
    def ضع_الترحيب(message):
        try:
            welcome = message.text.split(" ", 1)[1]
            حفظ_الاعدادات(message.chat.id, "welcome", welcome)
            bot.reply_to(message, "✅ تم وضع الترحيب")
        except: bot.reply_to(message, "⚠️ الاستخدام: /ضع_الترحيب اهلا بك")

    @bot.message_handler(commands=['ضع_قوانين'])
    def ضع_قوانين(message):
        try:
            rules = message.text.split(" ", 1)[1]
            حفظ_الاعدادات(message.chat.id, "rules", rules)
            bot.reply_to(message, "✅ تم وضع القوانين")
        except: bot.reply_to(message, "⚠️ الاستخدام: /ضع_قوانين ممنوع السب")

    @bot.message_handler(commands=['اضف_امر'])
    def اضف_امر(message):
        try:
            _, command, reply = message.text.split(" ", 2)
            conn = sqlite3.connect(DB)
            conn.execute("INSERT OR REPLACE INTO custom_commands VALUES (?,?,?)", (message.chat.id, command, reply))
            conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم اضافة الامر /{command}")
        except: bot.reply_to(message, "⚠️ الاستخدام: /اضف_امر الاسم الرد")

    @bot.message_handler(commands=['تعيين_الايدي'])
    def تعيين_الايدي(message): bot.reply_to(message, "🚧 قيد التطوير")

    @bot.message_handler(commands=['اضف_قناه', 'حذف_قناه'])
    def قناه(message):
        try:
            channel = message.text.split(" ", 1)[1]
            if "اضف" in message.text:
                حفظ_الاعدادات(message.chat.id, "channel", channel)
                bot.reply_to(message, f"✅ تم اضافة القناة: {channel}")
            else:
                حفظ_الاعدادات(message.chat.id, "channel", None)
                bot.reply_to(message, "🗑️ تم حذف القناة")
        except: bot.reply_to(message, "⚠️ الاستخدام: /اضف_قناه @username")

    # ========== 3. اوامر التحميل ==========
    @bot.message_handler(commands=['تفعيل_التحميل', 'تعطيل_التحميل'])
    def التحميل(message):
        if "تفعيل" in message.text: حفظ_الاعدادات(message.chat.id, "download_enabled", 1); bot.reply_to(message, "✅ تم تفعيل التحميل")
        else: حفظ_الاعدادات(message.chat.id, "download_enabled", 0); bot.reply_to(message, "❌ تم تعطيل التحميل")

    @bot.message_handler(commands=['بحث'])
    def بحث(message):
        settings = جيب_الاعدادات(message.chat.id)
        if settings['download'] == 0: return bot.reply_to(message, "❌ التحميل معطل")
        try:
            song = message.text.split(" ", 1)[1]
            bot.reply_to(message, f"🔍 جاري البحث عن: {song}\n🚧 ربط اليوتيوب قيد التطوير")
        except: bot.reply_to(message, "⚠️ الاستخدام: /بحث اسم الاغنية")

    @bot.message_handler(commands=['تيك'])
    def تيك(message):
        settings = جيب_الاعدادات(message.chat.id)
        if settings['download'] == 0: return bot.reply_to(message, "❌ التحميل معطل")
        try:
            link = message.text.split(" ", 1)[1]
            bot.reply_to(message, f"📥 جاري تحميل تيك توك: {link}\n🚧 قيد التطوير")
        except: bot.reply_to(message, "⚠️ الاستخدام: /تيك الرابط")

    @bot.message_handler(commands=['ساوند'])
    def ساوند(message):
        settings = جيب_الاعدادات(message.chat.id)
        if settings['download'] == 0: return bot.reply_to(message, "❌ التحميل معطل")
        try:
            link = message.text.split(" ", 1)[1]
            bot.reply_to(message, f"🎵 جاري تحميل ساوند: {link}\n🚧 قيد التطوير")
        except: bot.reply_to(message, "⚠️ الاستخدام: /ساوند الرابط")

    # ========== امر قائمة 2 ==========
    @bot.message_handler(commands=['م2'])
    def م2(message):
        bot.reply_to(message, """<b>• اهلا بك في قائمة اوامر الاعدادات
━━━━━━━━━━━━
- اوامر رؤية الاعدادات :
- الرابط
- المالكين - المالكين_الاساسين - المنشئين
- الادمنيه - المدراء - المميزين
- المحظورين - المكتومين
- القوانين - معلوماتي
- الحمايه - الاعدادت - المجموعه

- اوامر وضع الاعدادات :
- انشاء_رابط
- اضف_رابط - مسح_الرابط - ضع_رابط
- ضع_الترحيب
- ضع_قوانين
- اضف_امر + الامر + الرد
- تعيين_الايدي
- اضف_قناه - حذف_قناه

- اوامر التحميل
- تفعيل_التحميل - تعطيل_التحميل
- بحث + اسم الاغنيه
- تيك + الرابط
- ساوند + الرابط
━━━━━━━━━━━━</b>""", parse_mode="HTML")

    print("✅ تم تحميل: cog2.py - ملف الاعدادات")
