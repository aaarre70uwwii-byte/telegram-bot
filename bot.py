import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "Tia"
DATA_FILE = "data.json"

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
except:
    data = {"groups": {}, "devs": [], "locks": {}, "welcome": {}, "rules": {}}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_dev(user_id): return user_id in data["devs"]
def is_admin(user_id, chat): return user_id in data["devs"] or chat.get_member(user_id).status in ['administrator', 'creator']

def get_lock(chat_id, key):
    chat_id = str(chat_id)
    return data["locks"].get(chat_id, {}).get(key, False)

def set_lock(chat_id, key, value):
    chat_id = str(chat_id)
    if chat_id not in data["locks"]: data["locks"][chat_id] = {}
    data["locks"][chat_id][key] = value
    save_data()

# ========== القوائم الرئيسية ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """‌‌‏أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━━━
◂ /م1 : اوامر الادمنيه
◂ /م2 : اوامر الاعدادات
◂ /م3 : اوامر القفل - الفتح
◂ /م4 : اوامر التسليه
◂ /م5 : اوامر Dev
◂ /م6 : الاوامر الخدميه
━━━━━━━━━━━━"""
    await update.message.reply_text(text)

async def m1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """◂ م1 : اوامر الادمنيه
━━━━━━━━━━━━
- اوامر الرفع والتنزيل :
رفع ادمن - تنزيل ادمن - رفع مشرف - تنزيل مشرف
- اوامر المسح :
مسح الكل - مسح المحظورين - مسح المكتومين
- اوامر الطرد والحظر :
حظر - طرد - كتم - الغاء الحظر - الغاء الكتم - تقييد"""
    await update.message.reply_text(text)

async def m2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """2:اوامر الاعدادات :
━━━━━━━━━━━━
الرابط - المالكين - الادمنيه - المحظورين - المكتومين
معلوماتي - القوانين
ضع الترحيب - ضع قوانين - ضع رابط"""
    await update.message.reply_text(text)

async def m3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """3:اوامر القفل والفتح :
━━━━━━━━━━━━
قفل الروابط - فتح الروابط
قفل الصور - فتح الصور
قفل الفيديو - فتح الفيديو
قفل الملصقات - فتح الملصقات
قفل الدردشه - فتح الدردشه
قفل الكل - فتح الكل
تفعيل الترحيب - تعطيل الترحيب"""
    await update.message.reply_text(text)

async def m5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_dev(update.effective_user.id): return await update.message.reply_text("للمطور فقط")
    text = """◂ م5 : اوامر Dev
━━━━━━━━━━━━
حظر عام - الغاء حظر عام
اذاعه + النص
تحديث - اعاده تشغيل"""
    await update.message.reply_text(text)

# ========== اوامر الادارة ==========
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("رد على الشخص")
    await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)
    await update.message.reply_text("تم الحظر ✅")
async def unban(update: Update,
