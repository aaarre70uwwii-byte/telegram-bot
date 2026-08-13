from pyrogram import filters, Client
from pyrogram.types import Message
from database import set_setting, get_setting, is_dev, cursor
from modules.utils import dev_keyboard
import asyncio

waiting = {}

def setup(app: Client):
    @app.on_message(filters.text & filters.private)
    async def service_panel(_, message: Message):
        global waiting
        text = message.text; uid = message.from_user.id
        if not is_dev(uid): return

        if text == "📋 الخدمي":
            await message.reply("اختر:", reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("1. تفعيل"), KeyboardButton("2. تعطيل")],
                [KeyboardButton("3. الاشتراك"), KeyboardButton("4. الرابط")],
                [KeyboardButton("5. الاحصائيات")], [KeyboardButton("رجوع")]
            ], resize_keyboard=True))
        elif text == "📢 اذاعة":
            waiting[uid] = "broadcast"; await message.reply("ارسل الرسالة للاذاعة")
        elif waiting.get(uid) == "broadcast":
            users = cursor.execute("SELECT id FROM users").fetchall()
            count = 0
            for u in users:
                try: await app.send_message(u[0], text); count += 1; await asyncio.sleep(0.05)
                except: pass
            waiting[uid] = None; await message.reply(f"✅ تمت الاذاعة لـ {count} عضو")
        elif text == "1. تفعيل": set_setting("service","1"); await message.reply("✅ تم التفعيل")
        elif text == "2. تعطيل": set_setting("service","0"); await message.reply("❌ تم التعطيل")
