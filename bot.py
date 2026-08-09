import os
import telebot
import yt_dlp
import threading
from flask import Flask

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# ===== امر تحميل الاغاني =====
@bot.message_handler(commands=['song'])
def download_song(message):
    query = message.text.replace("/song ", "")
    if not query:
        bot.reply_to(message, "استخدم: /song اسم الاغنية")
        return
    
    msg = bot.reply_to(message, f"جاري البحث وتحميل: {query} ...⏳")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch1' # يبحث اول نتيجة في اليوتيوب
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            title = info['title']
        
        # يرسل الصوت
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=title, performer="YouTube")
        
        os.remove(filename) # يحذف الملف بعد الارسال
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"صار خطأ: {e}")

# ===== اوامر الحماية حقك =====
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id, f"🔥 اهلا {user.first_name}")

@bot.message_handler(commands=['ban', 'mute'])
def admin_cmds(message):
    if message.from_user.id!= ADMIN_ID: return
    # باقي اوامر الحماية

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, """🔥 بوت حماية + اغاني 𝐓𝐢𝐚

**تحميل اغاني:**
`/song اسم الاغنية` - ينزلها صوت MP3

**حماية:**
`/ban` `/mute` رد على العضو""", parse_mode="Markdown")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
