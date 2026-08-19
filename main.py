import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import random
import os

# ==========================================
# ⚙️ قسم المتغيرات والإعدادات (تعديل هنا بسهولة)
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN") # يقرا التوكن من المتغيرات حق Railway

if not BOT_TOKEN:
    raise ValueError("CRITICAL ERROR: 'BOT_TOKEN' environment variable is missing! ضع التوكن في Variables")

CHANNEL_URL = "https://t.me/eeccvu" # رابط قناة التحديثات الخاص بك

# نصوص واجهات الأزرار والرسائل الأساسية مأخوذة من تصاميمك بالظبط
MAIN_MENU_TEXT = """↤اهلا فيك بعد عمري في قائمه اوامر : ✓ 𝐓𝐢𝐚 :
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه
━━━━━━━━━━━━
                  1. 2. 3.
                  4. 5. 6"""

M1_TEXT = """↢ أهلاً فيك يا حلو ♡
• قائمة اوامر الادمنيه

⚙️ اوامر الرفع والتنزيل:
• رفع - تنزيل مالك اساسي
↢ رفع - تنزيل مالك
↢ رفع - تنزيل مشرف
↢ رفع - تنزيل منشئ
↢ رفع - تنزيل مدير
↢ رفع - تنزيل ادمن
↢ رفع - تنزيل مميز
↢ تنزيل الكل - لازاله جميع الرتب اعلاه

🗑️ اوامر المسح :
• مسح + عدد
↢ مسح بالرد
↢ مسح الايدي
↢ مسح الكل
↢ مسح المنشئين
↢ مسح المدراء
↢ مسح المالكين
↢ مسح الادمنيه

🚫 اوامر الطرد والحظر :
↢ تقييد + الوقت
↢ حظر
↢ طرد
↢ كتم
↢ تقييد
↢ الغاء الحظر
↢ الغاء الكتم
↢ فك التقييد
↢ رفع القيود"""

M2_TEXT = """حياك الله في قائمة الاعدادات :
• اكتب في قروبك كذا ↓
↢ الرابط
↢ المالكين
↢ المالكين الاساسين
↢ المنشئين
↢ الادمنيه
↢ المدراء
↢ المميزين
↢ المحظورين
↢ القوانين
↢ المكتومين
↢ معلوماتي
↢ الحمايه
↢ الاعدادت
↢ المجموعه

⚙️ اوامر وضع الاعدادات :
↢ مسح الرابط
↢ انشاء رابط
↢ ضع الترحيب
↢ ضـع رابط
↢ اضف امر
↢ تعيين الايدي"""

M3_TEXT = """- حياك في قائمة القفل - التعطيل :

🔒 اولا : اوامر القفل والفتح :
↢ قفل - فتح جمثون
↢ قفل - فتح السب
↢ قفل - فتح الايرانيه
↢ قفل - فتح الكتابه
↢ قفل - فتح التعديل
↢ قفل - فتح الفيديو
↢ قفل - فتح الصور
↢ قفل - فتح الملصقات
↢ قفل - فتح المتحركه
↢ قفل - فتح الدردشه
↢ قفل - فتح الروابط
↢ قفل - فتح التاك
↢ قفل - فتح البوتات
↢ قفل - فتح المعرفات
↢ قفل - البوتات بالطرد
↢ قفل - فتح الكلايش
↢️ قفل - فتح التكرار
↢ قفل - فتح التوجيه
↢ قفل - فتح الانلاين
↢ قفل - فتح الجهات
↢ قفل - فتح الكل
↢ قفل - فتح الدخول
↢ قفل - فتح الصوت

⚙️ ثانيا : اوامر التفعيل - التعطيل :
↢ تفعيل - تعطيل ضافني
↢ تفعيل - تعطيل الاذكار
↢ تفعيل - تعطيل الثنائي
↢ تفعيل - تعطيل افتاري
↢ تفعيل - تعطيل التسليه
↢ تفعيل - تعطيل الكت
↢ تفعيل - تعطيل الترحيب
↢ تفعيل - تعطيل الردود
↢ تفعيل - تعطيل الانذار
↢ تفعيل - تعطيل التحذير
↢ تفعيل - تعطيل الايدي
↢ تفعيل - تعطيل الرابط
↢ تفعيل - تعطيل اطردني
↢ تفعيل - تعطيل الحظر
↢ تفعيل - تعطيل الرفع
↢ تفعيل - تعطيل التنزيل
↢ تفعيل - تعطيل التحويل
↢ تفعيل - تعطيل الحمايه
↢ تفعيل - تعطيل المنشن
↢ تفعيل - تعطيل وضع الاقتباسات
↢ تفعيل - تعطيل الخدميه
↢ تفعيل - تعطيل الايدي بالصوره
↢ تفعيل - تعطيل التحقق"""

M4_TEXT = """اهلا بك عزيزي
- اوامر التسليه :
━━━━━━━━━━━━
🎯 اوامر تسلية تظهر بالايدي :
• رفع - تنزيل : حمار : الحمير
• رفع بقلبي : تنزيل من قلبي

👥 للجروب:
• رفع + اسم اختياري
• مسح رتب التسليه
• رتب التسليه
• تعطيل التسليه
━━━━━━━━━━━━
🌍 للعام:
• رفع عام + اسم اختياري
• رتب التسليه عام
• مسح رتب التسليه
━━━━━━━━━━━━
💍 أوامر أخرى:
• طلاق - زواج
• زوجي - زوجتي
• تتزوجني
• اكتموه (تصويت)
• تعطيل - تفعيل : اكتموه
• تعطيل - تفعيل : زوجني"""

M5_TEXT = """- اهلا بك عزي Dev
• اضف رد تواصل : حذف رد تواصل : ردود التواصل
• ترحيب البوت : مسح صوره الترحيب
• تعطيل : اسم بوتك + غادر
• تعطيل - تفعيل الزاجل
• مسح المالكين الاساسيين
• ذيع + ايدي المجموعه - بالرد
• فتح - قفل ردود MY
• رفع - تنزيل Dev = مطور ثانوي
• فتح - قفل الاحصائيات
• فتح - قفل حظر العام

🚫 أوامر العام والحظر:
• حظر - كتم عام
• حظر - الغاء حظر بالرد للتواصل
• مسح المحظورين - المحظورين للتواصل
• قائمه العام : قائمه الرتب العامه
• الغاء كتم عام - الغاء عام
• مسح المكتومين عام : مسح المحظورين عام
• تغير الرتب العام : مسح رتب العام : مسح رتبه عام

💬 أوامر الردود العامة:
• الردود العامه : الردود المتعدده العامه
• مسح الردود العامه : مسح الردود المتعدده العامه
• اضف رد عام : اضف رد متعدد عام
• اضف ميزة: (صور،صوت،فيديو،فويسات،متحركه)🎮 أوامر الألعاب والكليشات:
• اضف لعبه عام (3 العاب كتابيه)
• مسح - ضع كليشه الالعاب
• مسح - ضع كليشه (م1، م2، م3، م4، م5، م6)
• تحديث : اعاده تشغيل - reload"""

M6_TEXT = """• اهلا بك عزيزي
- اوامر الخدميه :
━━━━━━━━━━━━
📊 ألعاب ونسب تفاعلية:
• نسبه الحب
• نسبه الغباء - بالرد
• تحبه - بالرد
• نسبه انوثتها - بالرد | نسبه رجولته - بالرد
• شبيهي - شبيهتي

💌 أوامر الهدايا والرسائل:
• ارسل + الكلام + اليوزر زاجل
• صيح | صيح + اليوزر يزعجه خاص
• اهديه بالرد | اهديه + يوزر الشخص

👤 الحساب والصور الشخصية:
• شرايك في افتاري | افتاره بالرد
• البايو بالرد
• من ضافني

🔍 البحث والتحميل:
• البوت السحري
• قوقل + كلام البحث
• تطبيق + اسم التطبيق
• تحميل لعبه + اسم اللعبه
• معنى + اسمك | العمر + عمرك | زخرف + اسمك
• ترجم عربي + الكلام | ترجم انقليزي + الكلام

📖 محتوى ديني وثقافي:
• قران | اذكار
• شعر ، قصائد | اقتباسات | ثريد | قصص ، كتب

🎥 الميديا والترفيه:
• اطربني | اغاني
• هيدرات | جداريات | ميمز | ايدت
• قيفات (اطفال ، رومنسيه ، كوكسال ، كيبوب ، عيال ، بنات)
• افتارات (بنات ، عيال ، فنانين ، تطقيم ، كيبوب ، انمي)

🛠️ أوامر تطوير وإضافات:
• نادي المطور | تفعيل كليشة المطور : الافتار والبايو
• اضف رد المالك | اضف رد انلاين | اضف رد متعدد
• افلام

📥 التحميل وتحويل الصيغ:
• ساوند + الرابط
• تيك + الرابط
• تويتر + الرابط
• تحويل الصيغ (صوت - تحويل - متحركه - بصمه) بالرد على الفيديو
━━━━━━━━━━━━"""

# نصوص الأزرار الشفافة
TEXT_HIDE_BUTTON = "❌ اخفاء الاوامر"
TEXT_UPDATES_BUTTON = "📢 تحديثات 𝐓𝐢𝐚"
TEXT_BACK_BUTTON = "⬅️ عودة للقائمة الرئيسية"
NOTIFICATION_HIDE = "تم إخفاء القائمة"

# ==========================================
# 🎛️ قسم البناء وقاعدة البيانات والوظائف التنفيذية
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# إنشاء وتجهيز جداول البيانات للحفظ التلقائي واللانهائي للرتب والإعدادات والقفل
def init_db():
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            chat_id INTEGER,
            user_id INTEGER,
            role TEXT,
            PRIMARY KEY (chat_id, user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locks (
            chat_id INTEGER,
            lock_type TEXT,
            status INTEGER,
            PRIMARY KEY (chat_id, lock_type)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- دوال التحكم بقاعدة البيانات ---
def set_user_role(chat_id, user_id, role):
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    if role is None:
        cursor.execute("DELETE FROM roles WHERE chat_id =? AND user_id =?", (chat_id, user_id))
    else:
        cursor.execute("INSERT OR REPLACE INTO roles (chat_id, user_id, role) VALUES (?,?,?)", (chat_id, user_id, role))
    conn.commit()
    conn.close()

def get_user_role(chat_id, user_id):
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM roles WHERE chat_id =? AND user_id =?", (chat_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "عضو"

def set_lock_status(chat_id, lock_type, status):
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO locks (chat_id, lock_type, status) VALUES (?,?,?)", (chat_id, lock_type, status))
    conn.commit()
    conn.close()

def is_lock_active(chat_id, lock_type):
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM locks WHERE chat_id =? AND lock_type =?", (chat_id, lock_type))
    row = cursor.fetchone()
    conn.close()
    return row[0] == 1 if row else False

def is_user_admin(chat_id, user_id):
    if chat_id == user_id: # في المحادثة الخاصة
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

# --- بناء واجهات لوحة التحكم (Keyboards) ---
def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    row1 = [InlineKeyboardButton("1️⃣", callback_data="cmd_1"),
            InlineKeyboardButton("2️⃣", callback_data="cmd_2"),
            InlineKeyboardButton("3️⃣", callback_data="cmd_3")]
    row2 = [InlineKeyboardButton("4️⃣", callback_data="cmd_4"),
            InlineKeyboardButton("5️⃣", callback_data="cmd_5"),
            InlineKeyboardButton("6️⃣", callback_data="cmd_6")]
    markup.row(*row1)
    markup.row(*row2)
    markup.row(InlineKeyboardButton(TEXT_HIDE_BUTTON, callback_data="hide_menu"))
    markup.row(InlineKeyboardButton(TEXT_UPDATES_BUTTON, url=CHANNEL_URL))
    return markup

def sub_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(TEXT_BACK_BUTTON, callback_data="back_to_main"))
    markup.row(InlineKeyboardButton(TEXT_UPDATES_BUTTON, url=CHANNEL_URL))
    return markup

# --- معالجة واستقبال الأوامر والرسائل النصية والوظائف الحقيقية ---

@bot.message_handler(commands=['start', 'help', 'menu'])
@bot.message_handler(func=lambda msg: msg.text == "الاوامر")
def send_menu(message):
    bot.send_message(message.chat.id, MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())

# 👤 تطبيق وظيفة "الايدي" وسحب الرتب الحقيقية والمحفوظة
@bot.message_handler(func=lambda msg: msg.text in ["ايدي", "الايدي", "معلوماتي"])
def get_user_id(message):
    user = message.from_user
    chat_member = bot.get_chat_member(message.chat.id, user.id)

    if chat_member.status == 'creator':
        role = "المالك الأساسي 👑"
    elif chat_member.status == 'administrator':
        role = "مشرف المجموعة 🛡️"
    else:
        role = get_user_role(message.chat.id, user.id)

    reply_text = f"👤 معلوماتك يا حلو:\n\n" \
                 f"↢ اسمك: {user.first_name}\n" \
                 f"↢ يوزرك: @{user.username if user.username else 'لا يوجد'}\n" \
                 f"↢ ايديك: `{user.id}`\n" \
                 f"↢ رتبتك: {role}"
    bot.reply_to(message, reply_text)

# ==========================================
# معالج الازرار
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_menu(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "hide_menu":
        bot.delete_message(chat_id, message_id)
        bot.answer_callback_query(call.id, NOTIFICATION_HIDE)
        return

    if call.data == "back_to_main":
        bot.edit_message_text(MAIN_MENU_TEXT, chat_id, message_id, reply_markup=main_menu_keyboard())

    elif call.data == "cmd_1":
        bot.edit_message_text(M1_TEXT, chat_id, message_id, reply_markup=sub_menu_keyboard())

    elif call.data == "cmd_2":
        bot.edit_message_text(M2_TEXT, chat_id, message_id, reply_markup=sub_menu_keyboard())

    elif call.data == "cmd_3":
        bot.edit_message_text(M3_TEXT, chat_id, message_id, reply_markup=sub_menu_keyboard())

    elif call.data == "cmd_4":
        bot.edit_message_text(M4_TEXT, chat_id, message_id, reply_markup=sub_menu_keyboard())

    elif call.data == "cmd_5":
        bot.edit_message_text(M5_TEXT, chat_id, message_id, reply_markup=sub_menu_keyboard())

    elif call.data == "cmd_6":
        bot.edit_message_text(M6_TEXT, chat_id, message_id, reply_markup=sub_menu_keyboard())

    bot.answer_callback_query(call.id)

print("BOT STARTED...")
bot.infinity_polling(none_stop=True) 
# ==========================================
# باقي اوامر م1 : اوامر الادمنيه
# ==========================================

@bot.message_handler(func=lambda msg: msg.text == "الادمنيه")
def list_admins(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    admins = bot.get_chat_administrators(message.chat.id)
    text = "↢ قائمة الادمنيه:\n"
    for admin in admins:
        name = admin.user.first_name
        text += f"- {name}\n"
    bot.reply_to(message, text)

@bot.message_handler(func=lambda msg: msg.text == "المشرفين")
def list_roles(message):
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, role FROM roles WHERE chat_id =?", (message.chat.id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows: return bot.reply_to(message, "↢ لا يوجد مشرفين مرفوعين")
    
    text = "↢ قائمة المشرفين:\n"
    for user_id, role in rows:
        try:
            user = bot.get_chat_member(message.chat.id, user_id).user
            name = user.first_name
            text += f"- {name} : {role}\n"
        except: continue
    bot.reply_to(message, text)

@bot.message_handler(func=lambda msg: msg.text == "تثبيت")
def pin_msg(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    if message.reply_to_message:
        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        bot.reply_to(message, "↢ تم تثبيت الرسالة ✓")
    else: bot.reply_to(message, "↢ رد على الرسالة")

@bot.message_handler(func=lambda msg: msg.text == "الغاء التثبيت")
def unpin_msg(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    bot.unpin_chat_message(message.chat.id)
    bot.reply_to(message, "↢ تم الغاء تثبيت الرسالة ✓")

@bot.message_handler(func=lambda msg: msg.text == "الحظر")
def list_banned(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    bot.reply_to(message, "↢ استخدم البوت @getmyid_bot لعرض قائمة المحظورين")

@bot.message_handler(func=lambda msg: msg.text == "المقيدين")
def list_restricted(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    bot.reply_to(message, "↢ استخدم البوت @getmyid_bot لعرض قائمة المكتومين")

# ==========================================
# م2 : الرابط والقوانين والترحيب والوصف
# ==========================================

def init_group_table():
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups
                     (chat_id INTEGER PRIMARY KEY, link TEXT, rules TEXT, welcome TEXT, description TEXT)''')
    conn.commit()
    conn.close()

init_group_table()

def get_group_data(chat_id):
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT link, rules, welcome, description FROM groups WHERE chat_id =?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None, None, None)

def set_group_data(chat_id, column, value):
    conn = sqlite3.connect("tia_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO groups (chat_id) VALUES (?)", (chat_id,))
    cursor.execute(f"UPDATE groups SET {column} =? WHERE chat_id =?", (value, chat_id))
    conn.commit()
    conn.close()

@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("ضع رابط"))
def set_link(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    link = message.text.replace("ضع رابط ", "", 1)
    set_group_data(message.chat.id, "link", link)
    bot.reply_to(message, "↢ تم حفظ الرابط ✓")

@bot.message_handler(func=lambda msg: msg.text == "الرابط")
def get_link(message):
    link, _, _, _ = get_group_data(message.chat.id)
    if link: bot.reply_to(message, f"↢ رابط المجموعة:\n{link}")
    else: bot.reply_to(message, "↢ لا يوجد رابط محفوظ. استخدم ضع رابط + الرابط")

@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("ضع قوانين"))
def set_rules(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    rules = message.text.replace("ضع قوانين ", "", 1)
    set_group_data(message.chat.id, "rules", rules)
    bot.reply_to(message, "↢ تم حفظ القوانين ✓")

@bot.message_handler(func=lambda msg: msg.text == "القوانين")
def get_rules(message):
    _, rules, _, _ = get_group_data(message.chat.id)
    if rules: bot.reply_to(message, f"↢ قوانين المجموعة:\n\n{rules}")
    else: bot.reply_to(message, "↢ لا توجد قوانين محفوظة")

@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("ضع ترحيب"))
def set_welcome(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    welcome = message.text.replace("ضع ترحيب ", "", 1)
    set_group_data(message.chat.id, "welcome", welcome)
    bot.reply_to(message, "↢ تم حفظ رسالة الترحيب ✓\nملاحظة: {name} = اسم العضو , {chat} = اسم القروب")

@bot.message_handler(func=lambda msg: msg.text == "الترحيب")
def get_welcome(message):
    _, _, welcome, _ = get_group_data(message.chat.id)
    if welcome: bot.reply_to(message, f"↢ رسالة الترحيب:\n{welcome}")
    else: bot.reply_to(message, "↢ لا توجد رسالة ترحيب محفوظة")

@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("ضع وصف"))
def set_description(message):
    if not is_user_admin(message.chat.id, message.from_user.id): return
    desc = message.text.replace("ضع وصف ", "", 1)
    set_group_data(message.chat.id, "description", desc)
    bot.reply_to(message, "↢ تم حفظ وصف المجموعة ✓")

@bot.message_handler(func=lambda msg: msg.text == "الوصف")
def get_description(message):
    _, _, _, desc = get_group_data(message.chat.id) # صلحت هذا السطر
    if desc: bot.reply_to(message, f"↢ وصف المجموعة:\n{desc}")
    else: bot.reply_to(message, "↢ لا يوجد وصف محفوظ")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    _, _, welcome, _ = get_group_data(message.chat.id) # صلحت هذا السطر
    for new_user in message.new_chat_members:
        name = new_user.first_name
        if welcome:
            text = welcome.replace("{name}", name).replace("{chat}", message.chat.title)
            bot.send_message(message.chat.id, text)
        else:
            bot.send_message(message.chat.id, f"↢ اهلا {name} نورت {message.chat.title} 🌹")
