import sqlite3
import os
import sys
import random

DB_NAME = "dev_data.db"
GROUPS_FILE = "groups.txt" # لحفظ ايدي القروبات

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS replies (chat_id INTEGER, trigger TEXT, reply TEXT, type TEXT, PRIMARY KEY(chat_id, trigger))")
    cursor.execute("CREATE TABLE IF NOT EXISTS gban (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS gmute (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS clips (name TEXT PRIMARY KEY, text TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()

init_db()

MAIN_DEV = 123456789 # غيره لايديك
DEV_PHOTO = "https://t.me/YourPhoto" # حط رابط صورتك
DEV_USERNAME = "@YourUsername" # حط يوزرك
DEV_NAME = "المطور الاساسي" # حط اسمك

def is_dev(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM devs WHERE user_id =?", (user_id,))
    is_secondary = cursor.fetchone()
    conn.close()
    return user_id == MAIN_DEV or is_secondary

def add_dev(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO devs VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def del_dev(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM devs WHERE user_id =?", (user_id,))
    conn.commit()
    conn.close()

def save_group(chat_id):
    if not os.path.exists(GROUPS_FILE):
        open(GROUPS_FILE, 'w').close()
    with open(GROUPS_FILE, 'r') as f: groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, 'a') as f: f.write(f"{chat_id}\n")

def get_all_groups():
    if not os.path.exists(GROUPS_FILE): return []
    with open(GROUPS_FILE, 'r') as f: return [int(x) for x in f.read().splitlines()]

def register_dev_handlers(bot):

    # ===== 1. قائمة اوامر المطور =====
    @bot.message_handler(commands=['المطور2'], chat_types=['group','supergroup','private'])
    def dev_menu(m):
        if not is_dev(m.from_user.id): return
        bot.reply_to(m, """- اهلا بك عزي Dev
━━━━━━━━━━━━
- اضف رد تواصل
- حذف رد تواصل
- ردود التواصل
- ترحيب البوت
- مسح صوره الترحيب
- تعطيل - تفعيل الزاجل
- فتح - قفل ردود MY
- فتح - قفل الاحصائيات
- فتح - قفل حظر العام
━━━━━━━━━━━━
- رفع Dev - تنزيل Dev
- مسح المالكين الاساسيين
- حظر عام - الغاء عام
- كتم عام - الغاء كتم عام
- قائمه العام - مسح المحظورين عام
- مسح المكتومين عام
━━━━━━━━━━━━
- اذاعه + بالرد
- اسم بوتك + غادر
- تحديث - اعاده تشغيل
━━━━━━━━━━━━
- ضع كليشه م1 الى م6 - مسح كليشه م1
━━━━━━━━━━━━""")

    # ===== 2. عرض معلومات المطور بصورة =====
    @bot.message_handler(commands=['المطور'], chat_types=['group','supergroup','private'])
    def show_dev_info(m):
        caption = f"""◂ **معلومات المطور**
━━━━━━━━━━━━
**الاسم:** {DEV_NAME}
**اليوزر:** {DEV_USERNAME}
**الايدي:** `{MAIN_DEV}`
━━━━━━━━━━━━
للتواصل: {DEV_USERNAME}"""

        try:
            bot.send_photo(m.chat.id, DEV_PHOTO, caption=caption, parse_mode="Markdown")
        except:
            bot.reply_to(m, caption, parse_mode="Markdown")

    # حفظ القروبات تلقائي
    @bot.message_handler(chat_types=['group','supergroup'])
    def save_group_id(m): save_group(m.chat.id)

    # ===== 3. معالجة اوامر المطور =====
    @bot.message_handler(func=lambda m: is_dev(m.from_user.id))
    def process_dev(m):
        text = m.text.strip()
        user_id = m.from_user.id
        chat_id = m.chat.id

        # ===== رفع وتنزيل مطور =====
        if text.startswith("رفع Dev") and m.reply_to_message:
            target = m.reply_to_message.from_user.id
            add_dev(target)
            bot.reply_to(m, f"👑 تم رفع {m.reply_to_message.from_user.first_name} مطور ثانوي")
        if text.startswith("تنزيل Dev") and m.reply_to_message:
            target = m.reply_to_message.from_user.id
            del_dev(target)
            bot.reply_to(m, f"🗑️ تم تنزيل {m.reply_to_message.from_user.first_name} من المطورين")

        if text == "مسح المالكين الاساسيين":
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM devs")
            conn.commit()
            conn.close()
            bot.reply_to(m, "🗑️ تم مسح كل المطورين الثانويين")

        # ===== الحظر العام =====
        if text.startswith("حظر عام") and m.reply_to_message:
            target = m.reply_to_message.from_user.id
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO gban VALUES (?)", (target,))
            conn.commit()
            conn.close()
            bot.reply_to(m, f"⛔ تم حظر {m.reply_to_message.from_user.first_name} عام")
        if text.startswith("الغاء عام") and m.reply_to_message:
            target = m.reply_to_message.from_user.id
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gban WHERE user_id =?", (target,))
            conn.commit()
            conn.close()
            bot.reply_to(m, f"✅ تم الغاء الحظر العام")

        if text == "قائمه العام":
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM gban")
            rows = cursor.fetchall()
            conn.close()
            bot.reply_to(m, f"المحظورين عام: {len(rows)}")

        if text == "مسح المحظورين عام":
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gban")
            conn.commit()
            conn.close()
            bot.reply_to(m, "🗑️ تم مسح المحظورين عام")

        # ===== الكتم العام =====
        if text.startswith("كتم عام") and m.reply_to_message:
            target = m.reply_to_message.from_user.id
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO gmute VALUES (?)", (target,))
            conn.commit()
            conn.close()
            bot.reply_to(m, f"🔇 تم كتم {m.reply_to_message.from_user.first_name} عام")
        if text.startswith("الغاء كتم عام") and m.reply_to_message:
            target = m.reply_to_message.from_user.id
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gmute WHERE user_id =?", (target,))
            conn.commit()
            conn.close()
            bot.reply_to(m, f"🔊 تم الغاء الكتم العام")

        if text == "مسح المكتومين عام":
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gmute")
            conn.commit()
            conn.close()
            bot.reply_to(m, "🗑️ تم مسح المكتومين عام")

        # ===== الاذاعة لكل القروبات =====
        if text.startswith("ذيع") and m.reply_to_message:
            groups = get_all_groups()
            count = 0
            for g in groups:
                try:
                    bot.forward_message(g, m.chat.id, m.reply_to_message.message_id)
                    count += 1
                except: pass
            bot.reply_to(m, f"📢 تمت الاذاعة لـ {count} قروب")

        # ===== المغادرة =====
        if "غادر" in text:
            bot.reply_to(m, "👋 تم المغادرة")
            bot.leave_chat(chat_id)

        # ===== التحديث واعادة التشغيل =====
        if text == "تحديث":
            bot.reply_to(m, "🔄 جاري التحديث...")
            os.system("git pull")
        if text == "اعاده تشغيل" or text == "reload":
            bot.reply_to(m, "♻️ جاري اعادة التشغيل...")
            os.execv(sys.executable, ['python'] + sys.argv)

        # ===== الكليشات =====
        if text.startswith("ضع كليشه "):
            parts = text.split(" ", 2)
            if len(parts) == 3:
                name, value = parts[1], parts[2]
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO clips VALUES (?,?)", (name, value))
                conn.commit()
                conn.close()
                bot.reply_to(m, f"✅ تم حفظ {name}")
        if text.startswith("مسح كليشه "):
            name = text.split(" ", 2)[2]
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clips WHERE name =?", (name,))
            conn.commit()
            conn.close()
            bot.reply_to(m, f"🗑️ تم مسح {name}")

    # ===== 4. الرد التلقائي عند مناداة المطور =====
    @bot.message_handler(func=lambda m: True, chat_types=['group','supergroup'])
    def dev_auto_reply(m):
        if not m.text: return

        dev_names = ["المطور", "المبرمج", "dev", "الادمن الاساسي", DEV_USERNAME.lower()]

        if any(name in m.text.lower() for name in dev_names):
            replies = [
                f"نعم؟ المطور {DEV_USERNAME} موجود 😎",
                f"تحتاج المطور؟ كلمه على {DEV_USERNAME}",
                f"المطور مشغول شوي، راسله {DEV_USERNAME}",
                f"ايش فيه؟ المطور {DEV_USERNAME} يسمعك"
            ]
            bot.reply_to(m, random.choice(replies))
