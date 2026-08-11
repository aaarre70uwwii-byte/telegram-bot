import os
import json
from telegram import ChatPermissions
from telegram.ext import ApplicationBuilder, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"
DEV_ID = 7488375443

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except: data = {"devs": [DEV_ID], "admins": {}, "active_groups": [], "photo_enabled": True, "custom_cmds": {}, "waiting_add": {}, "locks": {}}

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def is_dev(uid): return uid in data["devs"]
def is_admin(uid, cid): return uid in data["devs"] or uid in data["admins"].get(str(cid), [])
def is_active(cid): return str(cid) in data["active_groups"]

# ========== الحماية ==========
async def check_locks(u,c):
    cid = str(u.effective_chat.id)
    if not data["locks"].get(cid): return False
    msg = u.message
    lock = data["locks"][cid]

    if lock.get("links") and msg.text and ("http" in msg.text or "t.me" in msg.text):
        await msg.delete(); return True
    if lock.get("photos") and msg.photo:
        await msg.delete(); return True
    if lock.get("videos") and msg.video:
        await msg.delete(); return True
    return False

# ========== اوامر المطور ==========
async def send_dev_info(u,c):
    mention = f"[{u.message.from_user.first_name}](tg://user?id={DEV_ID})"
    caption = f"👑 **المطور الاساسي** 👑\n━━━━━━━━━━\n{mention}\nالايدي: `{DEV_ID}`\n━━━━━━━━━━"
    if data.get("photo_enabled", True):
        try:
            photos = await c.bot.get_user_profile_photos(DEV_ID, limit=1)
            if photos.total_count > 0:
                await u.message.reply_photo(photo=photos.photos[0][0].file_id, caption=caption, parse_mode='Markdown'); return
        except: pass
    await u.message.reply_text(caption, parse_mode='Markdown')

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

# ========== اوامر الحماية ==========
async def lock_cmd(u,c, lock_type):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    cid = str(u.effective_chat.id)
    if cid not in data["locks"]: data["locks"][cid] = {}
    data["locks"][cid][lock_type] = True; save()
    await u.message.reply_text(f"✅ تم قفل {lock_type}")

async def unlock_cmd(u,c, lock_type):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    cid = str(u.effective_chat.id)
    if cid in data["locks"]: data["locks"][cid][lock_type] = False; save()
    await u.message.reply_text(f"✅ تم فتح {lock_type}")

# ========== اضافة امر ==========
async def add_command_start(u,c):
    if not is_dev(u.effective_user.id): return
    data["waiting_add"][str(u.effective_user.id)] = True; save()
    await u.message.reply_text("📝 ارسل: `الامر | الرد`", parse_mode='Markdown')

async def save_custom_command(u,c, text):
    if "|" not in text: return await u.message.reply_text("❌ الصيغة: `الامر | الرد`")
    cmd, reply = text.split("|", 1)
    data["custom_cmds"][cmd.strip().lower()] = reply.strip()
    data["waiting_add"].pop(str(u.effective_user.id), None); save()
    await u.message.reply_text(f"✅ تم اضافة الامر `{cmd.strip()}`")

# ========== الرد التلقائي ==========
async def auto_reply(u,c):
    if not u.message: return
    uid = str(u.effective_user.id); text = u.message.text; cid = str(u.effective_chat.id)

    if not is_active(cid) and u.effective_user.id!= DEV_ID and text!= "تفعيل": return
    if await check_locks(u,c): return

    if data["waiting_add"].get(uid): return await save_custom_command(u,c, text)

    # اوامر اساسية
    if text == "اضف امر": return await add_command_start(u,c)
    if text == "رفع ادمن": return await promote_admin(u,c)
    if text == "تنزيل ادمن": return await demote_admin(u,c)

    # الحماية
    if text == "قفل الروابط": return await lock_cmd(u,c,"links")
    if text == "فتح الروابط": return await unlock_cmd(u,c,"links")
    if text == "قفل الصور": return await lock_cmd(u,c,"photos")
    if text == "فتح الصور": return await unlock_cmd(u,c,"photos")

    # الايدي
    if text == "تفعيل الايدي بالصوره":
        if not is_dev(u.effective_user.id): return
        data["photo_enabled"] = True; save()
        return await u.message.reply_text("✅ تم تفعيل الايدي بالصورة")
    if text == "تعطيل الايدي بالصوره":
        if not is_dev(u.effective_user.id): return
        data["photo_enabled"] = False; save()
        return await u.message.reply_text("❌ تم تعطيل الايدي بالصورة")

    if "المطور" in text: return await send_dev_info(u,c)

    if text == "تفعيل":
        if not is_admin(u.effective_user.id, cid): return
        if cid not in data["active_groups"]: data["active_groups"].append(cid); save()
        return await u.message.reply_text("✅ تم تفعيل المجموعة")
    if text == "تعطيل":
        if not is_admin(u.effective_user.id, cid): return
        if cid in data["active_groups"]: data["active_groups"].remove(cid); save()
        return await u.message.reply_text("❌ تم تعطيل المجموعة")

    if text.lower() in data["custom_cmds"]:
        return await u.message.reply_text(data["custom_cmds"][text.lower()])

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, auto_reply))
    print("Tia شغال - كامل")
    app.run_polling()

if __name__ == "__main__": main()
