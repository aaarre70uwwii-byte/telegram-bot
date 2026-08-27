from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import os, json, random

app = Client("MyShieldBot")
OWNER_ID = int(os.getenv("OWNER_ID"))

DB_FILE = "data.json"
with open(DB_FILE,"r", encoding="utf-8") as f: db = json.load(f)

def save():
    with open(DB_FILE,"w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

def is_admin(user_id):
    return user_id == OWNER_ID or user_id in db["ranks"].get("admin", [])

def get_settings(chat_id):
    return db["settings"].setdefault(str(chat_id), {})

def get_fun(chat_id):
    return get_settings(chat_id).setdefault("fun", {"ranks":{},"global_ranks":{},"votes":{},"married":{}})

# ========== عرض قائمة م4 ==========
@app.on_callback_query(filters.regex("menu_4"))
async def show_fun_menu(client, query: CallbackQuery):
    text = """**• اهلا بك عزي**
**- اوامر التسليه :**
━━━━━━━━━━━━
**- اوامر تسلية تظهر بالايدي :**

`رفع هطف` `تنزيل هطف`
`رفع بثر` `تنزيل بثر`
`رفع حمار` `تنزيل حمار`
`رفع كلب` `تنزيل كلب`
`رفع كلبه` `تنزيل كلبه`
`رفع عتوي` `تنزيل عتوي`
`رفع عتويه` `تنزيل عتويه`
`رفع لحجي` `تنزيل لحجي`
`رفع لحجيه` `تنزيل لحجيه`
`رفع خروف` `تنزيل خروف`
`رفع خفيفه` `تنزيل خفيفه`
`رفع خفيف` `تنزيل خفيف`
`رفع بقلبي` `تنزيل من قلبي`

**- للقروب:**
`رفع` `مسح رتب التسليه` `رتب التسليه`

**- للعام:**
`رفع عام` `رتب التسليه عام` `مسح رتب التسليه عام`

**- الزواج:**
`طلاق` `زواج` `زوجي` `زوجتي` `تتزوجني`

**- التصويت:**
`اكتموه` `تفعيل اكتموه` `تعطيل اكتموه`
`تفعيل زوجني` `تعطيل زوجني`
━━━━━━━━━━━━"""
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ رجوع", callback_data="back_menu")]])
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

# ========== قاموس الرتب كامل ==========
ranks_map = {
    "هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب",
    "كلبه": "الكلبات", "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج",
    "لحجيه": "اللحجيات", "خروف": "الخرفان", "خفيفه": "الخفيفات", "خفيف": "الخفيفين"
}

# ========== رفع وتنزيل رتب ==========
for rank in ranks_map.keys():
    @app.on_message(filters.group & filters.command([f"رفع {rank}", f"تنزيل {rank}"]))
    async def rank_handler(client, message: Message, r=rank):
        if not get_settings(message.chat.id).get("feature_التسليه", True): return
        if not is_admin(message.from_user.id): return
        if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
        uid = str(message.reply_to_message.from_user.id)
        fun = get_fun(message.chat.id)
        name = message.reply_to_message.from_user.first_name

        if "رفع" in message.text:
            fun["ranks"][uid] = r
            await message.reply(f"✅ تم رفع {name} الى رتبة {ranks_map[r]}")
        else:
            fun["ranks"].pop(uid, None)
            await message.reply(f"✅ تم تنزيل {name} من رتبة {ranks_map[r]}")
        save()

@app.on_message(filters.group & filters.command("رفع بقلبي"))
async def raise_heart(client, message: Message):
    if not get_settings(message.chat.id).get("feature_التسليه", True): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = str(message.reply_to_message.from_user.id)
    get_fun(message.chat.id)["ranks"][uid] = "قلبي"
    save()
    await message.reply(f"❤️ تم رفع {message.reply_to_message.from_user.first_name} بقلبك")

@app.on_message(filters.group & filters.command("تنزيل من قلبي"))
async def down_heart(client, message: Message):
    if not get_settings(message.chat.id).get("feature_التسليه", True): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = str(message.reply_to_message.from_user.id)
    fun = get_fun(message.chat.id)
    if fun["ranks"].get(uid) == "قلبي": fun["ranks"].pop(uid)
    save()
    await message.reply(f"💔 تم تنزيل {message.reply_to_message.from_user.first_name} من قلبك")

# ========== رفع باسم اختياري للقروب ==========
@app.on_message(filters.group & filters.command("رفع"))
async def raise_custom(client, message: Message):
    if not get_settings(message.chat.id).get("feature_التسليه", True): return
    if not is_admin(message.from_user.id): return
    if len(message.command) < 2: return await message.reply("❌ الاستخدام: رفع اسم الرتبة")
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    rank_name = " ".join(message.command[1:])
    uid = str(message.reply_to_message.from_user.id)
    get_fun(message.chat.id)["ranks"][uid] = rank_name
    save()
    await message.reply(f"✅ تم رفع {message.reply_to_message.from_user.first_name} الى {rank_name}")

@app.on_message(filters.group & filters.command("رتب التسليه"))
async def show_ranks(client, message: Message):
    ranks = get_fun(message.chat.id)["ranks"]
    if not ranks: return await message.reply("مافي رتب تسليه")
    text = "**رتب التسليه:**\n"
    for uid, rank in ranks.items(): text += f"• {rank} - `{uid}`\n"
    await message.reply(text)

@app.on_message(filters.group & filters.command("مسح رتب التسليه"))
async def clear_ranks(client, message: Message):
    if not is_admin(message.from_user.id): return
    get_fun(message.chat.id)["ranks"] = {}; save()
    await message.reply("✅ تم مسح رتب التسليه")

# ========== رتب التسليه العام ==========
@app.on_message(filters.group & filters.command("رفع عام"))
async def raise_global(client, message: Message):
    if not get_settings(message.chat.id).get("feature_التسليه", True): return
    if not is_admin(message.from_user.id): return
    if len(message.command) < 2: return await message.reply("❌ الاستخدام: رفع عام اسم الرتبة")
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    rank_name = " ".join(message.command[1:])
    uid = str(message.reply_to_message.from_user.id)
    get_fun(message.chat.id)["global_ranks"][uid] = rank_name
    save()
    await message.reply(f"✅ تم رفع {message.reply_to_message.from_user.first_name} عام الى {rank_name}")

@app.on_message(filters.group & filters.command("رتب التسليه عام"))
async def show_global(client, message: Message):
    ranks = get_fun(message.chat.id)["global_ranks"]
    if not ranks: return await message.reply("مافي رتب عام")
    text = "**رتب التسليه العام:**\n"
    for uid, rank in ranks.items(): text += f"• {rank} - `{uid}`\n"
    await message.reply(text)

@app.on_message(filters.group & filters.command("مسح رتب التسليه عام"))
async def clear_global(client, message: Message):
    if not is_admin(message.from_user.id): return
    get_fun(message.chat.id)["global_ranks"] = {}; save()
    await message.reply("✅ تم مسح رتب التسليه العام")

# ========== الزواج والطلاق ==========
@app.on_message(filters.group & filters.command(["تفعيل زوجني","تعطيل زوجني"]))
async def toggle_marry(client, message: Message):
    if not is_admin(message.from_user.id): return
    s = get_settings(message.chat.id)
    s["feature_زوجني"] = "تفعيل" in message.text; save()
    await message.reply("✅ تم تفعيل الزواج" if s["feature_زوجني"] else "❌ تم تعطيل الزواج")

@app.on_message(filters.group & filters.command("زواج"))
async def marry(client, message: Message):
    if not get_settings(message.chat.id).get("feature_زوجني", True): return await message.reply("❌ امر الزواج معطل")
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    a, b = str(message.from_user.id), str(message.reply_to_message.from_user.id)
    get_fun(message.chat.id)["married"][a] = b
    save()
    await message.reply(f"💍 مبروك {message.from_user.first_name} و {message.reply_to_message.from_user.first_name} تزوجتو")

@app.on_message(filters.group & filters.command("طلاق"))
async def divorce(client, message: Message):
    married = get_fun(message.chat.id)["married"]
    if str(message.from_user.id) in married:
        married.pop(str(message.from_user.id)); save()
        await message.reply("💔 تم الطلاق")
    else: await message.reply("❌ انت مش متزوج")

@app.on_message(filters.group & filters.command(["زوجي","زوجتي"]))
async def my_spouse(client, message: Message):
    spouse = get_fun(message.chat.id)["married"].get(str(message.from_user.id))
    if spouse: await message.reply(f"❤️ زوجك/زوجتك: `{spouse}`")
    else: await message.reply("❌ انت مش متزوج")

@app.on_message(filters.group & filters.command("تتزوجني"))
async def propose(client, message: Message):
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    await message.reply(f"💍 {message.reply_to_message.from_user.first_name} تتزوجني؟")

# ========== التصويت اكتموه ==========
@app.on_message(filters.group & filters.command(["تفعيل اكتموه","تعطيل اكتموه"]))
async def toggle_vote(client, message: Message):
    if not is_admin(message.from_user.id): return
    s = get_settings(message.chat.id)
    s["feature_اكتموه"] = "تفعيل" in message.text; save()
    await message.reply("✅ تم تفعيل اكتموه" if s["feature_اكتموه"] else "❌ تم تعطيل اكتموه")

@app.on_message(filters.group & filters.command("اكتموه"))
async def mute_vote(client, message: Message):
    if not get_settings(message.chat.id).get("feature_اكتموه", True): return await message.reply("❌ امر اكتموه معطل")
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    chat_id = str(message.chat.id); target = str(message.reply_to_message.from_user.id)
    votes = get_fun(chat_id)["votes"].setdefault(target, [])
    if message.from_user.id not in votes: votes.append(message.from_user.id)
    if len(votes) >= 3:
        await client.restrict_chat_member(message.chat.id, int(target), ChatPermissions(can_send_messages=False))
        await message.reply(f"🔇 تم كتم {message.reply_to_message.from_user.first_name} بالتصويت")
        votes.clear()
    else: await message.reply(f"تصويت اكتموه: {len(votes)}/3")
