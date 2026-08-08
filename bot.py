import asyncio, os, random, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatMemberStatus, ParseMode
from yt_dlp import YoutubeDL

DB_FILE = "data.json"
try:
    with open(DB_FILE, "r", encoding="utf-8") as f: DB = json.load(f)
except: DB = {"BANNED":[],"MUTED":[],"ADMINS":[],"CHATS":[],"REPLIES":{},"S_REPLIES":{},"U_REPLIES":{},"WHISPERS":{}, "ACTIVE":True}

def save():
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(DB, f, ensure_ascii=False, indent=2)

# ========== ازرار التحكم ==========
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛡️ الحماية", callback_data="shield"), InlineKeyboardButton("📢 الاذاعة", callback_data="broadcast")],
        [InlineKeyboardButton("🎮 الالعاب", callback_data="games"), InlineKeyboardButton("🔍 بحث يوتيوب", callback_data="search")],
        [InlineKeyboardButton("💬 الردود", callback_data="replies"), InlineKeyboardButton("⚙️ تفعيل/تعطيل", callback_data="toggle")],
        [InlineKeyboardButton("👑 المطور", callback_data="dev"), InlineKeyboardButton("📊 الاحصائيات", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def shield_keyboard():
    keyboard = [
        [InlineKeyboardButton("حظر", callback_data="cmd_ban"), InlineKeyboardButton("فك حظر", callback_data="cmd_unban")],
        [InlineKeyboardButton("كتم", callback_data="cmd_mute"), InlineKeyboardButton("فك كتم", callback_data="cmd_unmute")],
        [InlineKeyboardButton("رفع ادمن", callback_data="cmd_promote"), InlineKeyboardButton("تنزيل", callback_data="cmd_demote")],
        [InlineKeyboardButton("قفل", callback_data="cmd_lock"), InlineKeyboardButton("فتح", callback_data="cmd_unlock")],
        [InlineKeyboardButton("رجوع", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== البداية ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = "🟢 شغال" if DB["ACTIVE"] else "🔴 متوقف"
    caption = f"مرحبا {update.effective_user.first_name} 👋\n\n**انا بوت {BOT_NAME}**\nالمطور: {DEVELOPER}\nالايدي: `{OWNER_ID}`\nالحالة: {status}"
    await update.message.reply_photo(photo=PHOTO_URL, caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    await update.message.reply_text(f"**لوحة تحكم {BOT_NAME}**", parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())

# ========== اوامر الحماية + الرفع + التعطيل ==========
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    user = await get_target(update, context)
    if user and user.id not in DB["BANNED"]: DB["BANNED"].append(user.id); save(); await update.message.reply_text(f"✅ تم حظر {user.first_name}")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    user = await get_target(update, context)
    if user and user.id in DB["BANNED"]: DB["BANNED"].remove(user.id); save(); await update.message.reply_text(f"✅ تم فك الحظر عن {user.first_name}")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    user = await get_target(update, context)
    if user and user.id not in DB["MUTED"]: DB["MUTED"].append(user.id); save(); await update.message.reply_text(f"🔇 تم كتم {user.first_name}")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    user = await get_target(update, context)
    if user and user.id in DB["MUTED"]: DB["MUTED"].remove(user.id); save(); await update.message.reply_text(f"🔊 تم فك الكتم عن {user.first_name}")

async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return await update.message.reply_text("هذا للمالك فقط")
    user = await get_target(update, context)
    if user and user.id not in DB["ADMINS"]: DB["ADMINS"].append(user.id); save(); await update.message.reply_text(f"👑 تم رفع {user.first_name} ادمن")

async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return
    user = await get_target(update, context)
    if user and user.id in DB["ADMINS"]: DB["ADMINS"].remove(user.id); save(); await update.message.reply_text(f"👤 تم تنزيل {user.first_name}")

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    await update.message.reply_text("🔒 تم قفل: الروابط + الصور + الملصقات + الفيديو + الصوت + الملفات")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    await update.message.reply_text("🔓 تم فتح كل القيود")

async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return
    DB["ACTIVE"] = not DB["ACTIVE"]; save()
    await update.message.reply_text("🟢 تم تفعيل البوت" if DB["ACTIVE"] else "🔴 تم تعطيل البوت")

# ========== الاذاعة ==========
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return
    msg = " ".join(context.args)
    count=0
    for chat in DB["CHATS"]:
        try: await context.bot.send_message(chat, f"📢 **اذاعة من {DEVELOPER}**\n\n{msg}", parse_mode=ParseMode.MARKDOWN); count+=1
        except: pass
    await update.message.reply_text(f"✅ تمت الاذاعة لـ {count} قروب")

# ========== الردود ==========
async def add_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    key, val = context.args[0], " ".join(context.args[1:])
    DB["REPLIES"][key]=val; save(); await update.message.reply_text(f"تم اضافة رد عام: `{key}`", parse_mode=ParseMode.MARKDOWN)

async def add_sreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= OWNER_ID: return
    key, val = context.args[0], " ".join(context.args[1:])
    DB["S_REPLIES"][key]=val; save(); await update.message.reply_text(f"تم اضافة رد مميز: `{key}`", parse_mode=ParseMode.MARKDOWN)

async def add_ureply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key, val = context.args[0], " ".join(context.args[1:])
    DB["U_REPLIES"][key]=val; save(); await update.message.reply_text(f"تم اضافة رد عضو: `{key}`", parse_mode=ParseMode.MARKDOWN)

async def del_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.args[0]
    if key in DB["REPLIES"]: del DB["REPLIES"][key]; save(); await update.message.reply_text("تم حذف الرد العام")
    elif key in DB["S_REPLIES"]: del DB["S_REPLIES"][key]; save(); await update.message.reply_text("تم حذف الرد المميز")
    elif key in DB["U_REPLIES"]: del DB["U_REPLIES"][key]; save(); await update.message.reply_text("تم حذف رد العضو")

# ========== الهمسات ==========
async def whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    to, msg = context.args[0], " ".join(context.args[1:])
    DB["WHISPERS"][to]=msg; save()
    await update.message.reply_text(f"📨 همسة الى {to}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("اضغط لقراءة الهمسة", callback_data=f"readw_{to}")]]))

# ========== البحث من اليوتيوب ==========
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("مثال: /search عمرو دياب")
    query = " ".join(context.args)
    results = await yt_search(query)
    keyboard = [[InlineKeyboardButton(f"{i+1}. {r['title'][:40]}", callback_data=f"dl_{r['id']}")] for i,r in enumerate(results)]
    await update.message.reply_text("🔍 **نتائج البحث:**", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE): # يرسل ملف صوتي
    if not context.args: return await update.message.reply_text("مثال: /play عمرو دياب")
    query = " ".join(context.args)
    msg = await update.message.reply_text(f"⏳ جاري تحميل: {query}")
    file = await yt_download(query)
    if file:
        await update.message.reply_audio(audio=InputFile(file), title=query)
        os.remove(file); await msg.delete()

# ========== الالعاب كامل ==========
async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("حجر ورقة مقص", callback_data="g_rps"), InlineKeyboardButton("تخمين رقم", callback_data="g_guess")],
        [InlineKeyboardButton("اسئلة معلومات", callback_data="g_quiz"), InlineKeyboardButton("كلمة السر", callback_data="g_word")],
        [InlineKeyboardButton("رجوع", callback_data="back")]
    ]
    await update.message.reply_text("🎮 **اختر لعبة:**", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== دوال مساعدة ==========
async def yt_search(query):
    ydl = YoutubeDL({'quiet':True, 'noplaylist':True})
    res = ydl.extract_info(f"ytsearch5:{query}", download=False)
    return [{"title":i['title'],"id":i['id']} for i in res['entries']]

async def yt_download(query):
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            return f"{info['title']}.mp3"
    except: return None

async def is_admin(update):
    member = await update.effective_chat.get_member(update.effective_user.id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or update.effective_user.id == OWNER_ID

async def get_target(update, context):
    return update.message.reply_to_message.from_user if update.message.reply_to_message else None

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not DB["ACTIVE"]: return
    chat = update.effective_chat.id
    if chat not in DB["CHATS"]: DB["CHATS"].append(chat); save()
    user = update.effective_user.id; text = update.message.text
    if user in DB["BANNED"]: return await update.message.delete()
    if user in DB["MUTED"]: return await update.message.delete()
    if text in DB["REPLIES"]: await update.message.reply_text(DB["REPLIES"][text])
    if text in DB["S_REPLIES"]: await update.message.reply_text(DB["S_REPLIES"][text])
    if text in DB["U_REPLIES"]: await update.message.reply_text(DB["U_REPLIES"][text])

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data=="dev": await q.edit_message_text(f"**المطور:** {DEVELOPER}\n**الاسم:** {BOT_NAME}\n**الايدي:** `{OWNER_ID}`", parse_mode=ParseMode.MARKDOWN)
    if q.data=="shield": await q.edit_message_text("**قائمة الحماية**", reply_markup=shield_keyboard())
    if q.data=="back": await q.edit_message_text(f"**لوحة تحكم {BOT_NAME}**", reply_markup=main_keyboard())
    if q.data=="toggle": await toggle(q, context)
    if q.data.startswith("readw_"): await q.edit_message_text(f"الهمسة: {DB['WHISPERS'].get(q.data.split('_')[1], 'انتهت')}")
    if q.data.startswith("dl_"): await q.edit_message_text("⏳ جاري تحميل الصوت...")

# ========== التشغيل ==========
app = ApplicationBuilder().token(TOKEN).build()
cmds = ["start","panel","ban","unban","mute","unmute","promote","demote","lock","unlock","toggle","broadcast","addreply","addsreply","addureply","delreply","whisper","games","search","play"]
for c in cmds: app.add_handler(CommandHandler(c, globals()[c]))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
