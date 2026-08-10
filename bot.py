import os
import random
import logging
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_NAME = "𝐓𝐢𝐚"
DEVELOPER_ID = 7488375443 # ايديك انت

if not BOT_TOKEN:
    raise ValueError("حط BOT_TOKEN في Railway Variables")

# === البيانات ===
BANNED_WORDS = ["غبي", "احمق", "كلب"]
BANNED_LINKS = ["http://", "https://", "t.me/", ".com"]
warnings = {}
muted_users = set()

def is_admin(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = context.bot.get_chat_member(chat_id, user_id)
    return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]

def is_dev(user_id):
    return user_id == DEVELOPER_ID

# === 1. اوامر البوت العامة ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"""مرحبا انا {BOT_NAME} 🤖🔒

**اوامر عامة:**
/help - عرض كل الاوامر
/song اسم - بحث اغنية
/rps حجر - حجر ورق مقص
/guess - تخمين رقم
/joke - نكتة
/id - يجيب ايديك وايدي القروب
"""
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"""📜 **اوامر {BOT_NAME}**

**اوامر عامة:**
/start /help /song /rps /guess /
