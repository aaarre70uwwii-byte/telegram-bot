 import os
import json
import asyncio
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
DEV_ID = 7488375443 # حط ايديك هنا
DATA_FILE = "data.json"

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except:
    data = {"devs": [DEV_ID], "owners": {}, "active_groups": []}

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def is_dev(uid): return uid in data["devs"]
def is_main_dev(uid): return uid == DEV_ID
def is_owner(uid, cid): return is_dev(uid) or uid in data["owners"].get(str(cid), [])
def is_active(cid): return str(cid) in data["active_groups"]

def get_panel():
    keyboard = [
        [KeyboardButton("✅ تفعيل"), KeyboardButton("❌ تعطيل")],
        [KeyboardButton("⬆️ رفع مالك"), KeyboardButton("⬇️ تنزيل مالك")],
        [KeyboardButton("⬆️ رفع مطور"), KeyboardButton("⬇️ تنزيل مطور")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(u,c):
    await u.message.reply_text("البوت شغال ✅", reply_markup=get_panel())

def get_target(u):
    if u.message.reply_to_message:
        return u.message.reply_to_message.from_user.id
    return None

# ========== اوامر المطور الاساسي فقط ==========
async def promote_dev(u,c):
    if not is_main_dev(u.effective_user.id): return
    uid = get_target(u)
    if not uid: return await u.message.reply_text("رد على الشخص")
    if uid not in data["devs"]: data["devs"].append(uid); save()
    await u.message.reply_text("✅ تم رفع مطور", reply_markup=get_panel())

async def demote_dev(u,c):
    if not is_main_dev(u.effective_user.id): return
    uid = get_target(u)
    if uid == DEV_ID: return await u.message.reply_text("ما اقدر انزل المطور الاساسي")
    if uid in data["devs"]: data["devs"].remove(uid); save()
    await u.message.reply_text("✅ تم تنزيل مطور", reply_markup=get_panel())

async def promote_owner(u,c):
    if not is_main_dev(u.effective_user.id): return
    uid = get_target(u)
    if not uid: return
    cid = str(u.effective_chat.id)
    if cid not in data["owners"]: data["owners"][cid] = []
    if uid not in data
