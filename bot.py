from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
import time
import os

# ====== قاعدة بيانات مؤقتة ======
warnings = {} # تحذيرات
playlist = [] # قائمة التشغيل
user_messages = {}
playing_songs = {}

# ====== إعدادات الحماية القوية ======
BANNED_WORDS = ["كلمة سب1", "كلمة سب2", "تفجير"]
BANNED_LINKS = ["http://", "https://", "t.me/", ".com", "@"]
SPAM_LIMIT = 5

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
    'noplaylist': True
}

def music_buttons():
    keyboard = [
        [InlineKeyboardButton("⏸️ إيقاف", callback_data="pause"), InlineKeyboardButton("▶️ تشغيل", callback_data="resume")],
        [InlineKeyboardButton("⏭️ التالي", callback_data="skip"), InlineKeyboardButton("🗑️ حذف", callback_data="delete")]
    ]
    return InlineKeyboardMarkup(keyboard)

def whisper_buttons(user_id, sender_id):
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ تمت القراءة", callback_data=f"read_{user_id}_{sender_id}")]])

# ====== أوامر أساسية ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🛡️ Siraj Guard V2

الحماية:
/ban /mute /unmute /warn - رد على رسالة

الأغاني:
/play اسم /song رابط /playlist عرض القائمة

أخرى:
/whisper @user رسالة /id
"""
    await update.message.reply_text(text)

async def id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 ايديك: {update.effective_user.id}", parse_mode="Markdown")

# ====== أوامر المشرفين ======
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    member = await context.bot.get_chat_member(update.effective_chat.id, user.id)
    if member.status in ["administrator", "creator"]:
        return await update.message.reply_text("❌ ما اقدر احظر مشرف")
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"✅ تم حظر {user.first_name}")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        until = time.time() + 3600
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions={"can_send_messages": False}, until_date=until)
        await update.message.reply_text("🔇 تم الكتم ساعة")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions={"can_send_messages": True})
        await update.message.reply_text("🔊 تم فك الكتم")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        chat_id = update.effective_chat.id
        if chat_id not in warnings: warnings[chat_id] = {}
        warnings[chat_id][user_id] = warnings[chat_id].get(user_id, 0) + 1

        count = warnings[chat_id][user_id]
        await update.message.reply_text(f"⚠️ تحذير {count}/3 لـ {update.message.reply_to_message.from_user.first_name}")

        if count >= 3:
            await context.bot.ban_chat_member(chat_id, user_id)
            await update.message.reply_text("🚫 تم الحظر بسبب 3 تحذيرات")

# ====== نظام الحماية القوي ======
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.lower() if update.message.text else ""
