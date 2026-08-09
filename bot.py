import os
import telebot
import requests
import yt_dlp
import threading
from flask import Flask

TOKEN = os.environ.get("TOKEN")
YOUTUBE_API = os.environ.get("YOUTUBE_API", "")

bot = telebot.TeleBot(TOKEN)
app = Flask('')
warns = {} # {chat_id: {user_id: عدد التحذيرات}}

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except: return False

# ===== الحماية =====
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id, f"🔥 اهلا {user.first_name} نورت القروب")

@bot.message_handler(content_types=['text'])
def anti(message):
    if is_admin(message.chat.id, message.from_user.id): return # الادمن معفي
    text = message.text.lower()
    if "http" in text or "t.me/" in text:
        bot.delete_message(message.chat.id, message.message_id)
        bot.reply_to(message, "❌ ممنوع الروابط")
        warn_user(message)

def warn_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id not in warns: warns[chat_id] = {}
    warns[chat_id][user_id] = warns[chat_id].get(user_id, 0) + 1
    if warns[chat_id][user_id] >= 3:
        bot.ban_chat_member(chat_id, user_id)
        bot.send_message(chat_id, "تم الحظر بسبب 3 تحذيرات")
    else:
        bot.send_message(chat_id, f"تحذير {warns[chat_id][user_id]}/3")

# ===== اوامر الادمن =====
@bot.message_handler(commands=['ban','mute','unmute','kick'])
def admin_cmd(message):
    if not is_admin(message.chat.id, message.from_user.id): 
        return bot.reply_to(message, "انت مش ادمن")
    if not message.reply_to_message: return
    uid = message.reply_to_message.from_user.id
    cmd = message.text
    if cmd == '/ban': bot.ban_chat_member(message.chat.id, uid)
    if cmd == '/kick': bot.ban_chat_member(message.chat.id, uid); bot.unban_chat_member(message.chat.id, uid)
    if cmd == '/mute': bot.restrict_chat_member(message.chat.id, uid, can_send_messages=False)
    if cmd == '/unmute': bot.restrict_chat_member(message.chat.id, uid, can_send_messages=True)
    bot.reply_to(message, f"تم {cmd}")

# ===== يوتيوب + اغاني =====
@bot.message_handler(commands=['yt'])
def search_yt(message):
    query = message.text.replace("/yt ", "")
    url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API}&q={query}&part=snippet&type=video&maxResults=3"
    res = requests.get(url).json()
    if "items" in res:
        for item in res["items"]:
            title = item["snippet"]["title"]
            link = f"https://youtu.be/{item['id']['videoId']}"
            bot.send_message(message.chat.id, f"🎬 {title}\n{link}")

@bot.message_handler(commands=['song'])
def download_song(message):
    query = message.text.replace("/song ", "")
    msg = bot.reply_to(message, f"جاري تحميل: {query} ⏳")
    ydl_opts = {'format': 'bestaudio/best','outtmpl': 'song.%(ext)s','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}],'quiet': True, 'default_search': 'ytsearch1'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3")
        with open(filename, 'rb') as audio: bot.send_audio(message.chat.id, audio)
        os.remove(filename); bot.delete_message(message.chat.id, msg.message_id)
    except: bot.reply_to(message, "صار خطأ")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
