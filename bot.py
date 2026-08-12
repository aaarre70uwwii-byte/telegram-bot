import os
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7488375443 # ايديك

app = Client("TiaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# قاعدة بيانات وهمية
db = {
    "contact": True,
    "service": True,
    "force": False,
    "force_channel": "",
    "welcome_pic": None,
    "banned": [],
    "devs": [7488375443]
}

def dev_keyboard():
    keyboard = [
        [KeyboardButton("الاحصائيات")],
        [KeyboardButton("تغيير اسم البوت"), KeyboardButton("مسح اسم البوت")],
        [KeyboardButton("تفعيل التواصل"), KeyboardButton("تعطيل التواصل")],
        [KeyboardButton("تفعيل البوت الخدمي"), KeyboardButton("تعطيل البوت الخدمي")],
        [KeyboardButton("تفعيل الاشتراك الاجباري"), KeyboardButton("تعطيل الاشتراك الاجباري")],
        [KeyboardButton("الاشتراك الاجباري"), KeyboardButton("تغيير الاشتراك الاجباري")],
        [KeyboardButton("تغيير كليشة الاشتراك"), KeyboardButton("مسح كليشة الاشتراك")],
        [KeyboardButton("جلب كليشة الاشتراك")],
        [KeyboardButton("تفعيل الاشتراك العام"), KeyboardButton("تعطيل الاشتراك العام")],
        [KeyboardButton("اذاعه للمجموعات"), KeyboardButton("اذاعه خاص")],
        [KeyboardButton("اذاعه بالتوجيه"), KeyboardButton("اذاعه بالتوجيه خاص")],
        [KeyboardButton("اذاعه بالتثبيت")],
        [KeyboardButton("قائمه العام"), KeyboardButton("المطورين"), KeyboardButton("المطورين الثانويين")],
        [KeyboardButton("مسح قائمه العام"), KeyboardButton("مسح المطورين"), KeyboardButton("مسح المطورين الثانويين")],
        [KeyboardButton("تغيير المطور الاساسي")],
        [KeyboardButton("اشتراك البوت"), KeyboardButton("ضع تاريخ الاشتراك")],
        [KeyboardButton("ضع صوره للترحيب")],
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

    # 1. الاحصائيات
    if text == "الاحصائيات":
        await message.reply(f"📊 **احصائيات 𝐓𝐢𝐚**\nالمطور: {OWNER_ID}\nالبوت الخدمي: {'مفعل' if db['service'] else 'معطل'}")

    # 2. التواصل
    elif text == "تفعيل التواصل": db["contact"] = True; await message.reply("✅ تم تفعيل التواصل")
    elif text == "تعطيل التواصل": db["contact"] = False; await message.reply("❌ تم تعطيل التواصل")

    # 3. البوت الخدمي
    elif text == "تفعيل البوت الخدمي": db["service"] = True; await message.reply("✅ تم تفعيل البوت الخدمي")
    elif text == "تعطيل البوت الخدمي": db["service"] = False; await message.reply("❌ تم تعطيل البوت الخدمي")

    # 4. الاشتراك الاجباري
    elif text == "تفعيل الاشتراك الاجباري": db["force"] = True; await message.reply("✅ تم تفعيل الاشتراك الاجباري")
    elif text == "تعطيل الاشتراك الاجباري": db["force"] = False; await message.reply("❌ تم تعطيل الاشتراك الاجباري")
    elif text == "الاشتراك الاجباري": await message.reply(f"📢 قناة الاشتراك: `{db['force_channel'] or 'غير مضبوطه'}`")
    elif text == "تغيير الاشتراك الاجباري": await message.reply("ارسل يوزر القناة: @channel")

    # 5. الاذاعة
    elif text == "اذاعه للمجموعات": await message.reply("📢 ارسل الرسالة للاذاعة في المجموعات")
    elif text == "اذاعه خاص": await message.reply("📢 ارسل الرسالة للاذاعة في الخاص")
    elif text == "اذاعه بالتوجيه": await message.reply("📢 ارسل الرسالة للتوجيه في المجموعات")
    elif text == "اذاعه بالتوجيه خاص": await message.reply("📢 ارسل الرسالة للتوجيه في الخاص")
    elif text == "اذاعه بالتثبيت": await message.reply("📢 ارسل الرسالة للاذاعة مع التثبيت")

    # 6. القوائم
    elif text == "قائمه العام": await message.reply(f"📝 المحظورين عام: {len(db['banned'])}")
    elif text == "المطورين": await message.reply(f"👑 المطورين:\n" + "\n".join([f"`{i}`" for i in db["devs"]]))
    elif text == "المطورين الثانويين": await message.reply("👑 المطورين الثانويين: لا يوجد")
    elif text == "مسح قائمه العام": db["banned"] = []; await message.reply("✅ تم مسح قائمة العام")
    elif text == "مسح المطورين": db["devs"] = [OWNER_ID]; await message.reply("✅ تم مسح المطورين وبقيت انت فقط")
    elif text == "مسح المطورين الثانويين": await message.reply("✅ تم مسح المطورين الثانويين")

    # 7. الباقي
    elif text == "اشتراك البوت": await message.reply("📅 اشتراك البوت: مدى الحياة")
    elif text == "تغيير اسم البوت": await message.reply("ارسل الاسم الجديد للبوت")
    elif text == "مسح اسم البوت": await message.reply("تم ارجاع اسم البوت الافتراضي")
    elif text == "تغيير المطور الاساسي": await message.reply("ارسل ايدي المطور الجديد")
    elif text == "ضع صوره للترحيب": await message.reply("ارسل الصورة الان")
    elif text == "تفعيل الاشتراك العام": await message.reply("✅ تم تفعيل الاشتراك العام")
    elif text == "تعطيل الاشتراك العام": await message.reply("❌ تم تعطيل الاشتراك العام")
    elif text == "تغيير كليشة الاشتراك": await message.reply("ارسل كليشة الاشتراك الجديدة")
    elif text == "مسح كليشة الاشتراك": await message.reply("✅ تم مسح كليشة الاشتراك")
    elif text == "جلب كليشة الاشتراك": await message.reply("كليشة الاشتراك: مرحبا بك اشترك بالقناة")
    elif text == "ضع تاريخ الاشتراك": await message.reply("ارسل تاريخ انتهاء الاشتراك")

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    if message.from_user.id == OWNER_ID:
        await message.reply("انا 𝐓𝐢𝐚 🌹\nارسل /المطور لفتح لوحة التحكم")
    else:
        if db["force"] and db["force_channel"]:
            await message.reply(f"❌ لازم تشترك في القناة اول\n{db['force_channel']}")
        else:
            await message.reply("انا 𝐓𝐢𝐚 🌹 جاهزة لحماية القروب")

print("TiaBot is running...")
app.run()
