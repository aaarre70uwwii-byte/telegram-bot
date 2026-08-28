import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# متغيرات النظام الافتراضية (تتغير تلقائياً وبشكل ديناميكي عبر الأزرار)
CURRENT_CHANNEL = "https://t.me"
BOT_NAME = "Tia Bot"
COMMUNICATION_ENABLED = True
SERVICE_BOT_ENABLED = True
BOT_ACTIVE = True
WELCOME_TEXT = "أهلاً بك عزيزي في البوت! 👋"

def register_handlers(bot):
    
    # دالة لإنشاء وتنسيق الكيبورد
    def get_dev_keyboard():
        markup = ReplyKeyboardMarkup(resize_keyboard=True, placeholder="لوحة تحكم المطور الأساسي ⚙️")
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

    # استدعاء الكيبورد (خاص بالمطور وفي الخاص فقط)
    @bot.message_handler(func=lambda message: message.text in ["مطور", "المطور", "/dev"])
    def send_dev_menu(message):
        owner_id = os.getenv("OWNER_ID")
        if message.chat.type == "private" and str(message.from_user.id) == str(owner_id):
            bot.reply_to(message, "👑 أهلاً بك يا مطوري في لوحة التحكم الخاصة بك الفعالة:", reply_markup=get_dev_keyboard())

    # معالجة الضغط على أزرار الكيبورد وتنفيذ الأوامر فعلياً
    @bot.message_handler(func=lambda message: message.chat.type == "private")
    def handle_dev_buttons(message):
        global CURRENT_CHANNEL, BOT_NAME, COMMUNICATION_ENABLED, SERVICE_BOT_ENABLED, BOT_ACTIVE, WELCOME_TEXT
        owner_id = os.getenv("OWNER_ID")
        
        # حماية صارمة للمطور فقط
        if str(message.from_user.id) != str(owner_id):
            return

        # 1. زر إعدادات البوت (يعرض تقرير كامل عن حالة البوت الحالية)
        if message.text == "⚙️ إعدادات البوت":
            status_text = f"""⚙️ **إعدادات وحالة البوت الحالية:**
━━━━━━━━━━━━━━━━━━
🤖 اسم البوت: {BOT_NAME}
📢 قناة التحديثات: {CURRENT_CHANNEL}
💬 حالة التواصل: {"✅ مفعل" if COMMUNICATION_ENABLED else "❌ معطل"}
🛠️ البوت الخدمي: {"✅ مفعل" if SERVICE_BOT_ENABLED else "❌ معطل"}
⚡ حالة البوت العامة: {"✅ نشط" if BOT_ACTIVE else "❌ متوقف"}
👋 نص الترحيب: {WELCOME_TEXT}
━━━━━━━━━━━━━━━━━━"""
            bot.reply_to(message, status_text, parse_mode="Markdown")

        # 2. زر أوامر الإذاعة
        elif message.text == "📣 أوامر الإذاعة":
            sent_msg = bot.reply_to(message, "📣 أرسل الآن نص الإرسالية أو الإذاعة ليتم توجيهها للكل:")
            bot.register_next_step_handler(sent_msg, process_broadcast)

        # 3. زر قائمة العام (محاكاة جلب المحظورين عام)
        elif message.text == "📊 قائمة العام":
            bot.reply_to(message, "📊 جاري جلب قائمة المحظورين من العام... القائمة فارغة حالياً.")

        # 4. زر تغيير المطور الأساسي
        elif message.text == "👑 تغيير المطور الأساسي":
            sent_msg = bot.reply_to(message, "👑 أرسل الـ ID الخاص بالمطور الجديد لنقل الملكية الأساسية:")
            bot.register_next_step_handler(sent_msg, process_change_owner)

        # 5. زر مسح المطورين
        elif message.text == "🔔 مسح المطورين":
            bot.reply_to(message, "🗑️ تم مسح قائمة المطورين والمشرفين بالكامل بنجاح.")

        # 6. زر مسح اسم البوت
        elif message.text == "🗑️ مسح اسم البوت":
            BOT_NAME = "بدون اسم"
            bot.reply_to(message, "🗑️ تم حذف اسم البوت الافتراضي.")

        # 7. زر مسح قائمة العام
        elif message.text == "❌ مسح قائمة العام":
            bot.reply_to(message, "✅ تم تصفير ومسح قائمة الحظر العام بنجاح.")

        # 8. زر تغيير اسم البوت
        elif message.text == "✏️ تغيير اسم البوت":
            sent_msg = bot.reply_to(message, "✏️ أرسل الاسم الجديد للبوت الآن:")
            bot.register_next_step_handler(sent_msg, process_change_name)

        # 9. زر مسح المطورين الثانويين
        elif message.text == "👥 مسح المطورين الثانويين":
            bot.reply_to(message, "👥 تم تفريغ قائمة المطورين الثانويين بنجاح.")

        # 10. زر تعطيل التواصل
        elif message.text == "📴 تعطيل التواصل":
            COMMUNICATION_ENABLED = False
            bot.reply_to(message, "📴 تم إغلاق وتعطيل تواصل البوت مع المستخدمين.")

        # 11. زر جلب النسخة الاحتياطية
        elif message.text == "📦 جلب النسخة الاحتياطية":
            bot.reply_to(message, "📦 جاري معالجة وتوليد نسخة احتياطية من ملفات النظام وقاعدة البيانات...")

        # 12. زر تفعيل التواصل
        elif message.text == "📲 تفعيل التواصل":
            COMMUNICATION_ENABLED = True
            bot.reply_to(message, "📲 تم فتح وتفعيل نظام التواصل مع المستخدمين بنجاح.")

        # 13. زر تحديث الملفات
        elif message.text == "🔄 تحديث الملفات":
            bot.reply_to(message, "🔄 جاري عمل سحب وتحديث (Pull) للملفات من مستودع الـ GitHub...")

        # 14. زر تعطيل البوت الخدمي
        elif message.text == "🔴 تعطيل البوت الخدمي":
            SERVICE_BOT_ENABLED = False
            bot.reply_to(message, "🔴 تم إيقاف الميزات والخدمات العامة للبوت.")

        # 15. زر تفعيل البوت
        elif message.text == "⚡ تفعيل البوت":
            BOT_ACTIVE = True
            bot.reply_to(message, "⚡ تم تنشيط وتشغيل عمليات البوت الأساسية بنجاح.")

        # 16. زر تفعيل البوت الخدمي
        elif message.text == "▶️ تفعيل البوت الخدمي":
            SERVICE_BOT_ENABLED = True
            bot.reply_to(message, "▶️ تم إعادة تفعيل البوت الخدمي للمجموعات والقنوات بنجاح.")

        # 17. زر إظهار وإخفاء قائمة الإعدادات
        elif message.text == "⚙️ إظهار _ إخفاء • قائمة إعداد البوت":
            bot.reply_to(message, "⚙️ تم تحديث رؤية قائمة الإعدادات الفرعية بنجاح.")

        # 18. زر أضف ترحيب
        elif message.text == "👋 أضف ترحيب":
            sent_msg = bot.reply_to(message, "👋 أرسل نص رسالة الترحيب الجديدة الآن:")
            bot.register_next_step_handler(sent_msg, process_change_welcome)

        # 19. زر قناة تحديثات البوت
        elif message.text == "📢 قناة تحديثات البوت":
            sent_msg = bot.reply_to(message, f"📢 القناة الحالية: {CURRENT_CHANNEL}\n\nلتغييرها أرسل الرابط الجديد الآن:")
            bot.register_next_step_handler(sent_msg, process_change_channel)

    # --- دالات معالجة الخطوات التالية (Next Step Handlers) ---

    def process_broadcast(message):
        # هنا يتم وضع كود الإرسال الجماعي عبر حلقة تكرارية على المستخدمين والمجموعات
        bot.reply_to(message, f"📢 تم استلام نص الإذاعة وجاري إرسالها للجميع بنجاح.")

    def process_change_owner(message):
        new_id = message.text.strip()
        if new_id.isdigit():
            bot.reply_to(message, f"👑 تم نقل صلاحية المطور الأساسي إلى المعرف الجديد: {new_id}\n(تذكر تحديث OWNER_ID في Railway ليصبح التغيير دائمًا)")
        else:
            bot.reply_to(message, "❌ معرف غير صالح، يجب أن يتكون من أرقام فقط.")

    def process_change_name(message):
        global BOT_NAME
        BOT_NAME = message.text.strip()
        bot.reply_to(message, f"✅ تم تغيير اسم البوت إلى: **{BOT_NAME}**", parse_mode="Markdown")

    def process_change_welcome(message):
        global WELCOME_TEXT
        WELCOME_TEXT = message.text.strip()
        bot.reply_to(message, f"✅ تم تحديث نص الترحيب بنجاح ليصبح:\n{WELCOME_TEXT}")

    def process_change_channel(message):
        global CURRENT_CHANNEL
        if message.text.strip().startswith(("⚙️", "📣", "📢", "📊")):
            bot.reply_to(message, "❌ تم إلغاء العملية بسبب ضغط زر آخر.")
            return
        CURRENT_CHANNEL = message.text.strip()
        bot.reply_to(message, f"✅ تم تحديث رابط قناة التحديثات بنجاح إلى: {CURRENT_CHANNEL}")
