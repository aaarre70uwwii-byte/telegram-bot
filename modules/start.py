from pyrogram import filters, Client
from pyrogram.types import Message
from database import is_dev, is_banned, set_setting, get_setting, cursor
from modules.utils import dev_keyboard

def setup(app: Client):
    @app.on_message(filters.command("start") & filters.private)
    async def start(_, message: Message):
        if is_banned(message.from_user.id): return
        cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (message.from_user.id, message.from_user.username))
        if is_dev(message.from_user.id):
            await message.reply("👨‍💻 مرحبا بك في TiaBot V3", reply_markup=dev_keyboard())
        else:
            if get_setting("service") == "0": return await message.reply("❌ البوت الخدمي معطل")
            await message.reply("🌹 مرحبا بك في البوت الخدمي\nارسل رسالتك للمطور")

    @app.on_message(filters.command("المطور") & filters.private)
    async def panel(_, message: Message):
        if not is_dev(message.from_user.id): return await message.reply("❌ للمطورين فقط")
        await message.reply("لوحة التحكم:", reply_markup=dev_keyboard())
