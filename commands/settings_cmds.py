from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import os, json

app = Client("MyShieldBot")
OWNER_ID = int(os.getenv("OWNER_ID"))

try:
    import yt_dlp
except:
    yt_dlp = None

DB_FILE = "data.json"
if not os.path.exists(DB_FILE):
    json.dump({
        "ranks":{"admin":[],"vip":[],"manager":[],"creator":[],"owner":[],"owner_basic":[]},
        "settings":{},
        "channels":[],
        "ban":[],"mute":[],"block":[],
        "commands":{}, "welcome":"", "id_template":"", "rules":""
    }, open(DB_FILE,"w", encoding="utf-8"))

with open(DB_FILE,"r", encoding="utf-8") as f: db = json.load(f)

def save():
    with open(DB_FILE,"w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

def is_admin(user_id):
    return user_id == OWNER_ID or user_id in db["ranks"].get("admin", [])

# ========== عرض قائمة م2 ==========
@app.on_callback_query(filters.regex("menu_2"))
async def show_settings_menu(client, query: CallbackQuery):
    text = """**- اهلا بك في قائمة اوامر الاعدادات :**
━━━━━━━━━━━━

**- اوامر رؤية الاعدادات :**
`الرابط` `المالكين` `المالكين الاساسين`
`المنشئين` `الادمنيه` `المدراء` `المميزين`
`المحظورين` `المكتومين` `القوانين`
`معلوماتي` `الحمايه` `الاعدادت` `المجموعه`

**- اوامر وضع الاعدادات :**
`اضف رابط` `مسح الرابط` `انشاء رابط`
`ضع الترحيب` `ضع قوانين` `ضع رابط`
`اضف امر` `تعيين الايدي`
`اضف قناه` `حذف قناه`

**- اوامر التحميل**
`تفعيل التحميل` `تعطيل التحميل`
`بحث + اسم الاغنيه` - لليوتيوب
`تيك + الرابط` - للتيك توك
`ساوند + الرابط` - للساوند
━━━━━━━━━━━━"""
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ رجوع", callback_data="back_menu")]])
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

# ========== اوامر الرؤية ==========
@app.on_message(filters.group & filters.command("الرابط"))
async def get_link(client, message: Message):
    if not is_admin(message.from_user.id): return
    link = db["settings"].get(str(message.chat.id), {}).get("link", "لا يوجد رابط محفوظ")
    await message.reply(f"**الرابط:**\n{link}")

@app.on_message(filters.group & filters.command(["المالكين","المالكين الاساسين","المنشئين","الادمنيه","المدراء","المميزين"]))
async def list_ranks(client, message: Message):
    if not is_admin(message.from_user.id): return
    keys = {"المالكين":"owner","المالكين الاساسين":"owner_basic","المنشئين":"creator","الادمنيه":"admin","المدراء":"manager","المميزين":"vip"}
    key = keys[message.command[0]]
    users = db["ranks"].get(key, [])
    await message.reply(f"**{message.command[0]}:**\n" + "\n".join([f"• `{u}`" for u in users]) if users else "فاضي")

@app.on_message(filters.group & filters.command(["المحظورين","المكتومين"]))
async def list_block(client, message: Message):
    if not is_admin(message.from_user.id): return
    key = "ban" if message.command[0]=="المحظورين" else "mute"
    users = db.get(key, [])
    await message.reply(f"**{message.command[0]}:**\n" + "\n".join([f"• `{u}`" for u in users]) if users else "مافي")

@app.on_message(filters.group & filters.command("القوانين"))
async def get_rules(client, message: Message):
    rules = db["settings"].get(str(message.chat.id), {}).get("rules", "لا توجد قوانين")
    await message.reply(f"**القوانين:**\n{rules}")

@app.on_message(filters.group & filters.command("معلوماتي"))
async def my_info(client, message: Message):
    user = message.from_user
    await message.reply(f"**اسمك:** {user.first_name}\n**ايديك:** `{user.id}`\n**يوزرك:** @{user.username}")

@app.on_message(filters.group & filters.command("الحمايه"))
async def protection(client, message: Message):
    await message.reply("**الحماية:**\nقفل الروابط: معطل\nقفل الكلايش: معطل\nقفل التكرار: معطل")

@app.on_message(filters.group & filters.command("الاعدادت"))
async def show_settings(client, message: Message):
    s = db["settings"].get(str(message.chat.id), {})
    await message.reply(f"**الاعدادات:**\nالرابط: {'موجود' if s.get('link') else 'مافي'}\nالترحيب: {'موجود' if s.get('welcome') else 'مافي'}")

@app.on_message(filters.group & filters.command("المجموعه"))
async def chat_info(client, message: Message):
    chat = await client.get_chat(message.chat.id)
    await message.reply(f"**المجموعة:** {chat.title}\n**الاعضاء:** {chat.members_count}\n**الايدي:** `{chat.id}`")

# ========== اوامر الوضع ==========
@app.on_message(filters.group & filters.command("انشاء رابط"))
async def create_link(client, message: Message):
    if not is_admin(message.from_user.id): return
    link = await client.export_chat_invite_link(message.chat.id)
    db["settings"].setdefault(str(message.chat.id), {})["link"] = link; save()
    await message.reply(f"✅ تم انشاء الرابط:\n{link}")

@app.on_message(filters.group & filters.command(["اضف رابط","ضع رابط"]))
async def set_link(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الرابط")
    link = message.reply_to_message.text
    db["settings"].setdefault(str(message.chat.id), {})["link"] = link; save()
    await message.reply("✅ تم حفظ الرابط")

@app.on_message(filters.group & filters.command("مسح الرابط"))
async def del_link(client, message: Message):
    if not is_admin(message.from_user.id): return
    db["settings"].setdefault(str(message.chat.id), {})["link"] = ""; save()
    await message.reply("✅ تم مسح الرابط")

@app.on_message(filters.group & filters.command("ضع الترحيب"))
async def set_welcome(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الترحيب")
    db["settings"].setdefault(str(message.chat.id), {})["welcome"] = message.reply_to_message.text; save()
    await message.reply("✅ تم وضع الترحيب")

@app.on_message(filters.group & filters.command("ضع قوانين"))
async def set_rules(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على القوانين")
    db["settings"].setdefault(str(message.chat.id), {})["rules"] = message.reply_to_message.text; save()
    await message.reply("✅ تم وضع القوانين")

@app.on_message(filters.group & filters.command("اضف امر"))
async def add_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الامر والرد")
    parts = message.reply_to_message.text.split("|")
    if len(parts)!= 2: return await message.reply("❌ الصيغة: الامر | الرد")
    db["commands"][parts[0]] = parts[1]; save()
    await message.reply(f"✅ تم اضافة امر `{parts[0]}`")

@app.on_message(filters.group & filters.command("تعيين الايدي"))
async def set_id(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على قالب الايدي")
    db["settings"].setdefault(str(message.chat.id), {})["id_template"] = message.reply_to_message.text; save()
    await message.reply("✅ تم تعيين قالب الايدي")

@app.on_message(filters.group & filters.command(["اضف قناه","حذف قناه"]))
async def channel_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if len(message.command) < 2: return await message.reply("❌ الاستخدام: اضف قناه @username")
    channel = message.command[1]
    if "اضف" in message.text:
        if channel not in db["channels"]: db["channels"].append(channel)
        await message.reply(f"✅ تم اضافة {channel}")
    else:
        db["channels"].remove(channel) if channel in db["channels"] else None
        await message.reply(f"✅ تم حذف {channel}")
    save()

# ========== اوامر التحميل ==========
download_status = {}

@app.on_message(filters.group & filters.command(["تفعيل التحميل","تعطيل التحميل"]))
async def toggle_download(client, message: Message):
    if not is_admin(message.from_user.id): return
    download_status[str(message.chat.id)] = "تفعيل" in message.text
    await message.reply("✅ تم تفعيل التحميل" if download_status[str(message.chat.id)] else "❌ تم تعطيل التحميل")

@app.on_message(filters.group & filters.command("بحث"))
async def search_yt(client, message: Message):
    if not download_status.get(str(message.chat.id), False): return await message.reply("❌ فعل التحميل اول")
    if not yt_dlp: return await message.reply("❌ نزل: pip install yt-dlp")
    if len(message.command) < 2: return await message.reply("❌ بحث + اسم")
    msg = await message.reply("⏳ جاري البحث...")
    try:
        with yt_dlp.YoutubeDL({'quiet':True}) as ydl:
            info = ydl.extract_info(f"ytsearch:{' '.join(message.command[1:])}", download=False)['entries'][0]
        await msg.edit(f"**{info['title']}**\n{info['webpage_url']}")
    except: await msg.edit("❌ فشل البحث")

@app.on_message(filters.group & filters.command("تيك"))
async def tiktok_dl(client, message: Message):
    if not download_status.get(str(message.chat.id), False): return
    await message.reply("⏳ قريبا: تحميل التيك توك")

@app.on_message(filters.group & filters.command("ساوند"))
async def soundcloud_dl(client, message: Message):
    if not download_status.get(str(message.chat.id), False): return
    await message.reply("⏳ قريبا: تحميل الساوند")
