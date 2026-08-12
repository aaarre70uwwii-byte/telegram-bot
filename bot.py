import os
import sqlite3
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ChatPermissions

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7488375443

app = Client("TiaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ========== قاعدة البيانات ==========
conn = sqlite3.connect("tia.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS devs (id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS ranks (chat_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY(chat_id, user_id))")
cursor.execute("CREATE TABLE IF NOT EXISTS replies (word TEXT PRIMARY KEY, reply TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS whispers (id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER, target_id INTEGER, text TEXT, read INTEGER DEFAULT 0)")
cursor.execute("INSERT OR IGNORE INTO devs (id) VALUES (7488375443)")
conn.commit()

# ========== الدوال المساعدة ==========
def is_dev(user_id):
    cursor.execute("SELECT id FROM devs WHERE id=?", (user_id,))
    return cursor.fetchone() is not None or user_id == OWNER_ID

def get_setting(key, default="0"):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    r = cursor.fetchone()
    return r[0] if r else default

def set_setting(key, value):
    cursor.execute("REPLACE INTO settings (key,value) VALUES (?,?)", (key,value))
    conn.commit()

def get_rank(chat_id, user_id):
    cursor.execute("SELECT rank FROM ranks WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    r = cursor.fetchone()
    return r[0] if r else "عضو"

def set_rank(chat_id, user_id, rank):
    if rank == "عضو":
        cursor.execute("DELETE FROM ranks WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    else:
        cursor.execute("REPLACE INTO ranks (chat_id,user_id,rank) VALUES (?,?,?)", (chat_id, user_id, rank))
    conn.commit()

def can_promote(my_rank, target_rank):
    ranks = {"عضو":0, "ادمن":1, "مدير":2, "مالك":3, "مالك اساسي":4}
    return ranks.get(my_rank,0) > ranks.get(target_rank,0)

# ========== الكيبوردات ==========
def public_keyboard():
    keyboard = [
        [KeyboardButton("اوامر الادمن"), KeyboardButton("اوامر القفل"), KeyboardButton("اوامر التسليه")],
        [KeyboardButton("الايدي"), KeyboardButton("الهمسات")],
        [KeyboardButton("الرئيسية")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def dev_keyboard():
    keyboard = [
        [KeyboardButton("الاحصائيات")],
        [KeyboardButton("اذاعة للمجموعات"), KeyboardButton("اذاعة للخاص")],
        [KeyboardButton("قائمة المحظورين"), KeyboardButton("مسح المحظورين")],
        [KeyboardButton("المطورين"), KeyboardButton("اضافة مطور")],
        [KeyboardButton("حظر عضو"), KeyboardButton("فك الحظر")],
        [KeyboardButton("وضع صورة ترحيب"), KeyboardButton("عرض صورة الترحيب")],
        [KeyboardButton("اخفاء اللوحة")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

waiting = {}
nokat = ["واحد محش راح المدرسة قال للاستاذ انا جيت متأخر عشان كنت نايم 😂", "واحد غبي اشترى جوال بزراير عشان الشاشة ما تنكسر"]
questions = ["لو معك مليون دولار ايش بتسوي؟", "ايش اكثر شي تخاف منه؟", "تحب السفر ولا الجلوس في البيت؟"]

# ========== حفظ البيانات ==========
@app.on_message(filters.group | filters.private)
async def save_data(client, message: Message):
    if message.from_user:
        cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (message.from_user.id,))
    if message.chat.type in ["group", "supergroup"]:
        cursor.execute("INSERT OR IGNORE INTO groups (id) VALUES (?)", (message.chat.id,))
    conn.commit()

# ========== /start ==========
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    cursor.execute("SELECT value FROM settings WHERE key=?", (f"ban_{message.from_user.id}",))
    if cursor.fetchone():
        return await message.reply("❌ انت محظور من استخدام البوت")
    await message.reply("**اهلا بك في بوت Tia** 🌹\nاختر من القائمة", reply_markup=public_keyboard())

# ========== /المطور ==========
@app.on_message(filters.command("المطور") & filters.private)
async def dev_panel(client, message: Message):
    if not is_dev(message.from_user.id):
        return await message.reply("❌ هذا الامر للمطور فقط")
    pic = get_setting("welcome_pic", None)
    if pic:
        await message.reply_photo(photo=pic, caption="**لوحة تحكم المطور** 👨‍💻", reply_markup=dev_keyboard())
    else:
        await message.reply("**لوحة تحكم المطور** 👨‍💻", reply_markup=dev_keyboard())

# ========== الايدي ==========
@app.on_message(filters.command("الايدي") | filters.command("id") | filters.text & filters.regex("^الايدي$"))
async def get_id(client, message: Message):
    user = message.from_user if not message.reply_to_message else message.reply_to_message.from_user
    photos = [p async for p in app.get_chat_photos(user.id, limit=1)]
    photo = photos[0].file_id if photos else None
    rank = get_rank(message.chat.id, user.id) if message.chat.type!= "private" else "خاص"
    text = f"""**بطاقة العضو**
━━━━━━━━━━━━━━
**الاسم**: {user.first_name}
**الايدي**: `{user.id}`
**اليوزر**: @{user.username if user.username else "لا يوجد"}
**الرتبة**: {rank}
━━━━━━━━━━━━━━"""
    if photo:
        await message.reply_photo(photo=photo, caption=text)
    else:
        await message.reply(text)

# ========== الهمسات ==========
@app.on_message(filters.command("همس") | filters.text & filters.regex("^همسة$"))
async def whisper(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ رد على الشخص اللي تريد تهمس له")
    target_id = message.reply_to_message.from_user.id
    sender = message.from_user.first_name
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"📨 همسة من {sender}", callback_data=f"whisper_{target_id}_{message.from_user.id}")]])
    await message.reply("✅ تم ارسال اشعار الهمسة", reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"whisper_(\d+)_(\d+)"))
async def show_whisper(client, callback):
    data = callback.data.split("_")
    target_id, sender_id = int(data[1]), int(data[2])
    if callback.from_user.id!= target_id:
        return await callback.answer("❌ هذه الهمسة ليست لك", show_alert=True)
    await callback.answer("اكتب الهمسة الان في الخاص", show_alert=True)
    waiting[sender_id] = f"whisper_to_{target_id}"

@app.on_message(filters.private & filters.text)
async def get_whisper_text(client, message: Message):
    uid = message.from_user.id
    if uid in waiting and waiting[uid].startswith("whisper_to_"):
        target_id = int(waiting[uid].split("_")[-1])
        cursor.execute("INSERT INTO whispers (sender_id,target_id,text) VALUES (?,?,?)",(uid, target_id, message.text))
        conn.commit()
        try:
            await app.send_message(target_id, f"📨 لديك همسة جديدة\nارسل /الهمسات لقراءتها")
            await message.reply("✅ تم ارسال الهمسة")
        except:
            await message.reply("❌ مقدر ارسل للشخص")
        waiting[uid] = None

@app.on_message(filters.command("الهمسات") | filters.text & filters.regex("^الهمسات$"))
async def read_whispers(client, message: Message):
    uid = message.from_user.id
    cursor.execute("SELECT id,sender_id,text FROM whispers WHERE target_id=? AND read=0", (uid,))
    whispers = cursor.fetchall()
    if not whispers:
        return await message.reply("📭 لا توجد همسات جديدة")
    text = "**📨 همساتك الجديدة:**\n━━━━━━━━━━━━━━\n"
    for w in whispers:
        sender = await app.get_users(w[1])
        text += f"**من**: {sender.first_name}\n**الهمسة**: {w[2]}\n━━━━━━━━━━━━━━\n"
        cursor.execute("UPDATE whispers SET read=1 WHERE id=?", (w[0],))
    conn.commit()
    await message.reply(text)

# ========== الردود التلقائية ==========
@app.on_message(filters.text & ~filters.command(["start","المطور","الايدي","الهمسات"]))
async def auto_reply(client, message: Message):
    word = message.text.strip()
    cursor.execute("SELECT reply FROM replies WHERE word=?", (word,))
    r = cursor.fetchone()
    if r:
        return await message.reply(r[0])
    if "السلام عليكم" in word:
        await message.reply("وعليكم السلام ورحمة الله ❤️")
    elif "شلونك" in word:
        await message.reply("الحمدلله بخير وانت؟")

# ========== ازرار الكيبورد العام ==========
@app.on_message(filters.text)
async def public_buttons(client, message: Message):
    text, uid, chat_id = message.text, message.from_user.id, message.chat.id
    cursor.execute("SELECT value FROM settings WHERE key=?", (f"ban_{uid}",))
    if cursor.fetchone() and not is_dev(uid):
        return

    try:
        member = await app.get_chat_member(chat_id, uid)
    except:
        member = None
    is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or get_rank(chat_id, uid)!= "عضو" if member else False

    if text == "اوامر الادمن":
        kb = ReplyKeyboardMarkup([
            [KeyboardButton("حظر عضو"), KeyboardButton("فك الحظر")],
            [KeyboardButton("كتم عضو"), KeyboardButton("فك الكتم")],
            [KeyboardButton("طرد عضو")],
            [KeyboardButton("رفع ادمن"), KeyboardButton("تنزيل ادمن")],
            [KeyboardButton("رفع مدير"), KeyboardButton("تنزيل مدير")],
            [KeyboardButton("رفع مالك"), KeyboardButton("تنزيل مالك")],
            [KeyboardButton("رفع مالك اساسي"), KeyboardButton("تنزيل مالك اساسي")],
            [KeyboardButton("الرئيسية")]
        ], resize_keyboard=True)
        await message
