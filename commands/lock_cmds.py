from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import os, json, re

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

# ========== عرض قائمة م3 ==========
@app.on_callback_query(filters.regex("menu_3"))
async def show_lock_menu(client, query: CallbackQuery):
    text = """**- اهلا بك في قائمة القفل - التعطيل :**
**- اوامر القفل والفتح :**
━━━━━━━━━━━━ 
`قفل جمثون` `قفل السب` `قفل الايرانيه` `قفل الكتابه`
`قفل الاباحي` `قفل تعديل الميديا` `قفل التعديل` `قفل الفيديو`
`قفل الصور` `قفل الملصقات` `قفل المتحركه` `قفل الدردشه`
`قفل الروابط` `قفل التاك` `قفل البوتات` `قفل المعرفات`
`قفل البوتات بالطرد` `قفل الكلايش` `قفل التكرار` `قفل التوجيه`
`قفل الانلاين` `قفل الجهات` `قفل الكل` `قفل الدخول`
`قفل الصوت` `قفل التوجيه بالتقييد` `قفل الروابط بالتقييد`
`قفل المتحركه بالتقييد` `قفل الصور بالتقييد` `قفل الفيديو بالتقييد`
━━━━━━━━━━━━
**- اوامر التفعيل - التعطيل :**
`تفعيل ضافني` `تفعيل الاذكار` `تفعيل الثنائي` `تفعيل افتاري`
`تفعيل التسليه` `تفعيل الكت` `تفعيل الترحيب` `تفعيل الردود`
`تفعيل الانذار` `تفعيل التحذير` `تفعيل الايدي` `تفعيل الرابط`
`تفعيل اطردني` `تفعيل الحظر` `تفعيل الرفع` `تفعيل التنزيل`
`تفعيل التحويل` `تفعيل الحمايه` `تفعيل المنشن` `تفعيل الاقتباسات`
`تفعيل الخدميه` `تفعيل اليوتيوب` `تفعيل الايدي بالصوره` `تفعيل التحقق`
`تفعيل ردود السورس`
━━━━━━━━━━━━"""
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ رجوع", callback_data="back_menu")]])
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

# ========== اوامر القفل الاساسية ==========
lock_commands = {
    "جمثون": "gmthon", "السب": "insult", "الايرانيه": "persian", "الكتابه": "text",
    "الاباحي": "porn", "تعديل الميديا": "edit_media", "التعديل": "edit", "الفيديو": "video",
    "الصور": "photo", "الملصقات": "sticker", "المتحركه": "gif", "الدردشه": "chat",
    "الروابط": "link", "التاك": "tag", "البوتات": "bots", "المعرفات": "username",
    "الكلايش": "spam", "التكرار": "flood", "التوجيه": "forward", "الانلاين": "inline",
    "الجهات": "contact", "الدخول": "join", "الصوت": "voice"
}

for cmd, key in lock_commands.items():
    @app.on_message(filters.group & filters.command([f"قفل {cmd}", f"فتح {cmd}"]))
    async def lock_handler(client, message: Message, k=key, c=cmd):
        if not is_admin(message.from_user.id): return
        s = get_settings(message.chat.id)
        s[f"lock_{k}"] = "قفل" in message.text
        save()
        await message.reply(f"✅ تم {'قفل' if s[f'lock_{k}'] else 'فتح'} {c}")

# ========== اوامر القفل بالتقييد ==========
restrict_commands = {
    "التوجيه بالتقييد": "forward_restrict", "الروابط بالتقييد": "link_restrict",
    "المتحركه بالتقييد": "gif_restrict", "الصور بالتقييد": "photo_restrict",
    "الفيديو بالتقييد": "video_restrict"
}

for cmd, key in restrict_commands.items():
    @app.on_message(filters.group & filters.command([f"قفل {cmd}", f"فتح {cmd}"]))
    async def restrict_handler(client, message: Message, k=key, c=cmd):
        if not is_admin(message.from_user.id): return
        s = get_settings(message.chat.id)
        s[f"lock_{k}"] = "قفل" in message.text
        save()
        await message.reply(f"✅ تم {'تقييد' if s[f'lock_{k}'] else 'فتح'} {c}")

@app.on_message(filters.group & filters.command(["قفل البوتات بالطرد","فتح البوتات بالطرد"]))
async def lock_bots_kick(client, message: Message):
    if not is_admin(message.from_user.id): return
    s = get_settings(message.chat.id)
    s["lock_bots_kick"] = "قفل" in message.text
    save()
    await message.reply("✅ تم تفعيل طرد البوتات" if s["lock_bots_kick"] else "✅ تم تعطيل طرد البوتات")

@app.on_message(filters.group & filters.command(["قفل الكل","فتح الكل"]))
async def lock_all(client, message: Message):
    if not is_admin(message.from_user.id): return
    if "قفل" in message.text:
        await client.set_chat_permissions(message.chat.id, ChatPermissions())
        await message.reply("🔒 تم قفل الكل")
    else:
        await client.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
        await message.reply("🔓 تم فتح الكل")

# ========== اوامر التفعيل والتعطيل ==========
features = [
    "ضافني", "الاذكار", "الثنائي", "افتاري", "التسليه", "الكت", "الترحيب", "الردود",
    "الانذار", "التحذير", "الايدي", "الرابط", "اطردني", "الحظر", "الرفع", "التنزيل",
    "التحويل", "الحمايه", "المنشن", "الاقتباسات", "الخدميه", "اليوتيوب", "الايدي بالصوره", "التحقق", "ردود السورس"
]

for feat in features:
    @app.on_message(filters.group & filters.command([f"تفعيل {feat}", f"تعطيل {feat}"]))
    async def feature_handler(client, message: Message, f=feat):
        if not is_admin(message.from_user.id): return
        s = get_settings(message.chat.id)
        s[f"feature_{f}"] = "تفعيل" in message.text
        save()
        await message.reply(f"✅ تم {'تفعيل' if s[f'feature_{f}'] else 'تعطيل'} {f}")
