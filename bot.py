from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus
import sqlite3, os, re

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("tia_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) # غيرت الاسم لتيا

# ========= قاعدة البيانات =========
conn = sqlite3.connect("tia.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS admins (chat_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY(chat_id, user_id))""")
cursor.execute("""CREATE TABLE IF NOT EXISTS whispers (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, to_id INTEGER, from_id INTEGER, text TEXT, seen INTEGER DEFAULT 0)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS commands (name TEXT PRIMARY KEY, value TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS welcome (chat_id INTEGER PRIMARY KEY, text TEXT, photo TEXT)""") # جدول الترحيب
conn.commit()

# الاوامر الافتراضية
default_cmds = {
    "id": "id,ايدي,ا,🆔 ايدي",
    "activate": "تفعيل",
    "ban": "🚫 حظر",
    "unban": "✅ فك حظر",
    "mute": "🔇 كتم",
    "unmute": "🔊 فك كتم",
    "kick": "👢 طرد",
    "promote_mod": "⬆️ رفع مدير",
    "promote_owner": "⬆️ رفع مالك",
    "promote_dev": "⬆️ رفع مطور",
    "promote_sudo": "⬆️ رفع مالك اساسي",
    "demote": "⬇️ تنزيل",
    "whisper": "همسه,همس,whisper",
    "setwelcome": "ضع ترحيب,وضع ترحيب" # امر جديد
}
for k,v in default_cmds.items():
    cursor.execute("INSERT OR IGNORE INTO commands (name, value) VALUES (?,?)", (k,v))
conn.commit()

def get_setting(key, default="0"):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,)); r = cursor.fetchone()
    return r[0] if r else default
def set_setting(key, value):
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value)); conn.commit()
def get_cmd(name):
    cursor.execute("SELECT value FROM commands WHERE name=?", (name,)); r = cursor.fetchone()
    return r[0].split(",") if r else default_cmds.get(name,"").split(",")

def get_rank(chat_id, user_id):
    if user_id == OWNER_ID: return "sudo"
    cursor.execute("SELECT rank FROM admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    r = cursor.fetchone()
    return r[0] if r else "member"

ranks = {"member":0, "mod":1, "owner":2, "dev":3, "sudo":4}
async def has_permission(app, chat_id, user_id, need_rank):
    user_rank = get_rank(chat_id, user_id)
    return ranks.get(user_rank, 0) >= ranks.get(need_rank, 0)

# ========= اوامر الخاص =========
@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
    name = m.from_user.first_name
    text = f"🌹 مرحبا {name} انا بوت تيا\n\n"
    text += "اضفني لمجموعتك واكتب `تفعيل`\n"
    text += "اوامري: ا - همسه - رفع مدير"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("اضفني لمجموعة", url=f"https://t.me/{(await app.get_me()).username}?startgroup=true")]])
    await m.reply(text, reply_markup=kb)

@app.on_message(filters.private & filters.command("whisper"))
async def check_whisper(_, m: Message):
    cursor.execute("SELECT id, from_id, text FROM whispers WHERE to_id=? AND seen=0", (m.from_user.id,))
    r = cursor.fetchone()
    if r:
        from_user = await app.get_users(r[1])
        await m.reply(f"📩 همسة جديدة من {from_user.first_name}\n\n{r[2]}")
        cursor.execute("UPDATE whispers SET seen=1 WHERE id=?", (r[0],)); conn.commit()
    else:
        await m.reply("❌ ما عندك همسات جديدة")

# ========= اوامر القروب =========
@app.on_message(filters.group & filters.text)
async def group_cmds(_, m: Message):
    chat_id = m.chat.id; user_id = m.from_user.id; text = m.text.strip()

    if get_setting(f"active_{chat_id}")!= "1" and text not in get_cmd("activate"): return

    # الحماية
    if get_setting("lock_all") == "1" and not await has_permission(app, chat_id, user_id, "mod"):
        try: await m.delete(); return
        except: pass
    if get_setting("lock_link") == "1" and re.search(r'http|t.me|@', text) and not await has_permission(app, chat_id, user_id, "mod"):
        await m.delete(); return await m.reply("❌ الروابط ممنوعة")

    # امر الايدي
    if text in get_cmd("id"):
        user = await app.get_users(user_id)
        rank = get_rank(chat_id, user_id)
        caption = f"🆔 ايديك: `{user_id}`\n👤 {m.from_user.first_name}\n🏷️ رتبتك: {rank}\n📛 @{m.from_user.username or 'لا يوجد'}"
        try:
            if user.photo:
                photo = await app.download_media(user.photo.big_file_id)
                await m.reply_photo(photo, caption=caption)
            else:
                await m.reply(caption)
        except: await m.reply(caption)

    # امر التفعيل
    if text in get_cmd("activate"):
        if await has_permission(app, chat_id, user_id, "mod"):
            set_setting(f"active_{chat_id}", "1")
            await m.reply("✅ تم تفعيل بوت تيا في المجموعة")
        else:
            await m.reply("❌ لازم تكون مدير")

    # امر وضع الترحيب: رد على صورة واكتب "ضع ترحيب مرحبا بك {name}"
    if text in get_cmd("setwelcome") and await has_permission(app, chat_id, user_id, "owner"):
        if m.reply_to_message and m.reply_to_message.photo:
            photo_id = m.reply_to_message.photo.file_id
            welcome_text = text.replace("ضع ترحيب","").replace("وضع ترحيب","").strip()
            if not welcome_text: welcome_text = "مرحبا {name} نورت {chat}"
            cursor.execute("INSERT OR REPLACE INTO welcome VALUES (?,?,?)", (chat_id, welcome_text, photo_id)); conn.commit()
            await m.reply("✅ تم حفظ الترحيب بالصورة")
        else:
            await m.reply("الاستخدام: رد على صورة واكتب `ضع ترحيب مرحبا بك {name}`")

    # امر الهمس
    if any(text.startswith(x) for x in get_cmd("whisper")):
        parts = text.split(" ", 2)
        if len(parts) < 3: return await m.reply("الاستخدام: `همسه @username النص`")
        try:
            to_user = await app.get_users(parts[1].replace("@",""))
            cursor.execute("INSERT INTO whispers (chat_id, to_id, from_id, text) VALUES (?,?,?,?)", (chat_id, to_user.id, user_id, parts[2])); conn.commit()
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("اضغط لعرض الهمسة 🔒", url=f"t.me/{(await app.get_me()).username}?start=whisper")]])
            await m.reply(f"✅ تم ارسال همسة سرية لـ {to_user.first_name}", reply_markup=kb)
        except: await m.reply("❌ المستخدم غير موجود")

    if not m.reply_to_message: return
    target = m.reply_to_message.from_user.id
    my_rank = get_rank(chat_id, user_id)
    target_rank = get_rank(chat_id, target)

    if ranks[my_rank] <= ranks[target_rank] and user_id!= OWNER_ID:
        return await m.reply("❌ ما تقدر على شخص رتبته اعلى منك")

    # اوامر الرفع
    if text in get_cmd("promote_mod") and await has_permission(app, chat_id, user_id, "owner"):
        cursor.execute("INSERT OR REPLACE INTO admins VALUES (?,?,?)", (chat_id, target, "mod")); conn.commit()
        await m.reply("✅ تم رفع مدير")
    elif text in get_cmd("promote_owner") and await has_permission(app, chat_id, user_id, "dev"):
        cursor.execute("INSERT OR REPLACE INTO admins VALUES (?,?,?)", (chat_id, target, "owner")); conn.commit()
        await m.reply("✅ تم رفع مالك")
    elif text in get_cmd("promote_dev") and await has_permission(app, chat_id, user_id, "sudo"):
        cursor.execute("INSERT OR REPLACE INTO admins VALUES (?,?,?)", (chat_id, target, "dev")); conn.commit()
        await m.reply("✅ تم رفع مطور")
    elif text in get_cmd("promote_sudo") and user_id == OWNER_ID:
        cursor.execute("INSERT OR REPLACE INTO admins VALUES (?,?,?)", (chat_id, target, "sudo")); conn.commit()
        await m.reply("✅ تم رفع مالك اساسي")
    elif text in get_cmd("demote") and await has_permission(app, chat_id, user_id, "owner"):
        cursor.execute("DELETE FROM admins WHERE chat_id=? AND user_id=?", (chat_id, target)); conn.commit()
        await m.reply("✅ تم التنزيل")

    # اوامر الادارة
    elif text in get_cmd("ban") and await has_permission(app, chat_id, user_id, "mod"):
        await app.ban_chat_member(chat_id, target); await m.reply("✅ تم الحظر")
    elif text in get_cmd("kick") and await has_permission(app, chat_id, user_id, "mod"):
        await app.ban_chat_member(chat_id, target); await app.unban_chat_member(chat_id, target); await m.reply("✅ تم الطرد")

# ========= الترحيب بالصورة =========
@app.on_chat_member_updated()
async def welcome(_, u):
    try:
        if u.new_chat_member and u.old_chat_member is None: # شخص دخل
            chat_id = u.chat.id
            cursor.execute("SELECT text, photo FROM welcome WHERE chat_id=?", (chat_id,))
            r = cursor.fetchone()
            name = u.new_chat_member.user.first_name
            chat_name = u.chat.title

            if r:
                welcome_text = r[0].replace("{name}", name).replace("{chat}", chat_name)
                photo_id = r[1]
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("قوانين المجموعة", callback_data="rules")]])
                await app.send_photo(chat_id, photo_id, caption=welcome_text, reply_markup=kb)
            else:
                # ترحيب افتراضي
                await app.send_message(chat_id, f"🌹 مرحبا {name} نورت {chat_name}")
    except: pass

print("Tia Bot is running...")
app.run()
