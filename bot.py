from pyrogram import Client

# إعداد البوت الأساسي
app = Client(
    "ProtectionBot",
    api_id=7488375443,
    api_hash="d37b2de52c76a51442c1ba82609cf9bb",
    bot_token="8985250187:AAHSZfDHuxy1A7PpDZt7k0QdEWAsaTt5aTU"
)

# استدعاء كل الملفات عشان تتفعل
import modules.database
import modules.locks
import modules.protection
import modules.settings
import modules.services
import modules.games
import modules.dev

print("• البوت شغال بنجاح ✅")
app.run()
