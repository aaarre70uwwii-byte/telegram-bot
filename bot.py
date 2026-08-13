import threading
from flask import Flask
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from database import is_dev, is_banned, set_setting, get_setting, cursor, conn

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "TiaBot V3 is alive!"
def run_flask(): app_flask.run(host='0.0.0.0', port=8080)

app = Client("TiaBotV3", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ============ الاوامر كلها هنا مباشرة عشان نتاكد ============

@app.on_message(filters.command("start") & filters.private)
async def start(_, message):
    if is_banned(message.from_user.id): return
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (message.from_user.id, message.from_user.username))
    if is_dev(message.from_user.id):
        await message.reply("👨‍💻 مرحبا بك في TiaBot V3\nاللوحة شغالة")
    else:
        if get_setting("service") == "0": return await message.reply("❌ البوت الخدمي معطل")
        await message.reply("🌹 مرحبا بك في البوت الخدمي")

@app.on_message(filters.command("المطور") & filters.private)
async def panel(_, message):
    if not is_dev(message.from_user.id): return await message.reply("❌ للمطورين فقط")
    await message.reply("لوحة التحكم شغالة ✅")

@app.on_message(filters.text & filters.private)
async def all_text(_, message):
    if not is_dev(message.from_user.id): return
    text = message.text
    if text == "1. قفل الروابط": 
        set_setting("lock_link","1")
        await message.reply("✅ تم قفل الروابط")

@app.on_message(filters.group & filters.text)
async def group_cmd(_, message):
    if message.text == "ايدي":
        await message.reply(f"🆔 ايديك: `{message.from_user.id}`")

print("✅ TiaBot V3 Started - All handlers loaded")

if __name__ == "__main__":
    t = threading.Thread(target=run_flask); t.daemon = True; t.start()
    app.run()
