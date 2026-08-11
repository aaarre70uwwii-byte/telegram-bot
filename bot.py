import os
import json
from telegram import ReplyKeyboardMarkup, KeyboardButton
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

def get_panel():
    keyboard = [
        [KeyboardButton("المطور"), KeyboardButton("تفعيل"), KeyboardButton("تعطيل")],
        [KeyboardButton("رفع ادمن"), KeyboardButton("تنزيل ادمن")],
        [KeyboardButton("قفل الروابط"), KeyboardButton("فتح الروابط")],
        [KeyboardButton("لوحة")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def send_dev_info(u,c):
    mention = f"[{u.message.from_user.first_name}](tg://user?id={DEV_ID})"
    caption = f"👑 **المطور الاساسي** 👑\n{mention}\nالايدي: `{DEV_ID}`"
    await u.message.reply_text(caption, parse_mode='Markdown', reply_markup=get_panel())

async def promote_admin(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return await u.message.reply_text("انت مش ادمن")
    if not u.message.reply_to_message: return await u.message.reply_text("رد على الشخص")
    cid = str(u.effective_chat.id); uid = u.message.reply_to_message.from_user.id
    if cid not in data["admins"]: data["admins"][cid] = []
    if uid not in data["admins"][cid]:
        data["admins"][cid].append(uid); save()
        await u.message.reply_text("✅ تم رفعه ادمن", reply_markup=get_panel())

async def demote_admin(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    cid = str(u.effective_chat.id); uid = u.message.reply_to_message.from_user.id
    if cid in data["admins"] and uid in data["admins"][cid]:
        data["admins"][cid].remove(uid); save()
        await u.message.reply_text("✅ تم تنزيله", reply_markup=get_panel())

async def auto_reply(u,c):
    if not u.message: return
    text = u.message.text; cid = str(u.effective_chat.id)

    # السماح للمطور دايما + السماح بامر التفعيل
    if not is_active(cid) and u.effective_user.id!= DEV_ID and text!= "تفعيل":
        return

    if text == "لوحة": return await u.message.reply_text("اختر:", reply_markup=get_panel())
    if text == "المطور": return await send_dev_info(u,c)
    if text == "رفع ادمن": return await promote_admin(u,c)
    if text == "تنزيل ادمن": return await demote_admin(u,c)

    if text == "تفعيل":
        if not is_admin(u.effective_user.id, cid): return await u.message.reply_text("لازم تكون ادمن في الجروب")
        if cid not in data["active_groups"]: data["active_groups"].append(cid); save()
        return await u.message.reply_text("✅ تم تفعيل المجموعة", reply_markup=get_panel())

    if text == "تعطيل":
        if not is_admin(u.effective_user.id, cid): return
        if cid in data["active_groups"]: data["active_groups"].remove(cid); save()
        return await u.message.reply_text("❌ تم تعطيل المجموعة", reply_markup=get_panel())

    if text.lower() in data["custom_cmds"]:
        return await u.message.reply_text(data["custom_cmds"][text.lower()])

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, auto_reply))
    print("Tia كامل - شغال")
    app.run_polling()

if __name__ == "__main__": main()
