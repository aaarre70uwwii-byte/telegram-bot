from pyrogram import filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from config import app, ADMIN_ID, db

def is_admin(user_id):
    return user_id == ADMIN_ID

main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("معلومات التنصيب")],
        [KeyboardButton("اعدادات البوت"), KeyboardButton("اعدادات الاساسي")],
        [KeyboardButton("اوامر الاشتراك الاجباري")],
        [KeyboardButton("اوامر الاذاعة"), KeyboardButton("الاوامر العامة")],
        [KeyboardButton("الغاء الامر")]
    ],
    resize_keyboard=True
)

# امر البدء
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    db["users"].add(message.from_user.id)
    text = f"""
AISED
/start
- اهلا بك عزيزي المطور الاساسي
- اليك كيبورد اوامر سورس اكس
- نوع البوت : مجاني
- ايديك: `{message.from_user.id}`
"""
    await message.reply(text, reply_markup=main_keyboard)

# كل الازرار
@app.on_message(filters.text)
async def buttons_handler(client, message: Message):
    user_id = message.from_user.id
    text = message.text

    if text == "معلومات التنصيب":
        await message.reply("**معلومات التنصيب:**\n1. ارفع السورس\n2. ضيف المتغيرات")
    
    elif text == "اعدادات البوت":
        if not is_admin(user_id): return await message.reply("❌ للمطور الاساسي فقط")
        await message.reply("**اعدادات البوت:**\nغير الاسم من @BotFather")
    
    elif text == "اعدادات الاساسي":
        if not is_admin(user_id): return await message.reply("❌ للمطور الاساسي فقط")
        await message.reply(f"**اعدادات المطور:**\nايديك: `{user_id}`\nعدد المستخدمين: `{len(db['users'])}`")
    
    elif text == "اوامر الاشتراك الاجباري":
        await message.reply(f"**الاشتراك الاجباري:**\nالحالية: `{db['channel'] or 'لا يوجد'}`")
    
    elif text == "اوامر الاذاعة":
        if not is_admin(user_id): return await message.reply("❌ للمطور الاساسي فقط")
        await message.reply(f"**الاذاعة:**\nرد على رسالة واكتب /broadcast\nالعدد: `{len(db['users'])}`")
    
    elif text == "الاوامر العامة":
        await message.reply("**العامة:**\n/start\n/id\n/ping\n/song")
    
    elif text == "الغاء الامر":
        await message.reply("تم الغاء الامر ✅", reply_markup=main_keyboard)

# امر الاذاعة
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(client, message: Message):
    if not message.reply_to_message: return await message.reply("رد على الرسالة")
    count = 0
    for user in db["users"]:
        try:
            await message.reply_to_message.copy(user)
            count += 1
        except: pass
    await message.reply(f"تمت الاذاعة لـ {count} مستخدم")
