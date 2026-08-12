import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7488375443

app = Client("TiaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

conn = sqlite3.connect("tia.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS devs (id INTEGER PRIMARY KEY)")
cursor.execute("INSERT OR IGNORE INTO devs (id) VALUES (7488375443)")
conn.commit()

def get_setting(key, default="1"):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    r = cursor.fetchone()
    return r[0] if r else default

def set_setting(key, value):
    cursor.execute("REPLACE INTO settings (key,value) VALUES (?,?)", (key,value))
    conn.commit()

def is_dev(user_id):
    cursor.execute("SELECT id FROM devs WHERE id=?", (user_id,))
    return cursor.fetchone() is not None or user_id == OWNER_ID

def dev_keyboard():
    keyboard = [
        [KeyboardButton("الاحصائيات")],
        [KeyboardButton("تفعيل التواصل"), KeyboardButton("تعطيل التواصل")],
        [KeyboardButton("تفعيل البوت الخدمي"), KeyboardButton("تعطيل البوت الخدمي")],
        [KeyboardButton("اذاعه للمجموعات"), KeyboardButton("اذاعه للخاص")],
        [KeyboardButton("قائمه العام"), KeyboardButton("مسح قائمه العام")],
        [KeyboardButton("المطورين"), KeyboardButton("اضافه مطور")],
        [KeyboardButton("حظر"), KeyboardButton("الغاء الحظر")],
        [KeyboardButton("ضع صوره ترحيب"), KeyboardButton("رد المطور")],
        [KeyboardButton("اخفاء اللوحه")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

waiting = {}

@app.on_message(filters.command("المطور") & filters.private)
async def show_panel(client, message: Message):
    if not is_dev(message.from_user.id):
        return await message.reply("❌ هذا الامر للمطورين فقط")
    await message.reply("👨‍💻 اهلا بك يا مطور Tia", reply_markup=dev_keyboard())

@app.on_message(filters.private)
async def save_user(client, message: Message):
    if not is_dev(message.from_user.id):
        cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (message.from_user.id,))
        conn.commit()

@app.on_message(filters.text & filters.private)
async def dev_buttons(client, message: Message):
    global waiting
    text = message.text.strip() # ضفت strip
    uid = message.from_user.id

    if not is_dev(uid):
        return

    if waiting.get(uid) == "broadcast":
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()
        count = 0
        for u in users:
            try:
                await app.send_message(u[0], text)
                count += 1
            except: pass
        waiting[uid] = None
        return await message.reply(f"✅ تمت الاذاعة لـ {count} عضو")

    if waiting.get(uid) == "ban":
        cursor.execute("INSERT OR IGNORE INTO settings (key,value) VALUES (?,?)", (f"ban_{text}","1"))
        conn.commit()
        waiting[uid] = None
        return await message.reply(f"✅ تم حظر: {text}")

    if waiting.get(uid) == "unban":
        cursor.execute("DELETE FROM settings WHERE key=?", (f"ban_{text}",))
        conn.commit()
        waiting[uid] = None
        return await message.reply(f"✅ تم فك الحظر: {text}")

    if waiting.get(uid) == "dev":
        cursor.execute("INSERT OR IGNORE INTO devs (id) VALUES (?)", (int(text),))
        conn.commit()
        waiting[uid] = None
        return await message.reply(f"✅ تم اضافة المطور: {text}")

    if waiting.get(uid) == "photo" and message.photo:
        set_setting("welcome_pic", message.photo.file_id)
        waiting[uid] = None
        return await message.reply("✅ تم حفظ صورة الترحيب")

    # برمجة الازرار - خليتها if منفصلة
    if text == "الاحصائيات":
        cursor.execute("SELECT COUNT(*) FROM users")
        c = cursor.fetchone()[0]
        await message.reply(f"📊 احصائيات Tia\nالاعضاء: {c}\nالبوت الخدمي: {'مفعل' if get_setting('service')=='1' else 'معطل'}")

    if text == "تفعيل التواصل": set_setting("contact","1"); await message.reply("✅ تم تفعيل التواصل")
    if text == "تعطيل التواصل": set_setting("contact","0"); await message.reply("❌ تم تعطيل التواصل")
    if text == "تفعيل البوت الخدمي": set_setting("service","1"); await message.reply("✅ تم تفعيل البوت الخدمي")
    if text == "تعطيل البوت الخدمي": set_setting("service","0"); await message.reply("❌ تم تعطيل البوت الخدمي")

    if text == "اذاعه للمجموعات" or text == "اذاعه للخاص":
        waiting[uid] = "broadcast"
        await message.reply("📢 ارسل الرسالة الان للاذاعة")

    if text == "قائمه العام":
        cursor.execute("SELECT key FROM settings WHERE key LIKE 'ban_%'")
        banned = [x[0].replace("ban_","") for x in cursor.fetchall()]
        await message.reply("المحظورين: " + str(banned) if banned else "قائمه العام فاضيه")
    if text == "مسح قائمه العام":
        cursor.execute("DELETE FROM settings WHERE key LIKE 'ban_%'")
        conn.commit(); await message.reply("✅ تم مسح قائمه العام")

    if text == "المطورين":
        cursor.execute("SELECT id FROM devs")
        devs = [str(x[0]) for x in cursor.fetchall()]
        await message.reply("👑 المطورين:\n" + "\n".join(devs))
    if text == "اضافه مطور":
        waiting[uid] = "dev"; await message.reply("ارسل ايدي المطور الجديد")

    if text == "حظر": waiting[uid] = "ban"; await message.reply("ارسل ايدي العضو للحظر")
    if text == "الغاء الحظر": waiting[uid] = "unban"; await message.reply("ارسل ايدي العضو لفك الحظر")

    if text == "ضع صوره ترحيب":
        waiting[uid] = "photo"; await message.reply("ارسل الصورة الان")
    if text == "رد المطور":
        pic = get_setting("welcome_pic", None)
        if pic: await message.reply_photo(photo=pic, caption="رد المطور")
        else: await message.reply("❌ لم تضع صورة ترحيب بعد")

    if text == "اخفاء اللوحه":
        await message.reply("✅ تم اخفاء اللوحه", reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True))

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    cursor.execute("SELECT value FROM settings WHERE
