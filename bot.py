import os
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7488375443

app = Client("TiaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

db = {
    "contact": True, "service": True, "force": False, "force_channel": "",
    "welcome_pic": None, "welcome_text": "مرحبا بك في 𝐓𝐢𝐚 🌹",
    "banned": [], "devs": [7488375443], "waiting": {}
}

def dev_keyboard():
    keyboard = [
        [KeyboardButton("الاحصائيات")],
        [KeyboardButton("تفعيل التواصل"), KeyboardButton("تعطيل التواصل")],
        [KeyboardButton("تفعيل البوت الخدمي"), KeyboardButton("تعطيل البوت الخدمي")],
        [KeyboardButton("تفعيل الاشتراك الاجباري"), KeyboardButton("تعطيل الاشتراك الاجباري")],
        [KeyboardButton("تغيير كليشة الاشتراك"), KeyboardButton("جلب كليشة الاشتراك")],
        [KeyboardButton("اذاعه للمجموعات"), KeyboardButton("اذاعه خاص")],
        [KeyboardButton("قائمه العام"), KeyboardButton("المطورين")],
        [KeyboardButton("ضع صوره للترحيب")],
        [KeyboardButton("رد المطور"), KeyboardButton("مسح رد المطور")], # الزر الجديد
        [KeyboardButton("اخفاء اللوحة")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

@app.on_message(filters.command("المطور") & filters.private)
async def show_panel(client, message: Message):
    if message.from_user.id!= OWNER_ID:
        return await message.reply("❌ هذا الامر للمطور فقط")
    await message.reply("👨‍💻 اهلا بك يا مطور 𝐓𝐢𝐚", reply_markup=dev_keyboard())

@app.on_message(filters.text("اخفاء اللوحة") & filters.private & filters.user(OWNER_ID))
async def hide_panel(client, message: Message):
    await message.reply("✅ تم اخفاء اللوحة", reply_markup=ReplyKeyboardMarkup([]))

# برمجة كل الازرار
@app.on_message(filters.private & filters.user(OWNER_ID))
async def dev_buttons(client, message: Message):
    text = message.text
    user_id = message.from_user.id

    # لو منتظر صورة
    if db["waiting"].get(user_id) == "photo":
        if message.photo:
            file_id = message.photo.file_id
            db["welcome_pic"] = file_id
            db["waiting"][user_id] = None
            await message.reply("✅ تم حفظ صورة الترحيب")
        return

    # الازرار
    if text == "الاحصائيات":
        await message.reply(f"📊 **احصائيات 𝐓𝐢𝐚**\nالبوت الخدمي: {'مفعل' if db['service'] else 'معطل'}\nالاشتراك: {'مفعل' if db['force'] else 'معطل'}")

    elif text == "تفعيل التواصل": db["contact"] = True; await message.reply("✅ تم تفعيل التواصل")
    elif text == "تعطيل التواصل": db["contact"] = False; await message.reply("❌ تم تعطيل التواصل")
    elif text == "تفعيل البوت الخدمي": db["service"] = True; await message.reply("✅ تم تفعيل البوت الخدمي")
    elif text == "تعطيل البوت الخدمي": db["service"] = False; await message.reply("❌ تم تعطيل البوت الخدمي")

    elif text == "تفعيل الاشتراك الاجباري": db["force"] = True; await message.reply("✅ تم تفعيل الاشتراك الاجباري")
    elif text == "تعطيل الاشتراك الاجباري": db["force"] = False; await message.reply("❌ تم تعطيل الاشتراك الاجباري")

    elif text == "تغيير كليشة الاشتراك":
        db["waiting"][user_id] = "text"
        await message.reply("ارسل كليشة الاشتراك الجديدة")
    elif text == "جلب كليشة الاشتراك":
        await message.reply(f"الكليشة الحالية:\n{db['welcome_text']}")

    elif text == "اذاعه للمجموعات": await message.reply("📢 ارسل الرسالة للاذاعة في المجموعات")
    elif text == "اذاعه خاص": await message.reply("📢 ارسل الرسالة للاذاعة في الخاص")

    elif text == "قائمه العام": await message.reply(f"📝 المحظورين عام: {len(db['banned'])}")
    elif text == "المطورين": await message.reply(f"👑 المطور الاساسي:\n`{OWNER_ID}`")

    elif text == "ضع صوره للترحيب":
        db["waiting"][user_id] = "photo"
        await message.reply("ارسل الصورة الان وسيتم حفظها كصورة ترحيب للمطور")

    elif text == "رد المطور": # <-- رد المطور بصورة
        if db["welcome_pic"]:
            await message.reply_photo(photo=db["welcome_pic"], caption=db["welcome_text"])
        else:
            await message.reply("❌ لم يتم وضع صورة ترحيب بعد. اضغط 'ضع صوره للترحيب'")

    elif text == "مسح رد المطور":
        db["welcome_pic"] = None
        await message.reply("✅ تم مسح رد المطور")

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    if message.from_user.id == OWNER_ID:
        if db["welcome_pic"]:
            await message.reply_photo(photo=db["welcome_pic"], caption=f"انا 𝐓𝐢𝐚 🌹\n{db['welcome_text']}\nارسل /المطور")
        else:
            await message.reply(f"انا 𝐓𝐢𝐚 🌹\n{db['welcome_text']}\nارسل /المطور")
    else:
        if db["force"] and db["force_channel"]:
            await message.reply(f"❌ لازم تشترك في القناة اول\n{db['force_channel']}")
        else:
            await message.reply("انا 𝐓𝐢𝐚 🌹 جاهزة لحماية القروب")

print("TiaBot is running...")
app.run()
