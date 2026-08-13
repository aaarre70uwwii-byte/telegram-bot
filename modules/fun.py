from pyrogram import filters
from pyrogram.types import Message
from bot import app
from modules.utils import has_permission
from database import cursor, conn

fun_ranks = ["هطف", "بثر", "حمار", "كلب", "كلبه", "عتوي", "عتويه", "لحجي", "خروف"]

# ========== رفع وتنزيل رتب التسليه ==========
@app.on_message(filters.group & filters.text & filters.reply)
async def fun_ranks_handler(_, m: Message):
    chat_id = m.chat.id
    user_id = m.from_user.id
    text = m.text.strip()
    target_id = m.reply_to_message.from_user.id

    if not await has_permission(app, chat_id, user_id, "mod"): return

    if text.startswith("رفع "):
        rank = text.split("رفع ")[1]
        if rank in fun_ranks:
            cursor.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?)", (chat_id, target_id, rank)); conn.commit()
            await m.reply(f"✅ تم رفع {m.reply_to_message.from_user.first_name} {rank}")

    elif text.startswith("تنزيل "):
        rank = text.split("تنزيل ")[1]
        if rank in fun_ranks:
            cursor.execute("DELETE FROM fun_ranks WHERE chat_id=? AND user_id=? AND rank=?", (chat_id, target_id, rank)); conn.commit()
            await m.reply(f"✅ تم تنزيل {m.reply_to_message.from_user.first_name} من {rank}")

    elif text == "مسح رتب التسليه":
        cursor.execute("DELETE FROM fun_ranks WHERE chat_id=?", (chat_id,)); conn.commit()
        await m.reply("✅ تم مسح جميع رتب التسليه")

@app.on_message(filters.group & filters.text & filters.regex(r"^رتب التسليه$"))
async def show_fun_ranks(_, m: Message):
    cursor.execute("SELECT user_id, rank FROM fun_ranks WHERE chat_id=?", (m.chat.id,))
    data = cursor.fetchall()
    if not data: return await m.reply("لا يوجد رتب تسليه")
    txt = "📋 رتب التسليه:\n"
    for uid, rank in data: txt += f"- {rank} : `{uid}`\n"
    await m.reply(txt)

# ========== اوامر تسليه عامه ==========
@app.on_message(filters.group & filters.text)
async def fun_commands(_, m: Message):
    if m.text == "عمري":
        await m.reply(f"عمرك {m.from_user.id % 25 + 15} سنة 😂")
    elif m.text == "طولي":
        await m.reply(f"طولك {m.from_user.id % 50 + 150} سم")
    elif m.text == "وزني":
        await m.reply(f"وزنك {m.from_user.id % 40 + 50} كيلو")
    elif m.text == "تحبني":
        await m.reply("اكيد احبك ❤️")
    elif m.text == "تكرهني":
        await m.reply("مستحيل اكرهك 🥺")
