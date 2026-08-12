import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7488375443 # ايديك

app = Client("TiaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# قاعدة بيانات مؤقته
db = {
    "contact": True,
    "service": True,
    "force": False,
    "force_channel": "",
    "welcome_text": "مرحبا بك في Tia",
    "welcome_pic": None,
    "banned": [],
    "devs": [7488375443],
    "waiting": None
}

def dev_keyboard():
    keyboard = [
        [KeyboardButton("الاحصائيات")],
        [KeyboardButton("تفعيل التواصل"), KeyboardButton("تعطيل التواصل")],
        [KeyboardButton("تفعيل البوت الخدمي"), KeyboardButton("تعطيل البوت الخدمي")],
        [KeyboardButton("تفعيل الاشتراك الاجباري"), KeyboardButton("تعطيل الاشتراك الاجباري")],
        [KeyboardButton("تغيير قناة الاشتراك"), KeyboardButton("عرض قناة الاشتراك")],
        [KeyboardButton("اذاعه للمجموعات"), KeyboardButton("اذاعه للخاص")],
        [KeyboardButton("قائمه العام"), KeyboardButton("مسح قائمه العام")],
        [KeyboardButton("المطورين"), KeyboardButton("اضافه مطور")],
        [KeyboardButton("ضع صوره ترحيب"), KeyboardButton("رد المطور")],
        [KeyboardButton("اخفاء اللوحه")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, selective=True)

@app.on_message(filters.command("المطور") & filters.private)
async def show_panel(client, message: Message):
    if message.from_user.id!= OWNER_ID:
        return await message.reply("❌ هذا الامر للمطور فقط")
    await message.reply("👨‍💻 اهلا بك يا مطور Tia", reply_markup=dev_keyboard())

@app.on_message(filters.text & filters.private & filters.user(OWNER_ID))
async def dev_buttons(client, message: Message):
    global db
    text = message.text

    # التحقق من الانتظار
    if db["waiting"] == "channel":
        db["force_channel"] = text
        db["waiting"] = None
        return await message.reply(f"✅ تم ضبط قناة الاشتراك: {text}")

    if db["waiting"] == "dev":
        try:
            db["devs"].append(int(text))
            db["waiting"] = None
            return await message.reply(f"✅ تم اضافة المطور: {text}")
        except:
            return await message.reply("❌ ارسل ايدي رقمي فقط")

    if db["waiting"] == "photo" and message.photo:
        db["welcome_pic"] = message.photo.file_id
        db["waiting"] = None
        return await message.reply("✅ تم حفظ صورة الترحيب")

    # برمجة الازرار
    if text == "الاحصائيات":
        await message.reply(f"📊 احصائيات Tia\nالبوت الخدمي: {'مفعل' if db['service'] else 'معطل'}\nالتواصل: {'مفعل' if db['contact'] else 'معطل'}")

    elif text == "تفعيل التواصل": db["contact"] = True; await message.reply("✅ تم تفعيل التواصل")
    elif text == "تعطيل التواصل": db["contact"] = False; await message.reply("❌ تم تعطيل التواصل")

    elif text == "تفعيل البوت الخدمي": db["service"] = True; await message.reply("✅ تم تفعيل البوت الخدمي")
    elif text == "تعطيل البوت الخدمي": db["service"] = False; await message.reply("❌ تم تعطيل البوت الخدمي")

    elif text == "تفعيل الاشتراك الاجباري": db["force"] = True; await message.reply("✅ تم تفعيل الاشتراك الاجباري")
    elif text == "تعطيل الاشتراك الاجباري": db["force"] = False; await message.reply("❌ تم تعطيل الاشتراك الاجباري")

    elif text == "تغيير قناة الاشتراك":
        db["waiting"] = "channel"
        await message.reply("📢 ارسل يوزر القناة مع @")
    elif text == "عرض قناة الاشتراك":
        await message.reply(f"📢 القناة الحاليه: {db['force_channel'] or 'غير مضبوطه'}")

    elif text == "اذاعه للمجموعات":
        await message.reply("📢 ارسل الرسالة الان للاذاعة في المجموعات")
    elif text == "اذاعه للخاص":
        await message.reply("📢 ارسل الرسالة الان للاذاعة في الخاص")

    elif text == "قائمه العام":
        if db["banned"]: await message.reply("المحظورين: " + str(db["banned"]))
        else: await message.reply("قائمه العام فاضيه")
    elif text == "مسح قائمه العام": db["banned"] = []; await message.reply("✅ تم مسح قائمه العام")

    elif text == "المطورين": await message.reply("👑 المطورين:\n" + "\n".join([str(i) for i in db["devs"]]))
    elif text == "اضافه مطور":
        db["waiting"] = "dev"
        await message.reply("ارسل ايدي المطور الجديد")

    elif text == "ضع صوره ترحيب":
        db["waiting"] = "photo"
        await message.reply("ارسل الصورة الان")
    elif text == "رد المطور":
        if db["welcome_pic"]:
            await message.reply_photo(photo=db["welcome_pic"], caption=db["welcome_text"])
        else:
            await message.reply("❌ لم تضع صورة ترحيب بعد")

    elif text == "اخفاء اللوحه":
        await message.reply("✅ تم اخفاء اللوحه", reply_markup=ReplyKeyboardMarkup([]))

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    if message.from_user.id == OWNER_ID:
        if db["welcome_pic"]:
            await message.reply_photo(photo=db["welcome_pic"], caption=f"{db['welcome_text']}\nارسل /المطور")
        else:
            await message.reply(f"{db['welcome_text']}\nارسل /المطور")
    else:
        if db["force"] and db["force_channel"]:
            await message.reply(f"❌ اشترك في القناة اولا: {db['force_channel']}")
        else:
            await message.reply("انا Tia جاهزه")

print("TiaBot is running...")
app.run()
