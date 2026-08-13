import threading, asyncio
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions
from pyrogram.errors import FloodWait, RPCError
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from database import *

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "TiaBot V4 OK"
def run_flask(): app_flask.run(host='0.0.0.0', port=8080)

app = Client("TiaBotV4", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
waiting = {}

def dev_kb():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📊 الاحصائيات")],
        [KeyboardButton("✅ تفعيل الخدمي"), KeyboardButton("❌ تعطيل الخدمي")],
        [KeyboardButton("🛡️ الحماية"), KeyboardButton("👮 الادمنية")],
        [KeyboardButton("📢 اذاعة")],
        [KeyboardButton("🗑️ اخفاء")]
    ], resize_keyboard=True)

def admin_kb():
    return ReplyKeyboardMarkup([
        [KeyboardButton("⬆️ رفع ادمن"), KeyboardButton("⬇️ تنزيل ادمن")],
        [KeyboardButton("🚫 حظر"), KeyboardButton("✅ فك حظر")],
        [KeyboardButton("🔇 كتم"), KeyboardButton("🔊 فك كتم")],
        [KeyboardButton("👢 طرد")],
        [KeyboardButton("رجوع")]
    ], resize_keyboard=True)

async def is_admin(app, chat_id, user_id):
    if is_dev(user_id): return True
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or is_admin_db(chat_id, user_id)
    except: return False

# ========= الاوامر الخاصة =========
@app.on_message(filters.command("start") & filters.private)
async def start(_, m: Message):
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (m.from_user.id, m.from_user.username))
    if is_dev(m.from_user.id):
        await m.reply("👨‍💻 مرحبا بك في TiaBot V4", reply_markup=dev_kb())
    else:
        if get_setting("service") == "0": return await m.reply("❌ الخدمي معطل")
        await m.reply("🌹 ارسل رسالتك للمطور")

@app.on_message(filters.command(["m", "المطور"]) & filters.private)
async def panel(_, m: Message):
    if not is_dev(m.from_user.id): return
    await m.reply("لوحة التحكم:", reply_markup=dev_kb())

@app.on_message(filters.command("whisper") & filters.private)
async def my_whisper(_, m: Message):
    r = cursor.execute("SELECT text, from_id FROM whispers WHERE to_id=? ORDER BY id DESC LIMIT 1", (m.from_user.id,)).fetchone()
    if r:
        u = await app.get_users(r[1])
        await m.reply(f"📩 همسة من {u.first_name}:\n`{r[0]}`")
        cursor.execute("DELETE FROM whispers WHERE to_id=?", (m.from_user.id,)); conn.commit()
    else: await m.reply("❌ لا توجد همسات")

# ========= لوحة المطور =========
@app.on_message(filters.text & filters.private)
async def dev_panel(_, m: Message):
    global waiting
    if not is_dev(m.from_user.id): return
    t = m.text
    if t == "📊 الاحصائيات":
        c = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        await m.reply(f"📊 الاعضاء: {c}")
    elif t == "✅ تفعيل الخدمي": set_setting("service","1"); await m.reply("✅ تم التفعيل")
    elif t == "❌ تعطيل الخدمي": set_setting("service","0"); await m.reply("❌ تم التعطيل")
    elif t == "📢 اذاعة": waiting[m.from_user.id] = "bc"; await m.reply("ارسل الرسالة للاذاعة")
    elif t == "🛡️ الحماية":
        await m.reply("الحماية:", reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("قفل الروابط"), KeyboardButton("فتح الروابط")],
            [KeyboardButton("قفل الكل"), KeyboardButton("فتح الكل")], [KeyboardButton("رجوع")]
        ], resize_keyboard=True))
    elif t == "قفل الروابط": set_setting("lock_link","1"); await m.reply("✅ تم قفل الروابط")
    elif t == "فتح الروابط": set_setting("lock_link","0"); await m.reply("✅ تم فتح الروابط")
    elif t == "قفل الكل": set_setting("lock_all","1"); await m.reply("✅ تم قفل كل شي")
    elif t == "فتح الكل": set_setting("lock_all","0"); await m.reply("✅ تم فتح كل شي")
    elif t == "👮 الادمنية": await m.reply("استخدم الازرار في القروب بالرد", reply_markup=admin_kb())
    elif t == "🗑️ اخفاء": await m.reply("تم الاخفاء", reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True))
    elif t == "رجوع": await m.reply("رجوع", reply_markup=dev_kb())
    elif waiting.get(m.from_user.id) == "bc":
        waiting[m.from_user.id] = None; await broadcast(app, m)

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

    if text.lower() in ["id", "ايدي", "🆔 ايدي"]:
        await m.reply(f"🆔 ايديك: `{user_id}`\n👤 {m.from_user.first_name}")

    if text.startswith("همسه"):
        parts = text.split(" ", 2)
        if len(parts) < 3: return
        try:
            to = await app.get_users(parts[1].replace("@",""))
            cursor.execute("INSERT INTO whispers (to_id, from_id, text) VALUES (?,?,?)", (to.id, user_id, parts[2])); conn.commit()
            await m.reply(f"✅ تم ارسال همسة لـ {to.first_name}. قله /whisper")
        except: await m.reply("❌ خطأ")

    if not m.reply_to_message: return
    if not await is_admin(app, chat_id, user_id): return
    target = m.reply_to_message.from_user.id

    if text in ["⬆️ رفع ادمن"]:
        cursor.execute("INSERT OR IGNORE INTO admins (chat_id, user_id) VALUES (?,?)", (chat_id, target)); conn.commit()
        await m.reply("✅ تم رفع ادمن")
    elif text in ["⬇️ تنزيل ادمن"]:
        cursor.execute("DELETE FROM admins WHERE chat_id=? AND user_id=?", (chat_id, target)); conn.commit()
        await m.reply("✅ تم تنزيل ادمن")
    elif text in ["🚫 حظر"]: await app.ban_chat_member(chat_id, target); await m.reply("✅ تم الحظر")
    elif text in ["✅ فك حظر"]: await app.unban_chat_member(chat_id, target); await m.reply("✅ تم فك الحظر")
    elif text in ["🔇 كتم"]: await app.restrict_chat_member(chat_id, target, ChatPermissions()); await m.reply("✅ تم الكتم")
    elif text in ["🔊 فك كتم"]: await app.restrict_chat_member(chat_id, target, ChatPermissions(can_send_messages=True)); await m.reply("✅ تم فك الكتم")
    elif text in ["👢 طرد"]: await app.ban_chat_member(chat_id, target); await app.unban_chat_member(chat_id, target); await m.reply("✅ تم الطرد")

# ========= الملاحظات =========
@app.on_message(filters.group & filters.command(["save", "حفظ"]))
async def save_note(_, m: Message):
    if not await is_admin(app, m.chat.id, m.from_user.id): return
    if not m.reply_to_message: return await m.reply("رد على رسالة")
    name = m.text.split(" ", 1)[1]
    content = m.reply_to_message.text or m.reply_to_message.caption
    cursor.execute("REPLACE INTO notes VALUES (?,?,?)", (m.chat.id, name, content)); conn.commit()
    await m.reply(f"✅ تم حفظ `{name}`")

@app.on_message(filters.group & filters.command(["note", "ملاحظة"]))
async def get_note(_, m: Message):
    name = m.text.split(" ", 1)[1]
    r = cursor.execute("SELECT content FROM notes WHERE chat_id=? AND name=?", (m.chat.id, name)).fetchone()
    await m.reply(r[0] if r else "❌ غير موجودة")

# ========= الاذاعة =========
async def broadcast(app, message):
    users = cursor.execute("SELECT id FROM users").fetchall()
    s = f = 0
    st = await message.reply(f"📢 بدأت الاذاعة لـ {len(users)}")
    for i, u in enumerate(users):
        try:
            if message.photo: await app.send_photo(u[0], message.photo.file_id, caption=message.caption)
            else: await app.send_message(u[0], message.text)
            s += 1
        except FloodWait as e: await asyncio.sleep(e.value)
        except: f += 1
        await asyncio.sleep(1.5)
        if (i+1)%50==0: await st.edit_text(f"تم: {i+1}/{len(users)}\n✅ {s}\n❌ {f}")
    await st.edit_text(f"✅ انتهت\nالاجمالي: {len(users)}\nوصل: {s}\nفشل: {f}")

# ========= الترحيب =========
@app.on_chat_member_updated()
async def welcome(_, u):
    if u.new_chat_member and u.old_chat_member.status == "left":
        if get_setting("welcome") == "1":
            await app.send_message(u.chat.id, f"مرحبا {u.new_chat_member.user.first_name} ❤️ نورت {u.chat.title}")

print("✅ TiaBot V4 Started")
if __name__ == "__main__":
    t = threading.Thread(target=run_flask); t.daemon=True; t.start()
    app.run()
