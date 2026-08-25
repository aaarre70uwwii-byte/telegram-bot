import sqlite3
import re
import time
import threading
from telebot import types

DB = "bot.db"
ID_المطور_الاساسي = 7488375443

اقفال = [
    "جمثون","السب","الايرانيه","الكتابه","الاباحي","تعديل_الميديا","التعديل",
    "الفيديو","الصور","الملصقات","المتحركه","الدردشه","الروابط","التاك","البوتات",
    "المعرفات","الكلايش","التكرار","التوجيه","الانلاين","الجهات","الكل","الدخول",
    "الصوت","التوجيه_تقييد","الروابط_تقييد","المتحركه_تقييد","الصور_تقييد","الفيديو_تقييد","البوتات_طرد"
]

تفعيلات = [
    "ضافني","الاذكار","الثنائي","افتاري","التسليه","الكت","الترحيب","الردود","الانذار",
    "التحذير","الايدي","الرابط","اطردني","الحظر","الرفع","التنزيل","التحويل","الحمايه",
    "المنشن","الاقتباسات","الخدميه","اليوتيوب","الايدي_بالصوره","التحقق","ردود_السورس"
]

ذاكرة_التكرار = {}
def تنظيف_الذاكرة():
    while True:
        time.sleep(3600)
        ذاكرة_التكرار.clear()
threading.Thread(target=تنظيف_الذاكرة, daemon=True).start()

def setup(bot, المطور_الاساسي, admins):

    def انشاء_جداول():
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS locks
                    (chat_id INTEGER, lock_name TEXT, status INTEGER DEFAULT 0, PRIMARY KEY(chat_id, lock_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS features
                    (chat_id INTEGER, feature_name TEXT, status INTEGER DEFAULT 1, PRIMARY KEY(chat_id, feature_name))''')
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

    def يقدر_يتصرف(chat_id, user_id):
        return جيب_الرتبة(chat_id, user_id) in ["مدير","منشئ","مالك","مالك_اساسي","مطور","مطور_اساسي"]

    def قفل(chat_id, الاسم):
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO locks VALUES (?,?,1)", (chat_id, الاسم)); conn.commit(); conn.close()
    def فتح(chat_id, الاسم):
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO locks VALUES (?,?,0)", (chat_id, الاسم)); conn.commit(); conn.close()
    def جيب_حالة_القفل(chat_id, الاسم):
        conn = sqlite3.connect(DB); result = conn.execute("SELECT status FROM locks WHERE chat_id =? AND lock_name =?", (chat_id, الاسم)).fetchone(); conn.close()
        return result[0] if result else 0
    def تفعيل(chat_id, الاسم):
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO features VALUES (?,?,1)", (chat_id, الاسم)); conn.commit(); conn.close()
    def تعطيل(chat_id, الاسم):
        conn = sqlite3.connect(DB); conn.execute("INSERT OR REPLACE INTO features VALUES (?,?,0)", (chat_id, الاسم)); conn.commit(); conn.close()
    def جيب_حالة_التفعيل(chat_id, الاسم):
        conn = sqlite3.connect(DB); result = conn.execute("SELECT status FROM features WHERE chat_id =? AND feature_name =?", (chat_id, الاسم)).fetchone(); conn.close()
        return result[0] if result else 1
    def عقاب_بالتقييد(chat_id, user_id):
        try: bot.restrict_chat_member(chat_id, user_id, until_date=int(time.time() + 300), permissions=types.ChatPermissions())
        except: pass

    @bot.message_handler(commands=[f'قفل_{x}' for x in اقفال] + [f'فتح_{x}' for x in اقفال])
    def اوامر_القفل(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمدير فما فوق")
        command = message.text.replace("/", "")
        if command.startswith("قفل_"):
            lock_name = command.replace("قفل_", "")
            قفل(message.chat.id, lock_name)
            bot.reply_to(message, f"🔒 تم قفل {lock_name}")
        else:
            lock_name = command.replace("فتح_", "")
            فتح(message.chat.id, lock_name)
            bot.reply_to(message, f"🔓 تم فتح {lock_name}")

    @bot.message_handler(commands=['قفل_الكل', 'فتح_الكل'])
    def الكل(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمدير فما فوق")
        if "قفل" in message.text:
            for lock in اقفال: قفل(message.chat.id, lock)
            bot.reply_to(message, "🔒 تم قفل الكل")
        else:
            for lock in اقفال: فتح(message.chat.id, lock)
            bot.reply_to(message, "🔓 تم فتح الكل")

    @bot.message_handler(commands=[f'تفعيل_{x}' for x in تفعيلات] + [f'تعطيل_{x}' for x in تفعيلات])
    def اوامر_التفعيل(message):
        if not يقدر_يتصرف(message.chat.id, message.from_user.id): return bot.reply_to(message, "❌ للمدير فما فوق")
        command = message.text.replace("/", "")
        if command.startswith("تفعيل_"):
            feature_name = command.replace("تفعيل_", "")
            تفعيل(message.chat.id, feature_name)
            bot.reply_to(message, f"✅ تم تفعيل {feature_name}")
        else:
            feature_name = command.replace("تعطيل_", "")
            تعطيل(message.chat.id, feature_name)
            bot.reply_to(message, f"❌ تم تعطيل {feature_name}")

    @bot.message_handler(content_types=['text','photo','video','sticker','animation','audio','voice','document','contact'])
    def مراقبة_الرسائل(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id == bot.get_me().id: return
        if يقدر_يتصرف(chat_id, user_id): return

        نص = message.text or message.caption or ""

        if جيب_حالة_القفل(chat_id, "الدردشه") == 1: return bot.delete_message(chat_id, message.message_id)
        if جيب_حالة_القفل(chat_id, "الكتابه") == 1 and message.content_type == "text": return bot.delete_message(chat_id, message.message_id)

        if جيب_حالة_القفل(chat_id, "الروابط") == 1 and re.search(r'(t\.me|telegram\.me|http|www)', نص):
            if جيب_حالة_القفل(chat_id, "الروابط_تقييد") == 1: عقاب_بالتقييد(chat_id, user_id)
            return bot.delete_message(chat_id, message.message_id)

        if جيب_حالة_القفل(chat_id, "التوجيه") == 1 and (message.forward_from or message.forward_sender_name):
            if جيب_حالة_القفل(chat_id, "التوجيه_تقييد") == 1: عقاب_بالتقييد(chat_id, user_id)
            return bot.delete_message(chat_id, message.message_id)

        if جيب_حالة_القفل(chat_id, "الصور") == 1 and message.content_type == "photo":
            if جيب_حالة_القفل(chat_id, "الصور_تقييد") == 1: عقاب_بالتقييد(chat_id, user_id)
            return bot.delete_message(chat_id, message.message_id)
        if جيب_حالة_القفل(chat_id, "الفيديو") == 1 and message.content_type == "video":
            if جيب_حالة_القفل(chat_id, "الفيديو_تقييد") == 1: عقاب_بالتقييد(chat_id, user_id)
            return bot.delete_message(chat_id, message.message_id)
        if جيب_حالة_القفل(chat_id, "الملصقات") == 1 and message.content_type == "sticker": return bot.delete_message(chat_id, message.message_id)
        if جيب_حالة_القفل(chat_id, "المتحركه") == 1 and message.content_type == "animation":
            if جيب_حالة_القفل(chat_id, "المتحركه_تقييد") == 1: عقاب_بالتقييد(chat_id, user_id)
            return bot.delete_message(chat_id, message.message_id)
        if جيب_حالة_القفل(chat_id, "الصوت") == 1 and message.content_type in ["voice","audio"]: return bot.delete_message(chat_id, message.message_id)

        if جيب_حالة_القفل(chat_id, "التاك") == 1 and re.search(r'@\w+', نص): return bot.delete_message(chat_id, message.message_id)
        if جيب_حالة_القفل(chat_id, "المعرفات") == 1 and re.search(r'#\w+', نص): return bot.delete_message(chat_id, message.message_id)

        if جيب_حالة_القفل(chat_id, "السب") == 1:
            كلمات_السب = ["كلب","حمار","غبي","زباله","تافه","اهبل"]
            if any(k in نص for k in كلمات_السب): return bot.delete_message(chat_id, message.message_id)

        if جيب_حالة_القفل(chat_id, "الايرانيه") == 1 and re.search(r'[پچژگکی]', نص): return bot.delete_message(chat_id, message.message_id)
        if جيب_حالة_القفل(chat_id, "الكلايش") == 1 and len(نص) > 400: return bot.delete_message(chat_id, message.message_id)

        if جيب_حالة_القفل(chat_id, "التكرار") == 1:
            key = f"{chat_id}_{user_id}"
            if key in ذاكرة_التكرار and ذاكرة_التكرار[key] == نص:
                return bot.delete_message(chat_id, message.message_id)
            ذاكرة_التكرار[key] = نص

        if جيب_حالة_القفل(chat_id, "البوتات") == 1 and message.new_chat_members:
            for new_member in message.new_chat_members:
                if new_member.is_bot:
                    bot.delete_message(chat_id, message.message_id)
                    if جيب_حالة_القفل(chat_id, "البوتات_طرد") == 1:
                        try: bot.ban_chat_member(chat_id, new_member.id)
                        except: pass

    @bot.message_handler(commands=['الاقفال'])
    def الاقفال(message):
        chat_id = message.chat.id
        text = "<b>حالة الاقفال:</b>\n━━━━━━━━━━━━\n"
        for lock in اقفال:
            حالة = "🔒" if جيب_حالة_القفل(chat_id, lock) == 1 else "🔓"
            text += f"{حالة} {lock}\n"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=['التفعيلات'])
    def التفعيلات(message):
        chat_id = message.chat.id
        text = "<b>حالة التفعيلات:</b>\n━━━━━━━━━━━━\n"
        for feat in تفعيلات:
            حالة = "✅" if جيب_حالة_التفعيل(chat_id, feat) == 1 else "❌"
            text += f"{حالة} {feat}\n"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=['م3'])
    def م3(message):
        bot.reply_to(message, """<b>• اهلا بك في قائمة القفل - التعطيل
━━━━━━━━━━━━
- اوامر القفل والفتح :
• قفل_جمثون - فتح_جمثون
• قفل_السب - فتح_السب
• قفل_الايرانيه - فتح_الايرانيه
• قفل_الكتابه - فتح_الكتابه
• قفل_الاباحي - فتح_الاباحي
• قفل_تعديل_الميديا - فتح_تعديل_الميديا
• قفل_التعديل - فتح_التعديل
• قفل_الفيديو - فتح_الفيديو
• قفل_الصور - فتح_الصور
• قفل_الملصقات - فتح_الملصقات
• قفل_المتحركه - فتح_المتحركه
• قفل_الدردشه - فتح_الدردشه
• قفل_الروابط - فتح_الروابط
• قفل_التاك - فتح_التاك
• قفل_البوتات - فتح_البوتات
• قفل_المعرفات - فتح_المعرفات
• قفل_البوتات_بالطرد
• قفل_الكلايش - فتح_الكلايش
• قفل_التكرار - فتح_التكرار
• قفل_التوجيه - فتح_التوجيه
• قفل_الانلاين - فتح_الانلاين
• قفل_الجهات - فتح_الجهات
• قفل_الكل - فتح_الكل
• قفل_الدخول - فتح_الدخول
• قفل_الصوت - فتح_الصوت
• قفل_التوجيه_بالتقييد - فتح_التوجيه_بالتقييد
• قفل_الروابط_بالتقييد - فتح_الروابط_بالتقييد
• قفل_المتحركه_بالتقييد - فتح_المتحركه_بالتقييد
• قفل_الصور_بالتقييد - فتح_الصور_بالتقييد
• قفل_الفيديو_بالتقييد - فتح_الفيديو_بالتقييد

- اوامر التفعيل - التعطيل :
• تفعيل_ضافني - تعطيل_ضافني
• تفعيل_الاذكار - تعطيل_الاذكار
• تفعيل_الثنائي - تعطيل_الثنائي
• تفعيل_افتاري - تعطيل_افتاري
• تفعيل_التسليه - تعطيل_التسليه
• تفعيل_الكت - تعطيل_الكت
• تفعيل_الترحيب - تعطيل_الترحيب
• تفعيل_الردود - تعطيل_الردود
• تفعيل_الانذار - تعطيل_الانذار
• تفعيل_التحذير - تعطيل_التحذير
• تفعيل_الايدي - تعطيل_الايدي
• تفعيل_الرابط - تعطيل_الرابط
• تفعيل_اطردني - تعطيل_اطردني
• تفعيل_الحظر - تعطيل_الحظر
• تفعيل_الرفع - تعطيل_الرفع
• تفعيل_التنزيل - تعطيل_التنزيل
• تفعيل_التحويل - تعطيل_التحويل
• تفعيل_الحمايه - تعطيل_الحمايه
• تفعيل_المنشن - تعطيل_المنشن
• تفعيل_وضع_الاقتباسات - تعطيل_وضع_الاقتباسات
• تفعيل_الخدميه - تعطيل_الخدميه
• تفعيل_اليوتيوب - تعطيل_اليوتيوب
• تفعيل_الايدي_بالصوره - تعطيل_الايدي_بالصوره
• تفعيل_التحقق - تعطيل_التحقق
• تفعيل_ردود_السورس - تعطيل_ردود_السورس
━━━━━━━━━━━━</b>""", parse_mode="HTML")

    print("✅ تم تحميل: cog3.py - ملف القفل والفتح كامل")
