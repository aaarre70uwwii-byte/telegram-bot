import os
import logging
import yt_dlp
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# جيب التوكن من Railway
TOKEN = os.getenv("BOT_TOKEN")

# كلمات ممنوعة للحماية التلقائية
BANNED_WORDS = ["رابط", "link", "http", "https", "t.me", "www.", "سب", "شتم"]

# ====== اوامر البوت ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "🛡️ <b>بوت الحماية والاغاني شغال 24 ساعة</b>\n\n"
        "<b>اوامر الحماية:</b>\n"
        "/ban - حظر عضو بالرد عليه\n"
        "/mute - كتم عضو ساعة\n"
        "/unmute - فك الكتم\n"
        "<b>اوامر الاغاني:</b>\n"
        "/play اسم الاغنية - تشغيل اغنية من يوتيوب\n"
    )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ رد على رسالة العضو اللي تشتي تحظره")
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text("✅ تم حظر العضو بنجاح")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ رد على رسالة العضو اللي تشتي تكتمه")
    user_id = update.message.reply_to_message.from_user.id
    until = update.message.date + 3600 # ساعة واحدة
    await context.bot.restrict_chat_member(
        update.effective_chat.id, user_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until
    )
    await update.message.reply_text("🔇 تم كتم العضو لمدة ساعة")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ رد على رسالة العضو")
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.restrict_chat_member(
        update.effective_chat.id, user_id,
        permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True)
    )
    await update.message.reply_text("🔊 تم فك الكتم")

# فلتر الحماية التلقائي
async def auto_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.lower()
    for word in BANNED_WORDS:
        if word in text:
            try:
                await update.message.delete()
                await update.message.reply_text(f"🚫 تم حذف رسالة: ممنوع ارسال الروابط والسب")
            except:
                pass
            break

# ====== اوامر الاغاني ======
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🎵 استخدم: `/play اسم الاغنية`")

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🎵 جاري البحث وتحميل: {query}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=open('song.mp3', 'rb'),
                title=info['title'],
                performer=info.get('uploader', 'Unknown')
            )
            os.remove("song.mp3")
            await msg.delete()
    except Exception as e:
        await msg.edit_text("❌ ما قدرت احمل الاغنية. جرب اسم ثاني")

def main():
    app = Application.builder().token(TOKEN).build()

    # اضافة الاوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("play", play))

    # فلتر تلقائي
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_filter))

    print("البوت شغال...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
