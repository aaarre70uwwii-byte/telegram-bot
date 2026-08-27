from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatPermissions, ChatMemberStatus
import os, json

app = Client("MyShieldBot")
OWNER_ID = int(os.getenv("OWNER_ID"))

DB_FILE = "data.json"
if not os.path.exists(DB_FILE):
    json.dump({"ranks":{"admin":[],"vip":[],"manager":[],"creator":[],"owner":[],"owner_basic":[]},"ban":[],"mute":[],"block":[]}, open(DB_FILE,"w"))
db = json.load(open(DB_FILE))

def save():
    with open(DB_FILE,"w") as f: json.dump(db, f)

def is_admin(user_id):
    return user_id == OWNER_ID or user_id in db["ranks"].get("admin", [])

# ========== عرض القائمة عند الضغط م1 ==========
@app.on_callback_query(filters.regex("menu_1"))
async def show_admin_menu(client, query: CallbackQuery):
    text = """**• أهلاً بك في عزيزي**
**- قائمة اوامر الادمنيه**
━━━━━━━━━━━━
**- اوامر الرفع والتنزيل :**
`رفع مالك اساسي` - `تنزيل مالك اساسي`
`رفع مالك` - `تنزيل مالك`
`رفع مشرف` - `تنزيل مشرف`
`رفع منشئ` - `تنزيل منشئ`
`رفع مدير` - `تنزيل مدير`
`رفع ادمن` - `تنزيل ادمن`
`رفع مميز` - `تنزيل مميز`
`تنزيل الكل`

**- اوامر المسح :**
`مسح الكل` `مسح + عدد` `مسح بالرد`
`مسح المنشئين` `مسح المدراء` `مسح المالكين`
`مسح الادمنيه` `مسح المميزين` `مسح المحظورين`
`مسح المكتومين` `مسح قائمه المنع`
`مسح الردود` `مسح الاوامر المضافه`
`مسح الايدي` `مسح الترحيب` `مسح الرابط`

**- اوامر الطرد والحظر :**
`تقييد + الوقت` `حظر` `طرد` `كتم` `تقييد`
`الغاء الحظر` `الغاء الكتم` `فك التقييد`
`رفع القيود` `منع بالرد` `الغاء منع بالرد`
`طرد البوتات` `طرد المحذوفين` `كشف البوتات`
━━━━━━━━━━━━"""
    await query.message.edit_text(text)
    await query.answer()

# ========== تنفيذ الاوامر ==========
@app.on_message(filters.group & filters.command(["رفع ادمن","تنزيل ادمن"]))
async def rank_admin(client, message: Message):
    if not is_admin(message.from_user.id): return await message.reply("❌ ليس لديك صلاحية")
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id # رقم مش نص
    if "رفع" in message.text:
        await client.promote_chat_member(message.chat.id, uid)
        if uid not in db["ranks"]["admin"]: db["ranks"]["admin"].append(uid)
        await message.reply("✅ تم رفع ادمن")
    else:
        await client.promote_chat_member(message.chat.id, uid, privileges=ChatMemberStatus.MEMBER)
        if uid in db["ranks"]["admin"]: db["ranks"]["admin"].remove(uid)
        await message.reply("❌ تم تنزيل ادمن")
    save()

@app.on_message(filters.group & filters.command(["رفع مميز","تنزيل مميز"]))
async def rank_vip(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    if "رفع" in message.text:
        if uid not in db["ranks"]["vip"]: db["ranks"]["vip"].append(uid)
    else:
        db["ranks"]["vip"].remove(uid) if uid in db["ranks"]["vip"] else None
    save(); await message.reply("✅ تم")

@app.on_message(filters.group & filters.command("تنزيل الكل"))
async def demote_all(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    for k in db["ranks"]:
        db["ranks"][k].remove(uid) if uid in db["ranks"][k] else None
    await client.promote_chat_member(message.chat.id, uid, privileges=ChatMemberStatus.MEMBER)
    save(); await message.reply("✅ تم تنزيل جميع الرتب")

@app.on_message(filters.group & filters.command("حظر"))
async def ban_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    await client.ban_chat_member(message.chat.id, uid)
    if uid not in db["ban"]: db["ban"].append(uid); save()
    await message.reply("⛔ تم الحظر")

@app.on_message(filters.group & filters.command("طرد"))
async def kick_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    await client.ban_chat_member(message.chat.id, uid)
    await client.unban_chat_member(message.chat.id, uid)
    await message.reply("👢 تم الطرد")

@app.on_message(filters.group & filters.command("كتم"))
async def mute_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    await client.restrict_chat_member(message.chat.id, uid, permissions=ChatPermissions())
    if uid not in db["mute"]: db["mute"].append(uid); save()
    await message.reply("🔇 تم الكتم")

@app.on_message(filters.group & filters.command("تقييد"))
async def restrict_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    await client.restrict_chat_member(message.chat.id, uid, permissions=ChatPermissions(can_send_messages=False))
    await message.reply("⛓️ تم التقييد")

@app.on_message(filters.group & filters.command(["الغاء الحظر","فك الحظر"]))
async def unban_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    await client.unban_chat_member(message.chat.id, uid)
    db["ban"].remove(uid) if uid in db["ban"] else None; save()
    await message.reply("✅ تم فك الحظر")

@app.on_message(filters.group & filters.command(["الغاء الكتم","فك الكتم"]))
async def unmute_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    await client.restrict_chat_member(message.chat.id, uid, permissions=ChatPermissions(can_send_messages=True))
    db["mute"].remove(uid) if uid in db["mute"] else None; save()
    await message.reply("🔊 تم فك الكتم")

@app.on_message(filters.group & filters.command("فك التقييد"))
async def unrestrict_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    await client.restrict_chat_member(message.chat.id, uid, permissions=ChatPermissions(can_send_messages=True))
    await message.reply("✅ تم فك التقييد")

@app.on_message(filters.group & filters.command("رفع القيود"))
async def lift_all(client, message: Message):
    if not is_admin(message.from_user.id): return
    await client.set_chat_permissions(message.chat.id, permissions=ChatPermissions(can_send_messages=True))
    await message.reply("✅ تم رفع جميع القيود")

@app.on_message(filters.group & filters.command("مسح"))
async def delete_cmd(client, message: Message):
    if not is_admin(message.from_user.id): return
    if len(message.command) > 1:
        count = int(message.command[1])
        await client.delete_messages(message.chat.id, list(range(message.id - count, message.id)))
        await message.delete()

@app.on_message(filters.group & filters.command("طرد البوتات"))
async def kick_bots(client, message: Message):
    if not is_admin(message.from_user.id): return
    c=0
    async for m in client.get_chat_members(message.chat.id):
        if m.user.is_bot: await client.ban_chat_member(message.chat.id, m.user.id); c+=1
    await message.reply(f"✅ تم طرد {c} بوت")

@app.on_message(filters.group & filters.command("كشف البوتات"))
async def show_bots(client, message: Message):
    if not is_admin(message.from_user.id): return
    bots=[]
    async for m in client.get_chat_members(message.chat.id):
        if m.user.is_bot: bots.append(f"• {m.user.first_name} - `{m.user.id}`")
    await message.reply("**البوتات:**\n" + "\n".join(bots) if bots else "مافي بوتات")
