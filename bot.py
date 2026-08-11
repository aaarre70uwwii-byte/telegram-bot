import os
import json
import asyncio
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from PIL import Image, ImageDraw, ImageFont
import io

TOKEN = os.getenv("BOT_TOKEN")
DEV_ID = 7488375443
DATA_FILE = "data.json"

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except: data = {"devs": [DEV_ID], "owners": {}, "managers": {}, "admins": {}, "active_groups": [], "custom_replies": {}, "member_replies": {}}

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def is_dev(uid): return uid in data["devs"]
def is_main_dev(uid): return uid == DEV_ID
def is_owner(uid, cid): return is_dev(uid) or uid in data["owners"].get(str(cid), [])
def is_manager(uid, cid): return is_owner(uid, cid) or uid in data["managers"].get(str(cid), [])
def is_admin(uid, cid): return is_manager(uid, cid) or uid in data["admins"].get(str(cid), [])
def is_active(cid): return str(cid) in data["active_groups"]

def get_rank(uid, cid):
    if uid == DEV_ID: return "👑 مطور اساسي"
    if is_dev(uid): return "🛡️ مطور"
    if is_owner(uid, cid): return "💎 مالك"
    if is_manager(uid, cid): return "⭐ مدير"
    if is_admin(uid, cid): return "🔰 ادمن"
    return "👤 عضو"

def get_panel():
    keyboard = [
        [KeyboardButton("👑 المطور"), KeyboardButton("🆔 الايدي")],
        [KeyboardButton("📊 لوحة"), KeyboardButton("✅ تفعيل")],
        [KeyboardButton("➕ اضف رد"), KeyboardButton("➕ رد عضو")],
        [KeyboardButton("⬆️ رفع مطور"), KeyboardButton("⬆️ رفع مالك")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(u,c):
    await u.message.reply_text(f"مرحبا {u.effective_user.first_name} 👋", reply_markup=get_panel())

def get_target(u):
    if u.message.reply_to_message:
        return u.message.reply_to_message.from_user.id, u.message.reply_to_message.from_user.first_name
    else:
        return u.effective_user.id, u.effective_user.first_name

# ========== الايدي بصورة ==========
async def show_id_photo(u,c):
    uid, name = get_target(u)
    cid = str(u.effective_chat.id)
    rank = get_rank(uid, cid)

    # انشاء صورة
    img = Image.new('RGB', (500, 250), color = '#1e1e2e')
    d = ImageDraw.Draw(img)

    # اكتب النص
    d.text((20,20), f"ID: {uid}", fill=(255,255,255))
    d.text((20,60), f"Name: {name}", fill=(255,255,255))
    d.text((20,100), f"Rank: {rank}", fill=(87, 242, 135))
    d.text((20,140), f"Group: {u.effective_chat.title or 'Private'}", fill=(255,255,255))

    bio = io.BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    await u.message.reply_photo(photo=bio, caption=f"🆔 معلومات {name}")

# ========== الردود ==========
async def handle_replies(u,c):
    if not u.message.text: return False
    text = u.message.text.lower()
    cid = str(u.effective_chat.id)

    # الردود المميزة - للمدراء فقط
    if text in data.get("custom_replies", {}).get(cid, {}):
        await u.message.reply_text(data["custom_replies"][cid][text])
        return True

    # ردود الاعضاء - للكل
    if text in data.get("member_replies", {}).get(cid, {}):
        await u.message.reply_text(data["member_replies"][cid][text])
        return True
    return False

# ========== اضافة رد ==========
async def add_reply(u,c, reply_type):
    if not is_manager(u.effective_user.id, u.effective_chat.id): return await u.message.reply_text("هذا الامر للمدير فقط")
    if not u.message.reply_to_message or not u.message.reply_to_message.text:
        return await u.message.reply_text("رد على الرسالة اللي تريد تخليها جواب")

    key = u.message.text.replace("اضف رد ", "").replace("رد عضو ", "").strip()
    answer = u.message.reply_to_message.text
    cid = str(u.effective_chat.id)

    if reply_type == "custom":
        if cid not in data["custom_replies"]: data["custom_replies"][cid] = {}
        data["custom_replies"][cid][key.lower()] = answer
    else:
        if cid not in data["member_replies"]: data["member_replies"][cid] = {}
        data["member_replies"][cid][key.lower()] = answer

    save()
    await u.message.reply_text(f"✅ تم حفظ الرد على كلمة: {key}")

# ========== الرد التلقائي ==========
async def auto_reply(u,c):
    if not u.message: return
    text = u.message.text.strip(); cid = str(u.effective_chat.id); uid = u.effective_user.id

    if not is_active(cid) and not is_main_dev(uid) and not text.startswith("تفعيل"): return

    # شيك على الردود اول
    if await handle_replies(u,c): return

    if text in ["لوحة", "📊 لوحة"]: return await u.message.reply_text("اختر:", reply_markup=get_panel())
    if text in ["الايدي", "🆔 الايدي"]: return await show_id_photo(u,c)

    if text.startswith("اضف رد "): return await add_reply(u,c,"custom")
    if text.startswith("رد عضو "): return await add_reply(u,c,"member")

    if text in ["رفع مطور"]:
        if not is_main_dev(uid): return
        target = get_target(u)[0]
        if target not in data["devs"]: data["devs"].append(target); save()
        await u.message.reply_text("✅ تم رفع مطور", reply_markup=get_panel())

    if text in ["تفعيل", "✅ تفعيل"]:
        if not is_owner(uid, cid): return await u.message.reply_text("لازم تكون مالك")
        if cid not in data["active_groups"]: data["active_groups"].append(cid); save()
        return await u.message.reply_text("✅ تم تفعيل المجموعة", reply_markup=get_panel())

async def main():
    app
