import sqlite3
import os
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443 # ايديك انت

def setup_settings(bot):

    # ========== دوال مساعدة ==========
    def جيب_الرتبة(chat_id, user_id):
        if user_id == ID_المطور_الاساسي: return "مطور_اساسي"
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "creator": return "مالك_اساسي"
        except: pass
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT role FROM ranks WHERE chat_id =? AND user_id =?",(chat_id, user_id)).fetchone()
        conn.close()
        return result[0] if result else "عضو"

    def يقدر_يتصرف(chat_id, user_id):
        return جيب_الرتبة(chat_id, user_id)!= "عضو"

    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        conn.execute("CREATE TABLE IF NOT EXISTS group_settings (chat_id INTEGER PRIMARY KEY, link TEXT, welcome TEXT, rules TEXT, channel TEXT, id_text TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS custom_commands (chat_id INTEGER, command TEXT, reply TEXT, PRIMARY KEY(chat_id, command))")
        conn.execute("CREATE TABLE IF NOT EXISTS protection (chat_id INTEGER PRIMARY KEY, flood INTEGER DEFAULT 0, links INTEGER DEFAULT 0)")
        conn.commit()
        conn.close()

    انشاء_جداول()

    # ========== اوامر الرؤية ==========
    @bot.message_handler(commands=['الرابط'])
    def الرابط(message):
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT link FROM group_settings WHERE chat_id =?", (message.chat.id,)).fetchone()
        conn.close()
        if result and result[0]: bot.reply_to(message, f"🔗 الرابط:\n{result[0]}")
        else: bot.reply_to(message, "❌ مافي رابط. استخدم /انشاء_رابط")

    @bot.message_handler(commands=['المالكين_الاساسين', 'المالكين', 'المنشئين', 'الادمنيه', 'المدراء', 'المميزين'])
    def عرض_الرتب(message):
        cmd = message.text.replace("/", "")
        chat_id = message.chat.id
        conn = sqlite3.connect(DB)
        roles = {"المالكين_الاساسين":"مالك_اساسي","المالكين":"مالك","المدراء":"مدير","الادمنيه":"ادمن","المميزين":"مميز"}
        if cmd in roles:
            users = conn.execute("SELECT user_id FROM ranks WHERE chat_id =? AND role =?", (chat_id, roles[cmd])).fetchall()
            text = f"**{cmd}:**\n"
            for u in users:
                try: name = bot.get_chat_member(chat_id, u[0]).user.first_name
                except: name = u[0]
                text += f"• {name} - `{u[0]}`\n"
            bot.reply_to(message, text if users else f"❌ مافي {cmd}")
        elif cmd == "المنشئين":
            admins = bot.get_chat_administrators(chat_id)
            creators = [a for a in admins if a.status == "creator"]
            text = "**المنشئين:**\n" + "\n".join([f"• {c.user.first_name}" for c in creators])
            bot.reply_to(message, text if creators else "❌ مافي منشئين")
        conn.close()

    @bot.message_handler(commands=['المحظورين'])
    def المحظورين(message):
        try:
            banned = bot.get_chat_members(message.chat.id, filter="kicked")
            text = "**المحظورين:**\n" + "\n".join([f"• {b.user.first_name}" for b in banned])
            bot.reply_to(message, text if banned else "✅ مافي محظورين")
        except: bot.reply_to(message, "❌ البوت مش ادمن")

    @bot.message_handler(commands=['المكتومين'])
    def المكتومين(message):
        bot.reply_to(message, "🔇 حاليا الكتم مؤقت. ما ينحفظ في الداتا")

    @bot.message_handler(commands=['القوانين'])
    def القوانين(message):
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT rules FROM group_settings WHERE chat_id =?", (message.chat.id,)).fetchone()
        conn.close()
        bot.reply_to(message, f"📜 القوانين:\n{result[0]}" if result and result[0] else "❌ لم يتم وضع قوانين")

    @bot.message_handler(commands=['معلوماتي'])
    def معلوماتي(message):
        user = message.from_user
        رتبة = جيب_الرتبة(message.chat.id, user.id)
        bot.reply_to(message, f"👤 اسمك: {user.first_name}\n🆔 ايديك: `{user.id}`\n🎖️ رتبتك: {رتبة}")

    @bot.message_handler(commands=['الحمايه'])
    def الحمايه(message):
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT flood, links FROM protection WHERE chat_id =?", (message.chat.id,)).fetchone()
        conn.close()
        flood = "مفعل" if result and result[0] else "معطل"
        links = "مفعل" if result and result[1] else "معطل"
        bot.reply_to(message, f"🛡️ **الحماية**\nالسبام: {flood}\nالروابط: {links}")

    @bot.message_handler(commands=['الاعدادت', 'المجموعه'])
    def الاعدادات(message):
        conn = sqlite3.connect(DB)
        s = conn.execute("SELECT * FROM group_settings WHERE chat_id =?", (message.chat.id,)).fetchone()
        p = conn.execute("SELECT * FROM protection WHERE chat_id =?", (message.chat.id,)).fetchone()
        conn.close()
        text = f"""**اعدادات المجموعه:**
الرابط: {'موجود' if s and s[1] else 'مافي'}
الترحيب: {'موجود' if s and s[2] else 'مافي'}
القوانين: {'موجوده' if s and s[3] else 'مافي'}
القناة: {s[4] if s and s[4] else 'مافي'}
الايدي: {s[5] if s and s[5] else 'افتراضي'}
الحماية: {'مفعله' if p else 'معطله'}"""
        bot.reply_to(message, text)

    # ========== اوامر الوضع ==========
    @bot.message_handler(commands=['انشاء_رابط', 'اضف_رابط', 'ضع_رابط'])
    def انشاء_رابط(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        try:
            link = bot.export_chat_invite_link(message.chat.id)
            conn = sqlite3.connect(DB)
            conn.execute("INSERT OR REPLACE INTO group_settings (chat_id, link) VALUES (?,?)", (message.chat.id, link))
            conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم انشاء الرابط:\n{link}")
        except: bot.reply_to(message, "❌ البوت مش ادمن")

    @bot.message_handler(commands=['مسح_الرابط'])
    def مسح_الرابط(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        conn = sqlite3.connect(DB)
        conn.execute("UPDATE group_settings SET link = NULL WHERE chat_id =?", (message.chat.id,))
        conn.commit(); conn.close()
        bot.reply_to(message, "🗑️ تم مسح الرابط")

    @bot.message_handler(commands=['ضع_قوانين'])
    def ضع_قوانين(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        قوانين = message.text.replace("/ضع_قوانين ", "", 1)
        conn = sqlite3.connect(DB)
        conn.execute("INSERT OR REPLACE INTO group_settings (chat_id, rules) VALUES (?,?)", (message.chat.id, قوانين))
        conn.commit(); conn.close()
        bot.reply_to(message, "✅ تم حفظ القوانين")

    @bot.message_handler(commands=['ضع_الترحيب'])
    def ضع_ترحيب(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        ترحيب = message.text.replace("/ضع_الترحيب ", "", 1)
        conn = sqlite3.connect(DB)
        conn.execute("INSERT OR REPLACE INTO group_settings (chat_id, welcome) VALUES (?,?)", (message.chat.id, ترحيب))
        conn.commit(); conn.close()
        bot.reply_to(message, "✅ تم حفظ رسالة الترحيب")

    @bot.message_handler(commands=['تعيين_الايدي'])
    def تعيين_الايدي(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        نص = message.text.replace("/تعيين_الايدي ", "", 1)
        conn = sqlite3.connect(DB)
        conn.execute("INSERT OR REPLACE INTO group_settings (chat_id, id_text) VALUES (?,?)", (message.chat.id, نص))
        conn.commit(); conn.close()
        bot.reply_to(message, "✅ تم تعيين شكل الايدي")

    @bot.message_handler(commands=['اضف_قناه', 'حذف_قناه'])
    def قناه(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        if "اضف" in message.text:
            قناه = message.text.replace("/اضف_قناه ", "", 1)
            conn = sqlite3.connect(DB)
            conn.execute("INSERT OR REPLACE INTO group_settings (chat_id, channel) VALUES (?,?)", (message.chat.id, قناه))
            conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم حفظ القناة: {قناه}")
        else:
            conn = sqlite3.connect(DB)
            conn.execute("UPDATE group_settings SET channel = NULL WHERE chat_id =?", (message.chat.id,))
            conn.commit(); conn.close()
            bot.reply_to(message, "🗑️ تم حذف القناة")

    @bot.message_handler(commands=['اضف_امر'])
    def اضف_امر(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        try:
            _, cmd, reply = message.text.split(" ", 2)
            conn = sqlite3.connect(DB)
            conn.execute("INSERT OR REPLACE INTO custom_commands VALUES (?,?,?)", (message.chat.id, cmd, reply))
            conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم اضافة الامر /{cmd}")
        except: bot.reply_to(message, "⚠️ الصيغة: /اضف_امر الاسم الرد")

    # ========== اوامر التحميل ==========
    التحميل_مفعل = {}

    @bot.message_handler(commands=['تفعيل_التحميل', 'تعطيل_التحميل'])
    def التحميل(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ ما عندك صلاحية")
        التحميل_مفعل[message.chat.id] = "تفعيل" in message.text
        bot.reply_to(message, f"✅ تم {'تفعيل' if التحميل_مفعل[message.chat.id] else 'تعطيل'} التحميل")

    @bot.message_handler(commands=['بحث'])
    def بحث(message):
        if not التحميل_مفعل.get(message.chat.id, False): return bot.reply_to(message, "❌ التحميل معطل")
        اسم = message.text.replace("/بحث ", "", 1)
        bot.reply_to(message, f"🔍 جاري البحث عن: {اسم}")

    @bot.message_handler(commands=['تيك', 'ساوند'])
    def تحميل_روابط(message):
        if not التحميل_مفعل.get(message.chat.id, False): return bot.reply_to(message, "❌ التحميل معطل")
        رابط = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else ""
        bot.reply_to(message, f"⏳ جاري تحميل: {رابط}")

    # ========== رد على الاوامر المخصصة ==========
    @bot.message_handler(func=lambda m: m.text and m.text.startswith("/") and not m.text.startswith("/اضف_امر"))
    def اوامر_مخصصة(message):
        cmd = message.text.replace("/", "")
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT reply FROM custom_commands WHERE chat_id =? AND command =?", (message.chat.id, cmd)).fetchone()
        conn.close()
        if result: bot.reply_to(message, result[0])
