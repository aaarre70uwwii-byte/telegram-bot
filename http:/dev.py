from pyrogram import filters
from pyrogram.types import Message
from bot import app

# ضع هنا الآي دي الخاص بمطور البوت
DEV_USER_ID = 7488375443

# قائمة تحفظ فيها القروبات تلقائي
CHATS = []

@app.on_message(filters.new_chat_members) # يحفظ القروب اول ما يدخل
async def save_chat(client, message):
    if message.chat.id not in CHATS:
        CHATS.append(message.chat.id)

# أوامر المطور
@app.on_message(filters.command(["إذاعة", "الاحصائيات"]) & filters.user(DEV_USER_ID))
async def developer_commands(client, message: Message):
    cmd = message.command[0]

    if cmd == "إذاعة":
        if len(message.command) < 2:
            return await message.reply("• يرجى كتابة النص المراد إذاعته بعد الأمر\nمثال: `إذاعة مرحبا`")

        broadcast_text = message.text.split(None, 1)[1]
        count = 0

        await message.reply(f"• جاري بدء الإذاعة لـ {len(CHATS)} مجموعة...")

        for chat_id in CHATS:
            try:
                await client.send_message(chat_id, f"📢 **إذاعة من المطور**\n\n{broadcast_text}")
                count += 1
            except: pass

        await message.reply(f"• تمت الإذاعة بنجاح لـ {count} مجموعة ✅")

    elif cmd == "الاحصائيات" or cmd == "الإحصائيات":
        await message.reply(f"• إحصائيات البوت:\n- عدد المجموعات: {len(CHATS)}\n- المطور: `{DEV_USER_ID}`")
