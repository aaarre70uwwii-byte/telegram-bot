import sqlite3
import os
import sys
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443 # انت بس

def setup_dev(bot):

    def جيب_الرتبة(chat_id, user_id):
        if user_id == ID_المطور_الاساسي: return "مطور_اساسي"
        conn = sqlite3.connect(DB)
        result = conn.execute("SELECT role FROM ranks WHERE chat_id =? AND user_id =?",(chat_id, user_id)).fetchone()
        conn.close()
        return result[0] if result else "عضو"

    def مطور_بس(message):
        if message.from_user.id!= ID_المطور_الاساسي:
            bot.reply_to(message, "❌ هذا الامر للمطور الاساسي فقط")
            return False
        return True

    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        conn.execute("CREATE TABLE IF NOT EXISTS dev_settings (id INTEGER PRIMARY KEY, تواصل TEXT, ترحيب_بوت TEXT, صورة_ترحيب TEXT, زاجل INTEGER DEFAULT 1, احصائيات INTEGER DEFAULT 1, حظر_عام INTEGER DEFAULT 1, ردود_my INTEGER DEFAULT 1)")
        conn.execute("CREATE TABLE IF NOT EXISTS global_bans (user_id INTEGER PRIMARY KEY, reason TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS global_mutes (user_id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS global_ranks (user_id INTEGER PRIMARY KEY, role TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS global_replies (word TEXT PRIMARY KEY, reply TEXT, type TEXT DEFAULT 'نص')")
        conn.execute("CREATE TABLE IF NOT EXISTS clich (menu INTEGER PRIMARY KEY, text TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)")
        conn.commit(); conn.close()
    انشاء_جداول()

    def جيب_اعداد(message, field):
        conn = sqlite3.connect(DB)
        result = conn.execute(f"SELECT {field} FROM dev_settings WHERE id = 1").fetchone()
        conn.close()
        return result[0] if result else 1

    # ========== التواصل والترحيب ==========
    @bot.message_handler(commands=['اضف_رد_تواصل'])
    def اضف_رد_تواصل(message):
        if not مطور_بس(message): return
        رد = message.text.replace("/اضف_رد_تواصل ", "", 1)
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO dev_settings (id, تواصل) VALUES (1,?)", (رد,)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم حفظ رد التواصل:\n{رد}")

    @bot.message_handler(commands=['ترحيب_البوت'])
    def ترحيب_بوت(message):
        if not مطور_بس(message): return
        رد = message.text.replace("/ترحيب_البوت ", "", 1)
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO dev_settings (id, ترحيب_بوت) VALUES (1,?)", (رد,)); conn.commit(); conn.close()
        bot.reply_to(message, f"✅ تم حفظ ترحيب البوت")

    @bot.message_handler(commands=['مسح_صوره_الترحيب'])
    def مسح_صورة(message):
        if not مطور_بس(message): return
        conn = sqlite3.connect(DB); conn.execute("UPDATE dev_settings SET صورة_ترحيب = NULL WHERE id = 1"); conn.commit(); conn.close()
        bot.reply_to(message, "🗑️ تم مسح صورة الترحيب")

    # ========== الاذاعة ==========
    @bot.message_handler(commands=['ذيع'])
    def ذيع(message):
        if not مطور_بس(message): return
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الرسالة")
        conn = sqlite3.connect(DB)
        chats = conn.execute("SELECT DISTINCT chat_id FROM group_settings").fetchall()
        conn.close()
        count = 0
        for c in chats:
            try: bot.copy_message(c[0], message.chat.id, message.reply_to_message.message_id); count+=1
            except: pass
        bot.reply_to(message, f"✅ تم الاذاعة لـ {count} مجموعة")

    # ========== الحظر العام ==========
    @bot.message_handler(commands=['حظر_عام', 'كتم_عام'])
    def حظر_عام(message):
        if not مطور_بس(message): return
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        user_id = message.reply_to_message.from_user.id
        conn = sqlite3.connect(DB)
        if "حظر" in message.text: conn.execute("INSERT OR IGNORE INTO global_bans VALUES (?, 'حظر عام')", (user_id,)); text = "🔨 تم حظر عام"
        else: conn.execute("INSERT OR IGNORE INTO global_mutes VALUES (?)", (user_id,)); text = "🔇 تم كتم عام"
        conn.commit(); conn.close(); bot.reply_to(message, text)

    @bot.message_handler(commands=['الغاء_حظر_عام', 'الغاء_كتم_عام'])
    def الغاء_عام(message):
        if not مطور_بس(message): return
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        user_id = message.reply_to_message.from_user.id
        conn = sqlite3.connect(DB)
        if "حظر" in message.text: conn.execute("DELETE FROM global_bans WHERE user_id =?", (user_id,)); text = "✅ تم الغاء الحظر العام"
        else: conn.execute("DELETE FROM global_mutes WHERE user_id =?", (user_id,)); text = "✅ تم الغاء الكتم العام"
        conn.commit(); conn.close(); bot.reply_to(message, text)

    @bot.message_handler(commands=['قائمه_العام', 'مسح_المحظورين_عام', 'مسح_المكتومين_عام'])
    def عام(message):
        if not مطور_بس(message): return
        conn = sqlite3.connect(DB)
        if "مسح" in message.text:
            if "محظورين" in message.text: conn.execute("DELETE FROM global_bans"); text = "🗑️ تم مسح المحظورين"
            else: conn.execute("DELETE FROM global_mutes"); text = "🗑️ تم مسح المكتومين"
        else:
            bans = conn.execute("SELECT user_id FROM global_bans").fetchall()
            mutes = conn.execute("SELECT user_id FROM global_mutes").fetchall()
            text = f"**المحظورين عام:** {len(bans)}\n**المكتومين عام:** {len(mutes)}"
        conn.commit(); conn.close(); bot.reply_to(message, text)

    # ========== الرتب العامة ==========
    @bot.message_handler(commands=['رفع_dev', 'تنزيل_dev'])
    def رفع_مطور(message):
        if not مطور_بس(message): return
        if not message.reply_to_message: return bot.reply_to(message, "⚠️ رد على الشخص")
        user_id = message.reply_to_message.from_user.id
        conn = sqlite3.connect(DB)
        if "رفع" in message.text:
            conn.execute("INSERT OR REPLACE INTO global_ranks VALUES (?, 'مطور_ثانوي')", (user_id,)) # تم التصحيح هنا
            text = "✅ تم رفع مطور ثانوي"
        else:
            conn.execute("DELETE FROM global_ranks WHERE user_id =?", (user_id,)); text = "❌ تم تنزيل مطور ثانوي"
        conn.commit(); conn.close(); bot.reply_to(message, text)

    @bot.message_handler(commands=['قائمه_الرتب_العامه', 'مسح_رتب_العام'])
    def رتب_عام(message):
        if not مطور_بس(message): return
        conn = sqlite3.connect(DB)
        if "مسح" in message.text: conn.execute("DELETE FROM global_ranks"); text = "🗑️ تم مسح الرتب العامة"
        else:
            ranks = conn.execute("SELECT user_id, role FROM global_ranks").fetchall()
            text = "**الرتب العامة:**\n" + "\n".join([f"{r[0]} - {r[1]}" for r in ranks])
        conn.commit(); conn.close(); bot.reply_to(message, text if text else "❌ مافي رتب")

    # ========== الفتح والقفل ==========
    @bot.message_handler(commands=['فتح_الاحصائيات', 'قفل_الاحصائيات', 'فتح_حظر_العام', 'قفل_حظر_العام', 'فتح_ردود_my', 'قفل_ردود_my'])
    def فتح_قفل(message):
        if not مطور_بس(message): return
        cmd = message.text.replace("/", "")
        field = "احصائيات" if "احصائيات" in cmd else "حظر_عام" if "حظر" in cmd else "ردود_my"
        val = 1 if "فتح" in cmd else 0
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO dev_settings (id, "+field+") VALUES (1,?)", (val,)); conn.commit(); conn.close()
        bot.reply_to(message, f"{'✅' if val else '❌'} تم {'فتح' if val else 'قفل'} {field}")

    # ========== الردود العامة ==========
    @bot.message_handler(commands=['اضف_رد_عام', 'اضف_رد_متعدد_عام'])
    def اضف_رد_عام(message):
        if not مطور_بس(message): return
        try:
            _, word, reply = message.text.split(" ", 2)
            type = "متعدد" if "متعدد" in message.text else "نص"
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO global_replies VALUES (?,?,?)", (word, reply, type)); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم اضافة الرد العام: {word}")
        except: bot.reply_to(message, "⚠️ الصيغة: /اضف_رد_عام الكلمة الرد")

    @bot.message_handler(commands=['الردود_العامه', 'مسح_الردود_العامه'])
    def ردود_عامه(message):
        if not مطور_بس(message): return
        conn = sqlite3.connect(DB)
        if "مسح" in message.text: conn.execute("DELETE FROM global_replies"); text = "🗑️ تم مسح الردود العامة"
        else: results = conn.execute("SELECT word, reply FROM global_replies").fetchall(); text = "**الردود العامة:**\n" + "\n".join([f"{r[0]} = {r[1]}" for r in results])
        conn.commit(); conn.close(); bot.reply_to(message, text if text else "❌ مافي ردود")

    # ========== الكلايش ==========
    @bot.message_handler(commands=['ضع_كليشه_م1', 'مسح_كليشه_م1', 'ضع_كليشه_م2', 'مسح_كليشه_م2', 'ضع_كليشه_م3', 'مسح_كليشه_م3', 'ضع_كليشه_م4', 'مسح_كليشه_م4', 'ضع_كليشه_م5', 'مسح_كليشه_م5', 'ضع_كليشه_م6', 'مسح_كليشه_م6'])
    def كليشه(message):
        if not مطور_بس(message): return
        cmd = message.text.replace("/", ""); num = int(cmd[-1])
        if "ضع" in cmd:
            text = message.text.split(" ", 1)[1]
            conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO clich VALUES (?,?)", (num, text)); conn.commit(); conn.close()
            bot.reply_to(message, f"✅ تم حفظ كليشة م{num}")
        else:
            conn = sqlite3.connect(DB); conn.execute("DELETE FROM clich WHERE menu =?", (num,)); conn.commit(); conn.close()
            bot.reply_to(message, f"🗑️ تم مسح كليشة م{num}")

    # ========== اعادة التشغيل ==========
    @bot.message_handler(commands=['اعاده_تشغيل', 'reload', 'تحديث'])
    def اعاده_تشغيل(message):
        if not مطور_بس(message): return
        bot.reply_to(message, "🔄 جاري اعادة التشغيل...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # ========== فلتر الحظر العام ==========
    @bot.message_handler(content_types=['text', 'photo', 'video'])
    def فلتر_عام(message):
        if جيب_اعداد(message, "حظر_عام") == 0: return
        conn = sqlite3.connect(DB)
        banned = conn.execute("SELECT 1 FROM global_bans WHERE user_id =?", (message.from_user.id,)).fetchone()
        muted = conn.execute("SELECT 1 FROM global_mutes WHERE user_id =?", (message.from_user.id,)).fetchone()
        conn.close()
        if banned:
            try: bot.kick_chat_member(message.chat.id, message.from_user.id)
            except: pass
        if muted:
            try: bot.delete_message(message.chat.id, message.message_id)
            except: pass
