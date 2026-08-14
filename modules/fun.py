import random
from pyrogram import filters
from pyrogram.types import Message
from bot import app # نستدعي app

# ألعاب وأوامر التسلية
@app.on_message(filters.command(["سؤال", "صراحة", "تخمين"]) & filters.group)
async def fun_games(client, message: Message):
    cmd = message.command[0] # نجيب اول كلمة فقط

    if cmd == "سؤال" or cmd == "صراحة":
        questions = [
            "ما هي أكثر صفة تحبها في نفسك؟",
            "لو ملكت العالم ليوم واحد ماذا تفعل؟",
            "موقف محرج لن تنساه أبداً؟",
            "كلمة تقولها لشخص أزعجك اليوم؟"
        ]
        await message.reply(f"• سؤال صراحة:\n{random.choice(questions)}")

    elif cmd == "تخمين":
        number = random.randint(1, 10)
        # نحفظ الرقم مؤقتا في ذاكرة البوت
        app.guess_number = {message.chat.id: number}
        await message.reply(f"• اخترت رقماً بين 1 و 10\nرد على هذه الرسالة برقمك")
