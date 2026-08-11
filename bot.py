import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"
DEV_ID = 7488375443 # ايديك

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except: data = {"devs": [DEV_ID], "admins": {}, "active_groups": [], "photo_enabled": True}

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

# ========== اوامر الرفع والتنزيل ==========
async def promote_admin(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return await u.message.reply_text("❌ انت مش ادمن")
    if not u.message.reply_to_message: return await u.message.reply_text("رد على الشخص اللي تريد ترفعه")
    cid = str(u.effective_chat.id); uid = u.message.reply_to_message.from_user.id
    if cid not in data["admins"]: data["admins"][cid] = []
    if uid not in data["admins"][cid]:
        data["admins"][cid].append(uid); save()
        await u.message.reply_text(f"✅ تم رفع {u.message.reply_to_message.from_user.first_name} ادمن")
    else:
        await u.message.reply_text("هو ادمن اصلا")

async def demote_admin(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return await u.message.reply_text("رد على الشخص")
    cid = str(u.effective_chat.id); uid = u.message.reply_to_message.from_user.id
    if cid in data["admins"] and uid in data["admins"][cid]:
        data["admins"][cid].remove(uid); save()
        await u.message.reply_text(f"✅ تم تنزيل {u.message.reply_to_message.from_user.first_name}")
    else:
        await u.message.reply_text("هو مش ادمن")

# ========== تفعيل وتعطيل الصورة ==========
async def enable_photo(u,c):
    if not is_dev(u.effective_user.id): return
    data["photo_enabled"] = True; save()
    await u.message.reply_text("✅ تم تفعيل الايدي بالصورة")

async def disable_photo(u,c):
    if not is_dev(u.effective_user.id): return
    data["photo_enabled"] = False; save()
    await u.message.reply_text("❌ تم تعطيل الايدي بالصورة")

# ========== تفعيل وتعطيل الجروب ==========
async def activate(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    cid = str(u.effective_chat.id)
    if cid not in data["active_groups"]: data["active_groups"].append(cid); save()
    await u.message.reply_text("✅ تم تفعيل المجموعة")

async def deactivate(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    cid = str(u.effective_chat.id)
    if cid in data["active_groups"]: data["active_groups"].remove(cid); save()
    await u.message.reply_text("❌ تم تعطيل المجموعة")

# ========== الرد التلقائي ==========
async def auto_reply(u,c):
    if not u.message: return
    text = u.message.text

    cid = str(u.effective_chat.id)
    if not is_active(cid) and u.effective_user.id!= DEV_ID and text!= "تفعيل":
        return

    if text == "رفع ادمن": await promote_admin(u,c)
    elif text == "تنزيل ادمن": await demote_admin(u,c)
    elif text == "تفعيل الايدي بالصوره": await enable_photo(u,c)
    elif text == "تعطيل الايدي بالصوره": await disable_photo(u,c)
    elif "المطور" in text or "المطورين" in text: await send_dev_info(u,c)
    elif text == "تفعيل": await activate(u,c)
    elif text == "تعطيل": await deactivate(u,c)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, auto_reply))
    print("Tia شغال - فيه رفع وتنزيل")
    app.run_polling()

if __name__ == "__main__": main()
