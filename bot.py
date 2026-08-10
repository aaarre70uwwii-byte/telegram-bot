import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "Tia"

# حط معرفك هنا بعد ما تجيبه من /id
ADMIN_IDS = [] 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        text = f"مرحبا انا {BOT_NAME} 💜\n\nضفني لجروب وخليني مشرف\nالاوامر:\n/start\n/help\n/id\n/mention"
    else:
        text = f"هلا بالجميع انا {BOT_NAME} 💜\nارسل /help عشان تشوف اوامري"
    await update.message.reply_text(text)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""**اوامر {BOT_NAME}:**
/start - تشغيل البوت
/help - المساعدة
/id - معرفك + معرف الجروب
/mention - يمنشن الكل
/kick - طرد عضو "للادمن فقط"
/ban - حظر عضو "للادمن فقط"
ملاحظة: رد على رسالة العضو مع الامر
"""
    await update.message.reply_text(text, parse_mode="Markdown")

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"معرفك: `{user_id}`\nمعرف الجروب: `{chat_id}`", parse_mode="Markdown")

async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    text = "منشن للكل 📢\n"
    async for member in chat.get_members():
        user = member.user
        if not user.is_bot:
            text += f"[{user.first_name}](tg://user?id={user.id}) "
    await update.message.reply_text(text, parse_mode="Markdown")

def is_admin(user_id, chat):
    return user_id in ADMIN_IDS or user_id == chat.owner.id

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id = update.effective_user.id
    if not is_admin(user_id, chat):
        await update.message.reply_text("هذا الامر للادمن فقط")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("رد على رسالة الشخص اللي تريد تطرده")
        return
    target_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(chat_id=chat.id, user_id=target_id)
    await update.message.reply_text("تم الطرد ✅")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id = update.effective_user.id
    if not is_admin(user_id, chat):
        await update.message.reply_text("هذا الامر للادمن فقط")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("رد على رسالة الشخص اللي تريد تحظره")
        return
    target_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(chat_id=chat.id, user_id=target_id)
    await update.message.reply_text("تم الحظر ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "مرحبا" in text or "هلا" in text:
        await update.message.reply_text(f"هلا والله 👋")

def main():
    if not TOKEN:
        print("حط BOT_TOKEN في Variables")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("mention", mention_all))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print(f"{BOT_NAME} شغال في الجروبات")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
import os
import json
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except: data = {"devs": [], "admins": {}, "owners": {}, "creators": {}, "vip": {}}

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def is_dev(uid): return uid in data["devs"]
def is_admin(uid, cid): return uid in data["devs"] or uid in data["admins"].get(str(cid), [])

# ========== م1 ==========
async def m1(u,c):
    text = """أهلاً بك عزيزي في قائمة الاوامر :
━━━━━
◂ م1 : اوامر الادمنيه
━━━━━━━━━━━━
- اوامر الرفع والتنزيل :
رفع مالك اساسي - تنزيل مالك اساسي
رفع مالك - تنزيل مالك
رفع مشرف - تنزيل مشرف
رفع منشئ - تنزيل منشئ
رفع مدير - تنزيل مدير
رفع ادمن - تنزيل ادمن
رفع مميز - تنزيل مميز
تنزيل الكل

- اوامر المسح :
مسح الكل - مسح المحظورين - مسح المكتومين

- اوامر الطرد والحظر :
حظر - طرد - كتم - تقييد
الغاء الحظر - الغاء الكتم - فك التقييد
━━━━━━━━━━━━"""
    await u.message.reply_text(text)

# ========== اوامر الرفع والتنزيل ==========
async def promote(u,c):
    if not is_dev(u.effective_user.id): return
    if not u.message.reply_to_message: return await u.message.reply_text("رد على الشخص")
    cid = str(u.effective_chat.id)
    uid = u.message.reply_to_message.from_user.id
    rank = u.message.text.split()[1] # ادمن, مدير, الخ

    ranks = {"ادمن": "admins", "مدير": "admins", "منشئ": "creators", "مالك": "owners", "مميز": "vip"}
    if rank in ranks:
        if cid not in data[ranks[rank]]: data[ranks[rank]][cid] = []
        if uid not in data[ranks[rank]][cid]: data[ranks[rank]][cid].append(uid); save()
        await u.message.reply_text(f"تم رفع {rank} ✅")

async def demote(u,c):
    if not is_dev(u.effective_user.id): return
    if not u.message.reply_to_message: return await u.message.reply_text("رد على الشخص")
    cid = str(u.effective_chat.id)
    uid = u.message.reply_to_message.from_user.id

    for r in ["admins", "owners", "creators", "vip"]:
        if cid in data[r] and uid in data[r][cid]: data[r][cid].remove(uid)
    save()
    await u.message.reply_text("تم التنزيل ✅")

async def demote_all(u,c):
    if not is_dev(u.effective_user.id): return
    cid = str(u.effective_chat.id)
    data["admins"][cid] = []; data["owners"][cid] = []; data["creators"][cid] = []; data["vip"][cid] = []
    save()
    await u.message.reply_text("تم تنزيل الكل ✅")

# ========== اوامر الحظر ==========
async def ban(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return await u.message.reply_text("رد على الشخص")
    await c.bot.ban_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id)
    await u.message.reply_text("تم الحظر ✅")

async def unban(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    await c.bot.unban_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id)
    await u.message.reply_text("تم الغاء الحظر ✅")

async def kick(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
    uid = u.message.reply_to_message.from_user.id
    await c.bot.ban_chat_member(u.effective_chat.id, uid)
    await c.bot.unban_chat_member(u.effective_chat.id, uid)
    await u.message.reply_text("تم الطرد ✅")

async def mute(u,c):
    if not is_admin(u.effective_user.id, u.effective_chat.id): return
    if not u.message.reply_to_message: return
