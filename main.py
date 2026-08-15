import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
import config

# 1. تهيئة عميل البوت وربطه بمجلد الأوامر تلقائياً
bot = Client(
    "my_bot_session",
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="plugins")  # يتعرف على ملفات الحماية والأغاني داخل مجلد plugins تلقائياً
)

# 2. تهيئة مشغل المكالمات الصوتية (الأغاني)
pytgcalls_client = PyTgCalls(bot)

# 3. دالة تهيئة وتشغيل نظام الأغاني والحماية معاً
async def initialize_all_systems():
    print("----------------------------------------")
    print("⚡ جاري الاتصال بخوادم تليجرام وبدء تشغيل البوت...")
    await bot.start()
    
    # تشغيل نظام الأغاني والمكالمات
    print("🎵 جاري تفعيل مشغل الأغاني والمكالمات الصوتية...")
    try:
        await pytgcalls_client.start()
        print("✅ تم تفعيل نظام الأغاني (PyTgCalls) بنجاح!")
    except Exception as e:
        print(f"❌ فشل تفعيل نظام الأغاني، السبب: {e}")

    # تشغيل نظام الحماية
    print("🛡️ جاري تشغيل جدار الحماية التلقائي للبوت...")
    try:
        # استيراد قاموس التحذيرات من ملف الحماية لتصفيره عند الإقلاع
        from plugins.protection import warnings
        warnings.clear()
        print("✅ تم تصفير سجل التحذيرات وجدار الحماية جاهز!")
    except ImportError:
        print("⚠️ تنبيه: ملف plugins/protection.py غير موجود أو لم يتم إنشاء قاموس الـ warnings بداخله بعد.")
    except Exception as e:
        print(f"⚠️ حدث خطأ أثناء تجهيز نظام الحماية: {e}")
        
    print("🚀 البوت والملفات متصلة الآن بالكامل وبانتظار الأوامر...")
    print("----------------------------------------")

# 4. دالة التشغيل والإغلاق الآمن للسيرفر
async def main():
    # استدعاء دالة التهيئة والربط
    await initialize_all_systems()
    
    # إبقاء البوت مستيقظاً ويعمل دون توقف
    await idle()
    
    # إغلاق الأنظمة بشكل آمن عند إيقاف السورس
    print("\n⚠️ جاري إيقاف البوت والمكالمات الصوتية بأمان...")
    try:
        await pytgcalls_client.stop()
    except Exception:
        pass
    await bot.stop()
    print("🛑 تم إيقاف السيرفر بنجاح.")

if __name__ == "__main__":  # هنا صلحتها
    # تشغيل المجلد البرمجي بأكمله
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف تشغيل السيرفر يدوياً.")
