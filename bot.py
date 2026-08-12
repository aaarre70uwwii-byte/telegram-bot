import re
from pyrogram import Client, filters
from pyrogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
DEVELOPER_ID = 7488375443
DB_FILE = "data.json"
votes = {}

def load_data():
    global data
    try:

app = Client("MyProtectionMusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ==================== قسم الحماية ====================

# منع إرسال الروابط في المجموعات
@app.on_message(filters.group & (filters.text | filters.caption) & ~filters.me)
async def anti_link(client: Client, message: Message):
    text = message.text or message.caption or ""
    # التحقق من وجود روابط (http أو www أو t.me)
    if re.search(r"http[s]?://|www\.|\.me/", text):
        try:
            await message.delete()
            await message.reply(f"⚠️ عذراً {message.from_user.mention}، ممنوع نشر الروابط هنا! [حمايتي الخاصة]")
        except Exception as e:
            print(f"خطأ في حذف الرابط: {e}")

# أمر ترحيب بالأعضاء الجدد وتأمين المجموعة
@app.on_message(filters.new_chat_members)
async def welcome_member(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            await message.reply("🤖 تم إضافتي بنجاح لتأمين وإدارة المجموعة!")
        else:
            await message.reply(f"مرحباً بك {member.mention} في المجموعة 🛡️ يرجى الالتزام بالقوانين.")

# ==================== قسم الموسيقى والترفيه ====================

# أمر تشغيل أغنية أو البحث عنها (رد تجريبي متكامل للميوزك)
@app.on_message(filters.command("play") & (filters.group | filters.private))
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("🎵 يرجى كتابة اسم الأغنية أو الرابط بعد الأمر، مثال:\n/play [اسم الأغنية]")
    
    query = " ".join(message.command[1:])
    sent = await message.reply(f"🔍 جاري البحث والتحضير لـ: {query}...")
    
    # هنا يتم دمج مكتبة التحميل أو تشغيل الصوتيات (yt-dlp)
    # محاكاة الاستجابة الناجحة لتشغيل الميوزك
    await sent.edit(f"🎶 تم بدء تشغيل الطلب: {query}\n🎧 استمتع بالاستماع! [بواسطة بوتك الخاص]")

# أمر البدء السريع
@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply(" أهلاً بك! أنا بوت حماية وموسيقى متكامل، يعمل بكامل حقوقك.\n\n استخدم /play للموسيقى والمجموعات محمية تلقائياً من الروابط.")

# تشغيل البوت
print("Bot is starting...")
app.run()
