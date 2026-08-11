 import os
import json
import asyncio
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

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

# ========== الايدي نص ==========
async def show_id(u,c):
    uid, name = get_target(u)
    cid = str(u.effective_chat.id)
    rank = get_rank(uid, cid)

    text = f"""
