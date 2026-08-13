from pyrogram import filters, Client
from pyrogram.types import Message
from database import set_setting
from modules.utils import dev_keyboard

def setup(app: Client):
    @app.on_message(filters.text & filters.private)
    async def protect_panel(_, message: Message):
        from database import is_dev
        if not is_dev(message.from_user.id): return
        text = message.text

        if text == "🛡️ الحماية":
            await message.reply("اختر:", reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("1. قفل الروابط"), KeyboardButton("2. فتح الروابط")],
                [KeyboardButton("3. قفل التكرار"), KeyboardButton("4. فتح التكرار")],
                [KeyboardButton("5. الحظر التلقائي")], [KeyboardButton("رجوع")]
            ], resize_keyboard=True))
        elif text == "1. قفل الروابط": set_setting("lock_link","1"); await message.reply("✅ تم قفل الروابط")
        elif text == "2. فتح الروابط": set_setting("lock_link","0"); await message.reply("✅ تم فتح الروابط")
