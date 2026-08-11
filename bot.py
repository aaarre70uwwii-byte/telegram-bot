import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except: data = {"devs": [7488375443], "admins": {}, "locks": {}} # انت المطور

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def is_admin(uid, cid):
    return uid in data["devs"] or uid in data["admins"].get(str(cid), [])

# ========== القائمة الرئيسية ==========
async def show_main_menu(u,c):
    keyboard = [
        [InlineKeyboardButton("1 الادمنيه", callback_data='m1'), InlineKeyboardButton("2 الاعدادات", callback_data='m2'), InlineKeyboardButton("3 القفل", callback_data='m3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """- أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
━━━━━━━━━━"""
    await u.message.reply_text(text, reply_markup=reply_markup)

# ========== م1 اوامر الادمنيه + تشتغل ==========
async def m1(u,c):
    text = """◂ م1 : اوامر الادمنيه
━━━━━━━━━━━━
رفع : `رفع ادمن` رد على العضو
تنزيل : `تنزيل ادمن` رد على العضو
حظر : `حظر` رد على العضو
طرد : `طرد` رد على العضو
كتم : `كتم` رد على العضو
فك كتم : `الغاء الكتم` رد على العضو
━━━━━━━━━━━━"""
    await u.message.reply_text(text)

# ========== م2 اوامر الاعدادات + تشتغل ==========
async def m2(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return await u.message.reply_text("للمشرفين فقط")
    cid = u.effective_chat.id
    text = f"""◂ م2 : اوامر الاعدادات
━━━━━━━━━━━━
`ايدي` : يطلع ايديك وايدي الجروب
`الرابط` : يجيب رابط الجروب
ايديك: `{u.effective_user.id}`
ايدي الجروب: `{cid}`
━━━━━━━━━━━━"""
    await u.message.reply_text(text, parse_mode='Markdown')

# ========== م3 اوامر القفل + تشتغل ==========
async def m3(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return await u.message.reply_text("للمشرفين فقط")
    text = """◂ م3 : اوامر القفل - الفتح
━━━━━━━━━━━━
`قفل الروابط` - `فتح الروابط`
`قفل الصور` - `فتح الصور`
`قفل الفيديو` - `فتح الفيديو`
`قفل الكل` - `فتح الكل`
━━━━━━━━━━━━"""
    await u.message.reply_text(text)

# ========== اوامر الرفع والتنزيل ==========
async def promote_admin(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return await u.message.reply_text("رد على الشخص")
    cid = str(u.effective_chat.id)
    uid = u.message.reply_to_message.from_user.id
    if cid not in data["admins"]: data["admins"][cid] = []
    if uid not in data["admins"][cid]:
        data["admins"][cid].append(uid)
        save()
    await u.message.reply_text(f"تم رفع {u.message.reply_to_message.from_user.first_name} ادمن ✅")

async def demote_admin(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    cid = str(u.effective_chat.id)
    uid = u.message.reply_to_message.from_user.id
    if cid in data["admins"] and uid in data["admins"][cid]:
        data["admins"][cid].remove(uid)
        save()
    await u.message.reply_text(f"تم تنزيل {u.message.reply_to_message.from_user.first_name} ✅")

# ========== اوامر الحظر والكتم ==========
async def ban(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    await c.bot.ban_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id)
    await u.message.reply_text(f"تم حظر {u.message.reply_to_message.from_user.first_name} ✅")

async def kick(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    uid = u.message.reply_to_message.from_user.id
    await c.bot.ban_chat_member(u.effective_chat.id, uid)
    await c.bot.unban_chat_member(u.effective_chat.id, uid)
    await u.message.reply_text(f"تم طرد {u.message.reply_to_message.from_user.first_name} ✅")

async def mute(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    await c.bot.restrict_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=False))
    await u.message.reply_text(f"تم كتم {u.message.reply_to_message.from_user.first_name} ✅")

async def unmute(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    await c.bot.restrict_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=True))
    await u.message.reply_text(f"تم فك الكتم ✅")

# ========== اوامر الاعدادات ==========
async def get_id(u,c):
    await u.message.reply_text(f"ايديك: `{u.effective_user.id}`\nايدي الجروب: `{u.effective_chat.id}`", parse_mode='Markdown')

async def get_link(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    link = await c.bot.export_chat_invite_link(u.effective_chat.id)
    await u.message.reply_text(f"رابط الجروب:\n{link}")

# ========== اوامر القفل ==========
async def lock_links(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    cid = str(u.effective_chat.id)
    if cid not in data["locks"]: data["locks"][cid] = {}
    data["locks"][cid]["links"] = True
    save()
    await u.message.reply_text("تم قفل الروابط ✅")

async def unlock_links(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    cid = str(u.effective_chat.id)
    if cid in data["locks"]: data["locks"][cid]["links"] = False
    save()
    await u.message.reply_text("تم فتح الروابط ✅")

# ========== منع الرسائل المقفلة ==========
async def check_locks(u,c):
    if not u.message: return
    cid = str(u.effective_chat.id)
    if cid in data["locks"]:
        if data["locks"][cid].get("links") and "http" in u.message.text:
            if not is_admin(u.effective_user.id, u.effective_chat.id):
                await u.message.delete()

# ========== الازرار ==========
async def button(u,c):
    query = u.callback_query
    await query.answer()
    if query.data == 'm1': await m1(query,c)
    elif query.data == 'm2': await m2(query,c)
    elif query.data == 'm3': await m3(query,c)

# ========== الرد التلقائي ==========
async def auto_reply(u,c):
    text = u.message.text
    await check_locks(u,c) # يفحص القفل قبل كل شي

    if text == "الاوامر":
        await show_main_menu(u,c)
    elif text == "رفع ادمن": await promote_admin(u,c)
    elif text == "تنزيل ادمن": await demote_admin(u,c)
    elif text == "حظر": await ban(u,c)
    elif text == "طرد": await kick(u,c)
    elif text == "كتم": await mute(u,c)
    elif text == "الغاء الكتم": await unmute(u,c)
    elif text == "ايدي": await get_id(u,c)
    elif text == "الرابط": await get_link(u,c)
    elif text == "قفل الروابط": await lock_links(u,c)
    elif text == "فتح الروابط": await unlock_links(u,c)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", show_main_menu))
    app.add_handler(CommandHandler("m1", m1))
    app.add_handler(CommandHandler("m2", m2))
    app.add_handler(CommandHandler("m3", m3))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT, auto_reply))
    print("Tia شغال")
    app.run_polling()

if __name__ == "__main__": main() 
import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"
DEV_ID = 7488375443 # ايديك

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except: data = {"devs": [DEV_ID], "admins": {}, "active_groups": [], "photo_enabled": True, "custom_cmds": {}, "waiting_add": {}}

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def is_dev(uid): return uid in data["devs"]
def is_admin(uid, cid): return uid in data["devs"] or uid in data["admins"].get(str(cid), [])
def is_active(cid): return str(cid) in data["active_groups"]

# ========== ارسال صورة المطور ==========
async def send_dev_info(u,c):
    mention = f"[{u.message.from_user.first_name}](tg://user?id={DEV_ID})"
    caption = f"""👑 **المطور الاساسي** 👑
━━━━━━━━━━
{mention}
الايدي: `{DEV_ID}`
━━━━━━━━━━"""

    if data.get("photo_enabled", True):
        try:
            photos = await c.bot.get_user_profile_photos(DEV_ID, limit=1)
            if photos.total_count > 0:
                await u.message.reply_photo(photo=photos.photos[0][0].file_id, caption=caption, parse_mode='Markdown')
                return
        except: pass
    await u.message.reply_text(caption, parse_mode='Markdown')

# ========== اضافة امر جديد ==========
async def add_command_start(u,c):
    if not is_dev(u.effective_user.id): return
    data["waiting_add"][str(u.effective_user.id)] = True
    save()
    await u.message.reply_text("📝 ارسل الامر والرد بهذا الشكل:\n`الامر | الرد`\n\nمثال: `باي | مع السلامة`", parse_mode='Markdown')

async def save_custom_command(u,c, text):
    if "|" not in text:
        return await u.message.reply_text("❌ الصيغة غلط. لازم `الامر | الرد`")
    cmd, reply = text.split("|", 1)
    cmd = cmd.strip().lower()
    reply = reply.strip()
    data["custom_cmds"][cmd] = reply
    data["waiting_add"].pop(str(u.effective_user.id), None)
    save()
    await u.message.reply_text(f"✅ تم اضافة الامر `{cmd}`\nالرد: {reply}", parse_mode='Markdown')

# ========== اوامر الرفع والتنزيل ==========
async def promote_admin(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return await u.message.reply_text("رد على الشخص")
    cid = str(u.effective_chat.id); uid = u.message.reply_to_message.from_user.id
    if cid not in data["admins"]: data["admins"][cid] = []
    if uid not in data["admins"][cid]:
        data["admins"][cid].append(uid); save()
        await u.message.reply_text(f"✅ تم رفع {u.message.reply_to_message.from_user.first_name} ادمن")

async def demote_admin(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    cid = str(u.effective_chat.id); uid = u.message.reply_to_message.from_user.id
    if cid in data["admins"] and uid in data["admins"][cid]:
        data["admins"][cid].remove(uid); save()
        await u.message.reply_text(f"✅ تم تنزيل {u.message.reply_to_message.from_user.first_name}")

# ========== تفعيل وتعطيل الصورة ==========
async def enable_photo(u,c):
    if not is_dev(u.effective_user.id): return
    data["photo_enabled"] = True; save()
    await u.message.reply_text("✅ تم تفعيل الايدي بالصورة")

async def disable_photo(u,c):
    if not is_dev(u.effective_user.id): return
    data["photo_enabled"] = False; save()
    await u.message.reply_text("❌ تم تعطيل الايدي بالصورة")

# ========== الرد التلقائي ==========
async def auto_reply(u,c):
    if not u.message: return
    uid = str(u.effective_user.id)
    text = u.message.text
    cid = str(u.effective_chat.id)

    if not is_active(cid) and u.effective_user.id!= DEV_ID and text!= "تفعيل":
        return

    # لو المطور قاعد يضيف امر
    if data["waiting_add"].get(uid):
        return await save_custom_command(u,c, text)

    # الاوامر الاساسية
    if text == "اضف امر": return await add_command_start(u,c)
    if text == "رفع ادمن": return await promote_admin(u,c)
    if text == "تنزيل ادمن": return await demote_admin(u,c)
    if text == "تفعيل
