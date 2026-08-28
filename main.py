import os
import time
import telebot

# 1. قراءة جميع المتغيرات الأربعة من بيئة Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# 2. التحقق الذكي من وجود المتغيرات لمنع السيرفر من العمل صامتاً
missing_vars = []
if not BOT_TOKEN: missing_vars.append("BOT_TOKEN")
if not OWNER_ID: missing_vars.append("OWNER_ID")
if not API_ID: missing_vars.append("API_ID")
if not API_HASH: missing_vars.append("API_HASH")

if missing_vars:
    raise ValueError(f"⚠️ خطأ: المتغيرات البيئية التالية مفقودة في إعدادات Railway: {', '.join(missing_vars)}")

# 3. إنشاء كائن البوت الرئيسي مع تفعيل ميزة الاسترداد المدمجة للأخطاء الداخلية
bot = telebot.TeleBot(BOT_TOKEN, exception_handler=telebot.ExceptionHandler())

# 4. استدعاء وتنشيط الملفات الفرعية للأوامر والكيبورد معاً
try:
    import main_menu
    import dev_keyboard

    # تفعيل الهاندلرز والتصاريح للملفين دون أي تداخل
    main_menu.register_handlers(bot)
    dev_keyboard.register_handlers(bot)
    print("✅ تم استدعاء وتأمين ملف قائمة الأوامر (main_menu) وملف كيبورد المطور (dev_keyboard) بنجاح!")
    
except ImportError as e:
    raise ImportError(f"⚠️ خطأ في البناء: تأكد من وجود ملفات main_menu.py و dev_keyboard.py بجانب هذا الملف الرئيسي. التفاصيل: {e}")

# 5. حلقة التشغيل اللانهائية المقاومة للتحطم كلياً (Crash Protection)
if __name__ == "__main__":
    print("🚀 نظام التشغيل الآمن والمقاوم للتحطم مُفعل وجاهز للعمل على Railway!")
    
    while True:
        try:
            print("🤖 البوت متصل الآن بنجاح ويستقبل الأوامر...")
            # infinity_polling يجبر البوت على إعادة الاتصال ذاتياً عند تحديثات خوادم تليجرام
            bot.infinity_polling(
                timeout=60, 
                long_polling_timeout=30, 
                restart_on_status_update=True
            )
        except Exception as e:
            # عند حدوث أي خطأ شبكة خارجي أو انقطاع اتصال مؤقت
            print(f"⚠️ تحذير: حدث خطأ غير متوقع في الاتصال: {e}")
            print("🔄 جاري إعادة تشغيل السورس تلقائياً خلال 5 ثوانٍ دون توقف حاوية Railway...")
            time.sleep(5)  # وقت انتظار أمان لمنع حظر التوكن من قِبل تليجرام
