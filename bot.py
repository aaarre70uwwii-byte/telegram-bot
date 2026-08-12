import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("RoseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# لوحة المطور
def dev_panel():
    keyboard = [
        [InlineKeyboardButton("الاحصائيات", callback_data="stats")],
        [InlineKeyboardButton("تغيير اسم البوت", callback_data="setname"), InlineKeyboardButton("مسح اسم البوت", callback_data="delname")],
        [InlineKeyboardButton("تفعيل التواصل", callback_data="on_contact"), InlineKeyboardButton("تعطيل التواصل", callback_data="off_contact")],
        [InlineKeyboardButton("تفعيل البوت الخدمي", callback_data="on_service"), InlineKeyboardButton("تعطيل البوت الخدمي", callback_data="off_service")],
        [InlineKeyboardButton("تفعيل الاشتراك الاجباري", callback_data="on_force"), InlineKeyboardButton("تعطيل الاشتراك الاجباري", callback_data="off_force")],
        [InlineKeyboardButton("الاشتراك الاجباري", callback_data="force_channel"), InlineKeyboardButton("تغيير الاشتراك الاجباري", callback_data="set_force")],
        [InlineKeyboardButton("تغيير كليشة الاشتراك", callback_data="set_force_msg"), InlineKeyboardButton("مسح كليشة الاشتراك", callback_data="del_force_msg")],
        [InlineKeyboardButton("جلب كليشة الاشتراك", callback_data="get_force_msg")],
        [InlineKeyboardButton("تفعيل الاشتراك العام", callback_data="on_public"), InlineKeyboardButton("تعطيل الاشتراك العام", callback_data="off_public")],
        [InlineKeyboardButton("اذاعه للمجموعات", callback_data="broadcast_groups"), InlineKeyboardButton("اذاعه خاص", callback_data="broadcast_users")],
        [InlineKeyboardButton("اذاعه بالتوجيه", callback_data="forward_broadcast"), InlineKeyboardButton("اذاعه بالتوجيه خاص", callback_data="forward_broadcast_users")],
        [InlineKeyboardButton("اذاعه بالتثبيت", callback_data="pin_broadcast")],
        [InlineKeyboardButton("قائمه العام", callback_data="banlist"), InlineKeyboardButton("المطورين", callback_data="devs"), InlineKeyboardButton("المطورين الثانويين", callback_data="sub_devs")],
        [InlineKeyboardButton("مسح قائمه العام", callback_data="del_banlist"), InlineKeyboardButton("مسح المطورين", callback_data="del_devs"), InlineKeyboardButton("مسح المطورين الثانويين", callback_data="del_sub_devs")],
        [InlineKeyboardButton("تغيير المطور الاساسي", callback_data="set_owner")],
        [InlineKeyboardButton("اشتراك البوت", callback_data="bot_sub"), InlineKeyboardButton("ضع تاريخ الاشتراك", callback_data="set_sub_date")],
        [InlineKeyboardButton("ضع صوره للترحيب", callback_data="set_welcome_pic")]
    ]
    return InlineKeyboardMarkup(keyboard)

@app.on_message(filters.command("المطور") & filters.private)
async def dev_cmd(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ هذا الامر للمطور فقط")
    await message.reply("👨‍💻 اهلا بك في لوحة المطور\nاختر الامر من الازرار بالاسفل:", reply_markup=dev_panel())

@app.on_callback_query()
async def callback(client, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("هذا الزر ليس لك", show_alert=True)
    
    if query.data == "stats":
        await query.message.edit_text("📊 **الاحصائيات**\nقريبا...")
    elif query.data == "broadcast_groups":
        await query.message.edit_text("📢 ارسل الان الرسالة اللي تريد اذاعتها للمجموعات")
    # تقدر تضيف باقي الازرار هنا بنفس الطريقة

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    if message.from_user.id == OWNER_ID:
        await message.reply("انا RoseBot 🌹\nارسل /المطور لفتح لوحة التحكم")
    else:
        await message.reply("انا RoseBot 🌹 جاهزة لحماية القروب")

print("RoseBot is running...")
app.run()
