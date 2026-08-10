from pyrogram import Client, filters
from pyrogram.types import Message

# ضع بيانات البوت هنا
api_id = 1234567  # استبدل برقم الـ API ID
api_hash = "your_api_hash"  # استبدل الـ API Hash
bot_token = "your_bot_token"  # استبدل توكن البوت

app = Client("MyBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# ايدي المطور الخاص بك
DEV_ID = 123456789  # استبدل بايدي المطور


@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
  await message.reply(
      "أهلاً بك! أنا بوت حماية وألعاب وأغاني. استخدم الأوامر لمعرفة المساعد."
  )


# رد المطور
@app.on_message(filters.command("المطور") | filters.regex("من هو مطوري"))
async def dev_cmd(client: Client, message: Message):
  await message.reply("مبمج هذا البوت هو مطور البوت الذكي. ايديه: 123456789")


# قسم الحماية (مثال كتم عضو)
@app.on_message(filters.command("كتم") & filters.group)
async def mute_cmd(client: Client, message: Message):
  if not message.reply_to_message:
    return await message.reply("بالرد على الرسالة لكتم المستخدم.")
  user_id = message.reply_to_message.from_user.id
  # كود كتم المستخدم في المجموعة
  await message.chat.restrict_member(
      user_id, permissions=pyrogram.types.ChatPermissions()
  )
  await message.reply("تم كتم المستخدم بنجاح.")


# قسم الأوامر والبحث
@app.on_message(filters.command("بحث"))
async def search_cmd(client: Client, message: Message):
  query = message.text.split(None, 1)
  if len(query) < 2:
    return await message.reply("اكتب ما تريد البحث عنه بعد الأمر.")
  await message.reply(f"جاري البحث عن: {query[1]}")


# قسم الهمسات
@app.on_message(filters.command("همسة"))
async def whisper_cmd(client: Client, message: Message):
  await message.reply("خاصية الهمسات تتيح إرسال رسالة لا يراها غير الشخص المقصود.")


# تشغيل البوت
print("البوت يعمل الان...")
app.run()
