import telebot
import config
import time
import os

# فحص المتغيرات
if not config.TOKEN:
    print("❌ خطأ: BOT_TOKEN غير موجود في المتغيرات")
    exit()
if not config.DEV:
    print("❌ خطأ: DEV_ID غير موجود في المتغيرات")
    exit()

bot = telebot.TeleBot(config.TOKEN, parse_mode="HTML")

المطور_الاساسي = config.DEV
admins = config.admins

# تحميل كل ملفات cogs
try:
    from cogs import cog1, cog2, cog3, cog4, cog5, cog6, cog7

    cog1.setup(bot, المطور_الاساسي, admins)
    cog2.setup(bot, المطور_الاساسي, admins)
    cog3.setup(bot, المطور_الاساسي, admins)
    cog4.setup(bot, المطور_الاساسي, admins)
    cog5.setup(bot, المطور_الاساسي, admins)
    cog6.setup(bot, المطور_الاساسي, admins)
    cog7.setup(bot, المطور_الاساسي, admins)

    print("✅ تم تحميل جميع ملفات cogs بنجاح")

except Exception as e:
    print(f"❌ خطأ في تحميل الملفات: {e}")
    exit()

print(f"✅ البوت 𝐓𝐢𝐚 اشتغل - المطور: {المطور_الاساسي}")

# تشغيل البوت مع اعادة تلقائية
while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"⚠️ حدث خطأ: {e}")
        time.sleep(5)
