import asyncio
from pyrogram import Client, idle
import config
from plugins.music import init_pytgcalls

bot = Client(
    "my_bot_session",
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def main():
    print("⚡ جاري تشغيل البوت والاتصال بتليجرام...")
    await bot.start()
    
    print("🎵 جاري تهيئة نظام الأغاني والصوتيات...")
    init_pytgcalls(bot)
    
    from plugins.protection import warnings
    warnings.clear()
    print("🛡️ نظام الحماية والأغاني يعملان الآن بنجاح!")
    print(f"✅ البوت شغال: @{(await bot.get_me()).username}")
    
    await idle()
    await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت يدويًا.")
