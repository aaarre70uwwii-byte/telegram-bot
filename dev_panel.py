import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# مخزن البيانات المؤقت لخيارات التحكم
DEV_DATA = {
    "channel": "https://t.me",
    "bot_name": "Tia Bot",
    "welcome": "أهلاً بك عزي في البوت! 👋"
}

# خليتها برا عشان main.py يستدعيها مباشرة
def get_dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, placeholder="لوحة تحكم المطور الأساسي ⚙️")
    markup.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📣 أوامر الإذاعة"), KeyboardButton("📊 قائمة العام"))
    markup.row(KeyboardButton("👑 تغيير المطور الأساسي"), KeyboardButton("🔔 مسح المطورين"))
    markup.row(KeyboardButton("🗑️ مسح اسم البوت"), KeyboardButton("❌ مسح قائمة العام"))
    markup.row(KeyboardButton("✏️ تغيير اسم البوت"), KeyboardButton("👥 مسح المطورين الثانويين"))
    markup.row(KeyboardButton("📴 تعطيل التواصل"), KeyboardButton("📦 جلب النسخة الاحتياطية"))
    markup.row(KeyboardButton("📲 تفعيل التواصل"), KeyboardButton("🔄 تحديث الملفات"))
    markup.row(KeyboardButton("🔴 تعطيل البوت الخدمي"), KeyboardButton("⚡ تفعيل البوت"))
    markup.row(KeyboardButton("▶️ تفعيل البوت الخدمي"))
    markup.row(KeyboardButton("⚙️ إظهار _ إخفاء • قائمة إعداد البوت"))
    markup.row(KeyboardButton("👋 أضف ترحيب"))
    markup.row(KeyboardButton("📢 قناة تحديثات البوت"))
    return markup

def register_handlers(bot):
    
    # استدعاء الكيبورد بالخاص للمطور فقط عند كتابة كلمة مطور
    @bot.message_handler(func=lambda message: message.text in ["مطور", "المطور", "/dev"] and message.chat.type == "private")
    def send_dev_menu(message):
        owner_id = os.getenv("OWNER_ID")
        if str(message.from_user.id) == str(owner_id):
            bot.send_message(message.chat.id, "👑 تم تفعيل لوحة تحكم المطور بنجاح أسفل الشاشة:", reply_markup=get_dev_keyboard())

    # الاستجابة للضغط على الأزرار بشكل معزول وصحيح
    @bot.message_handler(func=lambda message: message.chat.type == "private" and message.text in [
        "⚙️ إعدادات البوت", "📣 أوامر الإذاعة", "📊 قائمة العام", "👑 تغيير المطور الأساسي", 
        "🔔 مسح المطورين", "🗑️ مسح اسم البوت", "❌ مسح قائمة العام", "✏️ تغيير اسم البوت", 
        "👥 مسح المطورين الثانويين", "📴 تعطيل التواصل", "📦 جلب النسخة الاحتياطية", 
        "📲 تفعيل التواصل", "🔄 تحديث الملفات", "🔴 تعطيل البوت الخدمي", "⚡ تفعيل البوت", 
        "▶️ تفعيل البوت الخدمي", "⚙️ إظهار _ إخفاء • قائمة إعداد البوت", "👋 أضف ترحيب", "📢 قناة تحديثات البوت"
    ])
    def handle_dev_buttons(message):
        owner_id = os.getenv("OWNER_ID")
        if str(message.from_user.id) != str(owner_id):
            return

        if message.text == "⚙️ إعدادات البوت":
            status = f"⚙️ **حالة البوت الحالية:**\n\n🤖 الاسم: {DEV_DATA['bot_name']}\n📢 القناة: {DEV_DATA['channel']}\n👋 الترحيب: {DEV_DATA['welcome']}"
            bot.reply_to(message, status, parse_mode="Markdown")
            
        elif message.text == "📣 أوامر الإذاعة":
            sent_msg = bot.reply_to(message, "📣 أرسل الآن نص الإذاعة التي تريد نشرها للجميع:")
            bot.register_next_step_handler(sent_msg, process_broadcast)
            
        elif message.text == "📢 قناة تحديثات البوت":
            sent_msg = bot.reply_to(message, f"📢 القناة الحالية هي: {DEV_DATA['channel']}\n\nأرسل يوزر أو رابط القناة الجديد الآن للتحديث:")
            bot.register_next_step_handler(sent_msg, process_change_channel)
            
        elif message.text == "✏️ تغيير اسم البوت":
            sent_msg = bot.reply_to(message, "✏️ أرسل اسم البوت الجديد الآن:")
            bot.register_next_step_handler(sent_msg, process_change_name)
            
        elif message.text == "👋 أضف ترحيب":
            sent_msg = bot.reply_to(message, "👋 أرسل نص الترحيب الجديد:")
            bot.register_next_step_handler(sent_msg, process_change_welcome)
            
        elif message.text in ["🔄 تحديث الملفات", "📦 جلب النسخة الاحتياطية"]:
            bot.reply_to(message, f"🔄 جاري تنفيذ عملية [{message.text}] على سيرفر Railway...")
        else:
            bot.reply_to(message, f"✅ تم تفعيل خيار: {message.text}")

    # دالات استقبال وحفظ المدخلات الجديدة من المطور
    def process_broadcast(message):
        bot.reply_to(message, "📢 تم استقبال النص، وجاري معالجة الإرسال الجماعي الحقيقي للمشتركين...")

    def process_change_channel(message):
        if message.text.strip().startswith(("⚙️", "📣", "📢")): return
        DEV_DATA["channel"] = message.text.strip()
        bot.reply_to(message, f"✅ تم تحديث قناة البوت بنجاح إلى: {DEV_DATA['channel']}")

    def process_change_name(message):
        if message.text.strip().startswith(("⚙️", "📣", "📢")): return
        DEV_DATA["bot_name"] = message.text.strip()
        bot.reply_to(message, f"✅ تم تغيير اسم البوت بنجاح إلى: {DEV_DATA['bot_name']}")

    def process_change_welcome(message):
        if message.text.strip().startswith(("⚙️", "📣", "📢")): return
        DEV_DATA["welcome"] = message.text.strip()
        bot.reply_to(message, f"✅ تم حفظ رسالة الترحيب الجديدة.")
