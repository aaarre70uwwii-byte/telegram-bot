from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import sqlite3, os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ========= قاعدة البيانات =========
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS admins (chat_id INTEGER, user_id INTEGER, PRIMARY KEY(chat_id, user_id))""")
cursor.execute("""CREATE TABLE IF NOT EXISTS notes (chat_id INTEGER, name TEXT, text TEXT, PRIMARY KEY(chat_id, name))""")
cursor.execute("""CREATE TABLE IF NOT EXISTS whispers (id INTEGER PRIMARY KEY AUTOINCREMENT, to_id INTEGER, from_id INTEGER, text TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS commands (name TEXT PRIMARY KEY, value TEXT)""")
conn.commit()

# الاوامر الافتراضية
default_cmds = {
    "id": "id,ايدي,🆔 ايدي",
    "activate": "تفعيل",
    "ban": "🚫 حظر",
    "unban": "✅ فك حظر",
    "mute": "🔇 كتم",
    "unmute": "🔊 فك كتم",
    "kick": "👢 طرد",
    "promote": "⬆️ رفع ادمن",
    "demote": "⬇️ تنزيل ادمن"
}
for k,v in default_cmds.items():
    cursor.execute("INSERT OR IGNORE INTO commands (name, value) VALUES (?,?)", (k,v))
conn.commit()

def get_setting(key, default="0"):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    r = cursor.fetchone()
    return r[0] if r else default

def set_setting(key, value):
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()

def get_cmd(name):
    cursor.execute("SELECT value FROM commands WHERE name=?", (name,))
    r = cursor.fetchone()
    return r[0].split(",") if r else default_cmds.get(name,"").split(",")

def set_cmd(name, value):
    cursor.execute("INSERT OR REPLACE INTO commands (name, value) VALUES (?,?)", (name, value))
    conn.commit()

async def is_admin(app, chat_id, user_id):
    if user_id == OWNER_ID: return True
    cursor.execute("SELECT 1 FROM admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    return cursor.fetchone() is not None

# ========= اوامر الخاص =========
@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("لوحة المطور ⚙️", callback_data="dev_panel")]])
    await m.reply("مرحبا انا بوت ادارة 👋\nاضفني لمجموعتك واستخدم /m", reply_markup=kb)

@app.on_message(filters.private & filters.command("m"))
async def dev_panel(_, m: Message):
    if m.from_user.id!= OWNER_ID: return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("تفعيل الحماية", callback_data="lock_all_on"), InlineKeyboardButton("تعطيل الحماية", callback_data="lock_all_off")],
        [InlineKeyboardButton("منع الروابط", callback_data="lock_link_on"), InlineKeyboardButton("السماح بالروابط", callback_data="lock_link_off")],
        [InlineKeyboardButton("تفعيل الترحيب", callback_data="welcome_on"), InlineKeyboardButton("تعطيل الترحيب", callback_data="welcome_off")],
        [InlineKeyboardButton("⚙️ تغيير الاوامر", callback_data="change_cmd")]
    ])
    await m.reply("لوحة تحكم المطور:", reply_markup=kb)

@app.on_callback_query()
async def cb(_, q):
    if q.from_user.id!= OWNER_ID: return
    data = q.data
    if data == "lock_all_on": set_setting("lock_all", "1"); await q.answer("تم تفعيل الحماية")
    if data == "lock_all_off": set_setting("lock_all", "0"); await q.answer("تم تعطيل الحماية")
    if data == "lock_link_on": set_setting("lock_link", "1"); await q.answer("تم منع الروابط")
    if data == "lock_link_off": set_setting("lock_link", "0"); await q.answer("تم السماح بالروابط")
    if data == "welcome_on": set_setting("welcome", "1"); await q.answer("تم تفعيل الترحيب")
    if data == "welcome_off": set_setting("welcome", "0"); await q.answer("تم تعطيل الترحيب")

    if data == "change_cmd":
        text = "اختر الامر اللي تريد تغيره:\n\n"
        for k in default_cmds.keys():
            text += f"`{k}` = {', '.join(get_cmd(k))}\n"
        text += "\nارسل: `تغيير امر id`"
        await q.message.edit_text(text)
    await q.answer()

@app.on_message(filters.private & filters.text)
async def change_command(_, m: Message):
    if m.from_user.id!= OWNER_ID: return
    if m.text.startswith("تغيير امر "):
        parts = m.text.split(" ", 2)
        if len(parts) < 3: return await m.reply("الاستخدام: تغيير امر id\nبعدها ارسل الاوامر الجديدة مفصولة ب,")
        cmd_name = parts[2]
        if cmd_name not in default_cmds: return await m.reply("❌ الامر غير موجود")
        await m.reply(f"ارسل الاوامر الجديدة لـ `{cmd_name}`\nمثال: ايدي, id, myid", reply_to_message_id=m.id)
        set_setting("waiting_cmd", cmd_name)

    elif get_setting("waiting_cmd")!= "0":
        cmd_name = get_setting("waiting_cmd")
        set_cmd(cmd_name, m.text)
        set_setting("waiting_cmd", "0")
        await m.reply(f"✅ تم تغيير امر `{cmd_name}` الى: {m.text}")

# ========= اوامر القروب =========
@app.on_message(filters.group & filters.text)
async def group_cmds(_, m: Message):
    chat_id = m.chat.id; user_id = m.from_user.id; text = m.text

    if get_setting("lock_all") == "1" and not await is_admin(app, chat_id, user_id):
        try: await m.delete()
        except: pass
        return
    if get_setting("lock_link") == "1" and "http" in text and not await is_admin(app, chat_id, user_id):
        await m.delete(); return await m.reply("❌ الروابط ممنوعة")

    # امر الايدي بصورة
    if text in get_cmd("id"):
        user = await app.get_users(user_id)
        caption = f"🆔 ايديك: `{user_id}`\n👤 {m.from_user.first_name}\n📛 @{m.from_user.username or 'لا يوجد'}"
        try:
            if user.photo:
                photo = await app.download_media(user.photo.big_file_id)
                await m.reply_photo(photo, caption=caption)
            else:
                await m.reply(caption)
        except:
            await m.reply(caption)

    # امر التفعيل
    if text == get_cmd("activate")[0]:
        if await is_admin(app, chat_id, user_id):
            set_setting(f"active_{chat_id}", "1")
            await m.reply("✅ تم تفعيل البوت في المجموعة")
        else:
            await m.reply("❌ لازم تكون ادمن")

    # الهمسة
    if text.startswith("همسه"):
        parts = m.text.split(" ", 2)
        if len(parts) < 3: return await m.reply("الاستخدام: همسه @username النص")
        try:
            to = await app.get_users(parts[1].replace("@",""))
            cursor.execute("INSERT INTO whispers (to_id, from_id, text) VALUES (?,?,?)", (to.id, user_id, parts[2])); conn.commit()
            await m.reply(f"✅ تم ارسال همسة لـ {to.first_name}. قله `/whisper`")
        except: await m.reply("❌ المستخدم غير موجود")

    # اوامر الادمن بالرد
    if not m.reply_to_message: return
    if not await is_admin(app, chat_id, user_id): return
    target = m.reply_to_message.from_user.id

    if text in get_cmd("promote"):
        cursor.execute("INSERT OR IGNORE INTO admins (chat_id, user_id) VALUES (?,?)", (chat_id, target)); conn.commit()
        await m.reply("✅ تم رفع ادمن")
    elif text in get_cmd("demote"):
        cursor.execute("DELETE FROM admins WHERE chat_id=? AND user_id=?", (chat_id, target)); conn.commit()
        await m.reply("✅ تم تنزيل ادمن")
    elif text in get_cmd("ban"): await app.ban_chat_member(chat_id, target); await m.reply("✅ تم الحظر")
    elif text in get_cmd("unban"): await app.unban_chat_member(chat_id, target); await m.reply("✅ تم فك الحظر")
    elif text in get_cmd("mute"): await app.restrict_chat_member(chat_id, target, ChatPermissions()); await m.reply("✅ تم الكتم")
    elif text in get_cmd("unmute"): await app.restrict_chat_member(chat_id, target, ChatPermissions(can_send_messages=True)); await m.reply("✅ تم فك الكتم")
    elif text in get_cmd("kick"): await app.ban_chat_member(chat_id, target); await app.unban_chat_member(chat_id, target); await m.reply("✅ تم الطرد")

# ========= الترحيب =========
@app.on_chat_member_updated()
async def welcome(_, u):
    try:
        if u.new_chat_member and u.old_chat_member is None:
            if get_setting("welcome") == "1":
                await app.send_message(u.chat.id, f"مرحبا {u.new_chat_member.user.first_name} ❤️ نورت {u.chat.title}")
    except: pass

print("Bot is running...")
app.run()
