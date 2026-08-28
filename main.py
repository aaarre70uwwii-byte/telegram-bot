import os
import time
import telebot

# 1. قراءة المتغيرات الأربعة من بيئة Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# 2. التحقق الذكي من وجود المتغيرات
missing_vars = []
if not BOT_TOKEN: missing_vars.append("BOT_TOKEN")
if not OWNER_ID: missing_vars.append("OWNER_ID")
if not API_ID: missing_vars.append("API_ID")
if not API_HASH: missing_vars.append("API_HASH")

if missing_vars:
    raise ValueError(f"⚠️ خطأ: المتغيرات التالية مفقودة في إعدادات Railway: {', '.join(missing_vars)}")

# 3. إنشاء كائن البوت مع تفعيل ميزة الاسترداد التلقائي ضد الأخطاء الداخلية
bot = telebot.TeleBot(BOT_TOKEN, exception_handler=telebot.ExceptionHandler())

# 4. استدعاء الملفات الفرعية وتفعيل الأوامر بها بالكامل
try:
    import main_menu
    import dev_keyboard

    # تفعيل وتسجيل الهاندلرز للملفين معاً دون نسيان أي منهما
    main_menu.register_handlers(bot)
    dev_keyboard.register_handlers(bot)
    print("✅ تم استدعاء وتفعيل ملف أوامر القائمة (main_menu) وملف كيبورد المطور (dev_keyboard) بنجاح!")
    
except ImportError as e:
    raise ImportError(f"⚠️ خطأ في الملفات الفرعية: تأكد من وجود ملف main_menu.py وملف dev_keyboard.py بجانب هذا الملف. التفاصيل: {e}")

# 5. تشغيل البوت مع آلية إعادة التشغيل التلقائي عند أي انهيار (Crash Protection)
if __name__ == "__main__":
    print("🚀 نظام الحماية من التحطم مُفعل بالكامل وجاهز للعمل!")
    
    while True:
        try:
            print("🤖 البوت متصل الآن ويستقبل الأوامر...")
            # infinity_polling مع خيارات الحماية وإعادة الاتصال التلقائي
            bot.infinity_polling(
                timeout=60, 
                long_polling_timeout=30, 
                restart_on_status_update=True
            )
        except Exception as e:
            # عند حدوث أي خطأ خارجي (مثل انقطاع الإنترنت أو سيرفرات تليجرام)
            print(f"⚠️ تحذير: حدث خطأ في الاتصال: {e}")
            print("🔄 جاري إعادة تشغيل البوت تلقائياً خلال 5 ثوانٍ دون توقف السيرفر...")
            time.sleep(5)  # الانتظار لمنع حظر التوكن من تليجرام عند تكرار الأخطاء
