from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from main import app
from database import set_lock, get_lock # استدعاء الداتا بيز

# ========== اوامر القفل والفتح ==========
@app.on_message(filters.group & filters.command("قفل"))
async def lock_cmd(client, message: Message):
    # 1. نحفظ في الداتا بيز ان الشات مقفل
    set_lock(message.chat.id, "chat", "مقفله")
    # 2. نقفل الشات فعليا من اعدادات التليجرام
    await app.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=False))
    await message.reply("🔒 تم قفل الدردشة")

@app.on_message(filters.group & filters.command("فتح"))
async def unlock_cmd(client, message: Message):
    # 1. نحفظ في الداتا بيز ان الشات مفتوح
    set_lock(message.chat.id, "chat", "فتحه")
    # 2. نفتح الشات فعليا
    await app.set_chat_permissions(
        message.chat.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )
    await message.reply("🔓 تم فتح الدردشة")

# ========== الحارس: يحذف الرسائل لو الشات مقفل ==========
@app.on_message(filters.group & ~filters.me & ~filters.command(["قفل", "فتح"]))
async def lock_guard(client, message: Message):
    status = get_lock(message.chat.id, "chat")
    if status == "مقفله":
        try:
            await message.delete() # نحذف الرسالة
        except:
            pass # لو البوت مش ادمن او ما عنده صلاحية
