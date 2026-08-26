import telebot
import telebot.apihelper
import config
import time
import os

# فحص المتغيرات
if not config.TOKEN:
    print("❌ خطأ: TOKEN غير موجود في المتغيرات")
    exit()
if not config.DEV:
    print("❌ خطأ: DEV_ID غير موجود في المتغيرات")
    exit()

bot = telebot.TeleBot(config.TOKEN, parse_mode="HTML")

المطور_الاساسي = config.DEV
admins = config.admins

def delete_old_webhook():
    """ نحذف الويبهوك القديم لو موجود """
    try:
        bot.delete_webhook()
        print("🗑️ تم حذف الويبهوك القديم")
        time.sleep(1)
    except telebot.apihelper.ApiTelegramException as e:
        if "404" in str(e) or "Not Found" in str(e):
            print("ℹ️ مافي ويبهوك قديم للحذف")
        else:
            print(f"⚠️ خطأ حذف الويبهوك: {e}")
    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")

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

print(f"✅ البوت 𝐓𝐢𝐚 جاهز - المطور: {المطور_الاساسي}")

# === اهم جزء: Webhook للـ Railway ===
WEBHOOK = os.getenv('WEBHOOK', 'False').lower() == 'true'
URL = os.getenv('URL', '')

if WEBHOOK and URL:
    # وضع الويبهوك حق Railway
    delete_old_webhook() # نحذفه اول
    print("🌐 شغال على Webhook:", URL)
    try:
        bot.set_webhook(url=URL)
        print("🚀 البوت شغال الان على Webhook...")
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ خطأ في الويبهوك: {e}")
else:
    # وضع polling حق الجهاز
    delete_old_webhook() # نحذفه اول
    print("🔄 شغال على Polling")
    print("🚀 البوت شغال الان على Polling...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"⚠️ حدث خطأ: {e}")
            time.sleep(5)
