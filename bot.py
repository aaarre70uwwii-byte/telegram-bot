import json
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatMemberStatus, ParseMode

TOKEN = "ضع_التوكن_هنا" # عدل التوكن
OWNER_ID = 7488375443
DB_FILE = "groups.json"

try:
    with open(DB_FILE, "r", encoding="utf-8") as f: DATA = json.load(f)
except: DATA = {}

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(DATA, f, ensure_ascii=False, indent=2)

def get_chat(chat_id):
    if str(chat_id) not in DATA:
        DATA[str(chat_id)] = {
            "admins":[], "banned":[], "muted":[], "warns":{},
            "welcome":"مرحبا {name} في {chat}",
            "rules":"لا يوجد قوانين",
            "locks":{"links":False,"flood":False}
        }
        save()
    return DATA[str(chat_id)]

async def is_admin(update: Update):
    user = update.effective_user.id
    chat = update.effective_chat.id
    member = await update.effective_chat.get_member(user)
    if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or user == OWNER_ID:
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"انا بوت حماية الجروبات 🛡️\nضفني ادمن وفعل الصلاحيات")

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("قفل الروابط", callback_data="lock_links"), InlineKeyboardButton("فتح الروابط", callback_data="unlock_links")],
        [InlineKeyboardButton("الاوامر", callback_data="cmds")]
    ])
    await update.message.reply_text("لوحة الحماية", reply_markup=kb)

# اوامر الحماية الاساسية
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return await update.message.reply_text("رد على الشخص")
    user = update.message.reply_to_message.from_user
    await update.effective_chat.ban_member(user.id)
    get_chat(update.effective_chat.id)["banned"].append(user.id); save()
    await update.message.reply_text(f"🚫 تم حظر {user.first_name}")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    await update.effective_chat.ban_member(user.id)
    await update.effective_chat.unban_member(user.id)
    await update.message.reply_text(f"👢 تم طرد {user.first_name}")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    await update.effective_chat.restrict_member(user.id, ChatPermissions(can_send_messages=False))
    get_chat(update.effective_chat.id)["muted"].append(user.id); save()
    await update.message.reply_text(f"🔇 تم كتم {user.first_name}")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    await update.effective_chat.restrict_member(user.id, ChatPermissions(can_send_messages=True))
    chat = get_chat(update.effective_chat.id)
    if user.id in chat["muted"]: chat["muted"].remove(user.id); save()
    await update.message.reply_text(f"🔊 تم فك الكتم عن {user.first_name}")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    chat = get_chat(update.effective_chat.id)
    uid = str(user.id)
    chat["warns"][uid] = chat["warns"].get(uid, 0) + 1
    save()
    if chat["warns"][uid] >= 3:
        await update.effective_chat.ban_member(user.id)
        await update.message.reply_text(f"🚫 تم حظر {user.first_name} بسبب 3 تحذيرات")
    else:
        await update.message.reply_text(f"⚠️ تحذير {chat['warns'][uid]}/3 لـ {user.first_name}")

async def del_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if update.message.reply_to_message:
        await update.message.reply_to_message.delete()
        await update.message.delete()

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if update.message.reply_to_message:
        await update.message.reply_to_message.pin()

async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    get_chat(update.effective_chat.id)["admins"].append(user.id); save()
    await update.message.reply_text(f"👑 تم رفع {user.first_name}")

async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    chat = get_chat(update.effective_chat.id)
    if user.id in chat["admins"]: chat["admins"].remove(user.id); save()
    await update.message.reply_text(f"👤 تم تنزيل {user.first_name}")

# الاعدادات
async def setrules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    rules = " ".join(context.args)
    get_chat(update.effective_chat.id)["rules"] = rules; save()
    await update.message.reply_text("✅ تم حفظ القوانين")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules = get_chat(update.effective_chat.id)["rules"]
    await update.message.reply_text(f"📜 القوانين:\n{rules}")

async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    welcome = " ".join(context.args)
    get_chat(update.effective_chat.id)["welcome"] = welcome; save()
    await update.message.reply_text("✅ تم حفظ رسالة الترحيب\nاستخدم {name} للاسم {chat} للقروب")

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    lock_type = context.args[0]
    get_chat(update.effective_chat.id)["locks"][lock_type] = True; save()
    await update.message.reply_text(f"🔒 تم قفل {lock_type}")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    lock_type = context.args[0]
    get_chat(update.effective_chat.id)["locks"][lock_type] = False; save()
    await update.message.reply_text(f"🔓 تم فتح {lock_type}")

# الترحيب والحماية التلقائية
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        chat = get_chat(update.effective_chat.id)
        text = chat["welcome"].format(name=user.first_name, chat=update.effective_chat.title)
        await update.message.reply_text(text)

async def anti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update): return
    chat = get_chat(update.effective_chat.id)
    msg = update.message.text or ""
    if chat["locks"]["links"] and "http" in msg:
        await update.message.delete()
        await update.message.reply_text("ممنوع الروابط")
    if chat["locks"]["flood"]:
        # حماية بسيطة من التكرار
        pass

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("kick", kick))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("del", del_msg))
app.add_handler(CommandHandler("pin", pin))
app.add_handler(CommandHandler("promote", promote))
app.add_handler(CommandHandler("demote", demote))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("setrules", setrules))
app.add_handler(CommandHandler("setwelcome", setwelcome))
app.add_handler(CommandHandler("lock", lock))
app.add_handler(CommandHandler("unlock", unlock))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti))

app.run_polling()
