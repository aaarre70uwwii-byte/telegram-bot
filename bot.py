import os, logging, asyncio, yt_dlp, random
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.types.input_stream import AudioQuality, StreamType

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
DEVELOPER_ID = 7488375443 # ايديك
DEV_NAME = "𝐀𝐥𝐒𝐄𝐃"
ASSISTANT_NAME = "@rrrrxe"

AUTO_REPLIES = {"هلا": "هلا والله ❤️"}
SPECIAL_REPLIES = {"احبك": "وانا احبك اكثر 😘"}
MEMBER_REPLIES = {}
BANNED_WORDS = ["رابط", "http", "t.me", "سب"]
GROUP_CHATS = set()
WHISPERS = {}
POINTS = {}
GAMES = {}
QUEUE = {}
vc_calls = PyTgCalls()

# ====== ستارت ======
async def start(u,c):
    if u.effective_chat.type in ["group", "supergroup"]: GROUP_CHATS.add(u.effective_chat.id)
    text = f"""🛡️ <b>بوت {DEV_NAME} V5</b>
/panel - لوحة التحكم
/play اسم - تشغيل اغنية
/games - الالعاب
/ban /kick /mute /unmute /promote /demote
/lock /unlock /broadcast
/addreply /addspecial /addmember
/whisper /me /avatar /dev"""
    await u.message.reply_html(text)

# ====== الحماية + الرفع ======
async def ban(u,c): await c.bot.ban_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id); await u.message.reply_text("✅ تم الحظر")
async def unban(u,c): await c.bot.unban_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id); await u.message.reply_text("✅ تم فك الحظر")
async def kick(u,c): await c.bot.ban_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id); await c.bot.unban_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id); await u.message.reply_text("👢 تم الطرد")
async def mute(u,c): await c.bot.restrict_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=False)); await u.message.reply_text("🔇 تم الكتم")
async def unmute(u,c): await c.bot.restrict_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=True)); await u.message.reply_text("🔊 تم فك الكتم")
async def promote(u,c): await c.bot.promote_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id, can_manage_chat=True, can_delete_messages=True); await u.message.reply_text("👑 تم الرفع")
async def demote(u,c): await c.bot.promote_chat_member(u.effective_chat.id, u.message.reply_to_message.from_user.id, can_manage_chat=False); await u.message.reply_text("👤 تم التنزيل")
async def lock(u,c): await c.bot.set_chat_permissions(u.effective_chat.id, ChatPermissions(can_send_messages=False)); await u.message.reply_text("🔒 تم تعطيل الشات")
async def unlock(u,c): await c.bot.set_chat_permissions(u.effective_chat.id, ChatPermissions(can_send_messages=True)); await u.message.reply_text("🔓 تم تفعيل الشات")

# ====== الردود + الاذاعة ======
async def add_reply(u,c): key,value=" ".join(c.args).split("|",1); AUTO_REPLIES[key.strip()]=value.strip(); await u.message.reply_text("✅ تم")
async def add_special(u,c):
    if u.effective_user.id!=DEVELOPER_ID: return
    key,value=" ".join(c.args).split("|",1); SPECIAL_REPLIES[key.strip()]=value.strip(); await u.message.reply_text("✅ تم مميز")
async def add_member_reply(u,c):
    user_id = u.message.reply_to_message.from_user.id; key,value=" ".join(c.args).split("|",1)
    if user_id not in MEMBER_REPLIES: MEMBER_REPLIES[user_id]={}
    MEMBER_REPLIES[user_id][key.strip()]=value.strip(); await u.message.reply_text("✅ تم رد العضو")
async def broadcast(u,c):
    if u.effective_user.id!=DEVELOPER_ID: return
    msg=" ".join(c.args); [await c.bot.send_message(chat_id, f"📢 {DEV_NAME}\n\n{msg}", parse_mode="HTML") for chat_id in GROUP_CHATS]; await u.message.reply_text("✅ تمت الاذاعة")

# ====== الهمسات ======
async def whisper(u,c):
    to_user = u.message.reply_to_message.from_user; whisper_text = " ".join(c.args)
    whisper_id = f"{u.effective_chat.id}_{to_user.id}_{u.message_id}"
    WHISPERS[whisper_id] = {"from": u.effective_user.full_name, "text": whisper_text}
    keyboard = [[InlineKeyboardButton("🔒 اضغط لقراءة الهمسة", callback_data=f"whisper_{whisper_id}")]]
    await u.message.reply_text(f"💌 همسة لـ {to_user.first_name}", reply_markup=InlineKeyboardMarkup(keyboard))
async def show_whisper(u,c): query = u.callback_query; data = WHISPERS.get(query.data.split("_",1)[1]); await query.answer(f"من: {data['from']}\n{data['text']}", show_alert=True)

# ====== الالعاب ======
async def games_menu(u,c): keyboard = [[InlineKeyboardButton("❌⭕ اكس او", callback_data="xo_new")],[InlineKeyboardButton("🏆 التوب", callback_data="top")]]; await u.message.reply_text("🎮 العاب", reply_markup=InlineKeyboardMarkup(keyboard))
async def xo_new(u,c): query=u.callback_query; GAMES[query.message.chat_id]={"board":[" "]*9,"turn":"❌"}; buttons=[[InlineKeyboardButton(" ",callback_data=f"xo_{i}")] for i in range(9)]; await query.edit_message_text("دور: ❌",reply_markup=InlineKeyboardMarkup([buttons[0:3],buttons[3:6],buttons[6:9]]))
async def xo_move(u,c): query=u.callback_query;i=int(query.data.split("_")[1]);game=GAMES[query.message.chat_id]; game["board"][i]=game["turn"];game["turn"]="⭕" if game["turn"]=="❌" else "❌"; buttons=[[InlineKeyboardButton(game["board"][j],callback_data=f"xo_{j}")] for j in range(9)]; await query.edit_message_text(f"دور: {game['turn']}",reply_markup=InlineKeyboardMarkup([buttons[0:3],buttons[3:6],buttons[6:9]]))
async def show_top(u,c): top=sorted(POINTS.items(),key=lambda x:x[1],reverse=True)[:5];text="🏆 توب\n";[text:=text+f"{i+1}. {uid} - {p}\n" for i,(uid,p) in enumerate(top)]; await u.callback_query.edit_message_text(text)

# ====== معلومات + المطور ======
async def me(u,c): user=u.effective_user; await u.message.reply_html(f"👤 {user.full_name}\n@{user.username}\n<code>{user.id}</code>")
async def avatar(u,c): user = u.message.reply_to_message.from_user if u.message.reply_to_message else u.effective_user; photos = await c.bot.get_user_profile_photos(user.id, limit=1); await u.message.reply_photo(photos.photos[0][-1].file_id)
async def dev(u,c): keyboard = [[InlineKeyboardButton(f"💬 {DEV_NAME}", url=f"https://t.me/rrrrxe")]]; await u.message.reply_text(f"👨‍💻 {DEV_NAME}", reply_markup=InlineKeyboardMarkup(keyboard))

# ====== الاغاني + ازرار التحكم ======
async def play(u,c):
    if not c.args: return await u.message.reply_text("🎵 /play اسم")
    chat_id = u.effective_chat.id; query = " ".join(c.args); msg = await u.message.reply_text("🎵 جاري التحميل...")
    ydl_opts = {'format':'bestaudio', 'noplaylist':True}; info = yt_dlp.YoutubeDL(ydl_opts).extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    keyboard = [[InlineKeyboardButton("⏸️", callback_data="pause"),InlineKeyboardButton("▶️", callback_data="resume")],[InlineKeyboardButton("⏭️", callback_data="skip"),InlineKeyboardButton("⏹️", callback_data="stop")]]
    try: await vc_calls.join_group_call(chat_id, AudioPiped(info['url']), stream_type=StreamType().local_stream); await msg.edit_text(f"▶️ {info['title']}", reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        if chat_id not in QUEUE: QUEUE[chat_id] = []
        QUEUE[chat_id].append({"title": info['title'], "url": info['url']}); await msg.edit_text(f"➕ {info['title']}")

async def music_buttons(u,c):
    query = u.callback_query; chat_id = query.message.chat_id
    if query.data == "pause": await vc_calls.pause_stream(chat_id); await query.answer("⏸️")
    elif query.data == "resume": await vc_calls.resume_stream(chat_id); await query.answer("▶️")
    elif query.data == "skip":
        if QUEUE.get(chat_id): next_song = QUEUE[chat_id].pop(0); await vc_calls.leave_group_call(chat_id); await vc_calls.join_group_call(chat_id, AudioPiped(next_song["url"]))
    elif query.data == "stop": await vc_calls.leave_group_call(chat_id); await query.edit_message_text("⏹️ تم الايقاف")

# ====== لوحة التحكم ======
async def admin_panel(u,c):
    keyboard = [
        [InlineKeyboardButton("🔒 تعطيل", callback_data="lock_all"), InlineKeyboardButton("🔓 تفعيل", callback_data="unlock_all")],
        [InlineKeyboardButton("👢 طرد", callback_data="kick_btn"), InlineKeyboardButton("🗑️ حذف", callback_data="delete_btn")],
        [InlineKeyboardButton("📢 اذاعة", callback_data="broadcast_btn"), InlineKeyboardButton("🎮 العاب", callback_data="games_btn")]
    ]
    await u.message.reply_text(f"⚙️ لوحة {DEV_NAME}", reply_markup=InlineKeyboardMarkup(keyboard))

async def panel_buttons(u,c):
    query = u.callback_query
    if query.data == "lock_all": await query.message.chat.set_permissions(ChatPermissions(can_send_messages=False)); await query.answer("🔒")
    elif query.data == "unlock_all": await query.message.chat.set_permissions(ChatPermissions(can_send_messages=True)); await query.answer("🔓")
    elif query.data == "delete_btn": await query.message.delete(); await query.answer("🗑️")
    elif query.data == "games_btn": await games_menu(query, None)

# ====== الفلتر ======
async def auto_filter(u,c):
    if not u.message or not u.message.text: return
    user_id = u.effective_user.id; text = u.message.text
    if user_id in MEMBER_REPLIES and text in MEMBER_REPLIES[user_id]: return await u.message.reply_text(MEMBER_REPLIES[user_id][text])
    if text in SPECIAL_REPLIES: return await u.message.reply_text(SPECIAL_REPLIES[text])
    if text in AUTO_REPLIES: return await u.message.reply_text(AUTO_REPLIES[text])
    for word in BANNED_WORDS:
        if word in text.lower(): await u.message.delete(); await u.message.reply_text("🚫"); return

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("panel",admin_panel))
    app.add_handler(CommandHandler("ban",ban)); app.add_handler(CommandHandler("unban",unban)); app.add_handler(CommandHandler("kick",kick)); app.add_handler(CommandHandler("mute",mute)); app.add_handler(CommandHandler("unmute",unmute))
    app.add_handler(CommandHandler("promote",promote)); app.add_handler(CommandHandler("demote",demote)); app.add_handler(CommandHandler("lock",lock)); app.add_handler(CommandHandler("unlock",unlock))
    app.add_handler(CommandHandler("addreply",add_reply)); app.add_handler(CommandHandler("addspecial",add_special)); app.add_handler(CommandHandler("addmember",add_member_reply))
    app.add_handler(CommandHandler("broadcast",broadcast)); app.add_handler(CommandHandler("dev",dev))
    app.add_handler(CommandHandler("play",play)); app.add_handler(CommandHandler("games",games_menu))
    app.add_handler(CommandHandler("whisper",whisper)); app.add_handler(CommandHandler("me",me)); app.add_handler(CommandHandler("avatar",avatar))
    app.add_handler(CallbackQueryHandler(show_whisper,pattern="^whisper_"))
    app.add_handler(CallbackQueryHandler(music_buttons, pattern="^(pause|resume|skip|stop)$"))
    app.add_handler(CallbackQueryHandler(panel_buttons, pattern="^(lock_all|unlock_all|delete_btn|games_btn)$"))
    app.add_handler(CallbackQueryHandler(xo_new,pattern="^xo_new")); app.add_handler(CallbackQueryHandler(xo_move,pattern="^xo_")); app.add_handler(CallbackQueryHandler(show_top,pattern="^top"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_filter))
    asyncio.run(vc_calls.start()); app.run_polling()

if __name__=="__main__": main()
