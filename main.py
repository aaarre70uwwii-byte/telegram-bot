from pyrogram import Client, filters
import os
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME

# ننشئ مجلد التحميل لو مش موجود
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# نعرف البوت
app = Client(
    "proprotectbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="modules") # هذا السطر يشغل كل ملفات modules تلقائي
)

# ===== اوامر عامة =====
@app.on_message(filters.command(["start", "تشغيل"]))
async def start(c, m):
    await m.reply(
        f"**مرحبا انا {BOT_NAME}**\n\n"
        "انا بوت حماية + تشغيل اغاني\n\n"
        "**اوامر الادمن:**\n"
        "`/حظر` - حظر عضو\n"
        "`/كتم 5m` - كتم عضو\n"
        "`/فك_كتم` - فك الكتم\n"
        "`/حذف 10` - حذف رسائل\n\n"
        "**اوامر الموسيقى:**\n"
        "`/اغنية اسم` - تحميل وتشغيل\n"
        "`/ايقاف` - ايقاف"
    )

@app.on_message(filters.command(["ping"]))
async def ping(c, m):
    await m.reply("✅ البوت شغال 100%")

# تشغيل البوت
print(f"🚀 {BOT_NAME} بدأ التشغيل...")
app.run()
