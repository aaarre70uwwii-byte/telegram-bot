import sqlite3
import time
import random
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

DB_NAME = "dev_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS warnings (chat_id INTEGER, user_id INTEGER, count INTEGER, PRIMARY KEY(chat_id, user_id))")
    conn.commit(); conn.close()
init_db()

def get_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def register_handlers(bot):

    @bot.message_handler(commands=['id'], chat_types=['group','supergroup','private'])
    def show_id(m):
        user = m.from_user
        chat = m.chat
        if m.reply_to_message:
            target = m.reply_to_message.from_user
            text = f"◂ **معلومات العضو**\n━━━━━━━━━━━━\n**الاسم:** {target.first_name}\n**اليوزر:** @{target.username}\n**الايدي:** `{target.id}`"
        else:
            text = f"◂ **معلوماتك**\n━━━━━━━━━━━━\n**الاسم:** {user.first_name}\n**اليوزر:** @{user.username}\n**الايدي:** `{user.id}`\n**ايدي القروب:** `{chat.id}`\n**الوقت:** {get_time()}"
        bot.reply_to(m, text, parse_mode="Markdown")

    @bot.message_handler(commands=['الرابط'], chat_types=['group','supergroup'])
    def get_link(m):
        if not m.from_user.id: return
        try:
            link = bot.export_chat_invite_link(m.chat.id)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔗 رابط القروب", url=link))
            bot.reply_to(m, "◂ **رابط القروب**\n━━━━━━━━━━━━", reply_markup=markup)
        except:
            bot.reply_to(m, "❌ ماقدر اجيب الرابط. تاكد اني ادمن وعندي صلاحية دعوة")

    @bot.message_handler(commands=['الوقت'], chat_types=['group','supergroup','private'])
    def show_time(m):
        bot.reply_to(m, f"🕐 **الوقت الان:**\n`{get_time()}`", parse_mode="Markdown")

    @bot.message_handler(commands=['تحويل'], chat_types=['group','supergroup'])
    def to_text(m):
        if not m.reply_to_message: return bot.reply_to(m, "❌ رد على الصورة او الملصق")
        if m.reply_to_message.sticker:
            bot.reply_to(m, f"اسم الملصق: `{m.reply_to_message.sticker.set_name}`", parse_mode="Markdown")
        elif m.reply_to_message.photo:
            bot.reply_to(m, "📸 هذه صورة")
        elif m.reply_to_message.voice:
            bot.reply_to(m, "🎤 هذه رسالة صوتية")
        else:
            bot.reply_to(m, "❌ ما اقدر احول هذا النوع")

    @bot.message_handler(commands=['احذف'], chat_types=['group','supergroup'])
    def delete_msg(m):
        if not m.reply_to_message: return bot.reply_to(m, "❌ رد على الرسالة اللي تريد تحذفها")
        try:
            bot.delete_message(m.chat.id, m.message_id)
            bot.delete_message(m.chat.id, m.reply_to_message.message_id)
        except:
            bot.reply_to(m, "❌ ماعندي صلاحية الحذف")

    @bot.message_handler(commands=['انذار'], chat_types=['group','supergroup'])
    def warn_user(m):
        if not m.reply_to_message: return bot.reply_to(m, "❌ رد على العضو")
        target = m.reply_to_message.from_user.id
        chat = m.chat.id

        conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
        cursor.execute("SELECT count FROM warnings WHERE chat_id =? AND user_id =?", (chat, target))
        row = cursor.fetchone()

        if row:
            count = row[0] + 1
            cursor.execute("UPDATE warnings SET count =? WHERE chat_id =? AND user_id =?", (count, chat, target))
        else:
            count = 1
            cursor.execute("INSERT INTO warnings VALUES (?,?,?)", (chat, target, count))
        conn.commit(); conn.close()

        if count >= 3:
            bot.reply_to(m, f"⛔ تم طرد {m.reply_to_message.from_user.first_name} بسبب 3 انذارات")
            try: bot.ban_chat_member(chat, target); bot.unban_chat_member(chat, target)
            except: pass
        else:
            bot.reply_to(m, f"⚠️ تم انذار {m.reply_to_message.from_user.first_name}\nالانذار رقم: {count}/3")

    @bot.message_handler(commands=['مسح_الانذارات'], chat_types=['group','supergroup'])
    def clear_warns(m):
        if not m.reply_to_message: return bot.reply_to(m, "❌ رد على العضو")
        target = m.reply_to_message.from_user.id
        conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
        cursor.execute("DELETE FROM warnings WHERE chat_id =? AND user_id =?", (m.chat.id, target))
        conn.commit(); conn.close()
        bot.reply_to(m, f"✅ تم مسح انذارات {m.reply_to_message.from_user.first_name}")

    @bot.message_handler(commands=['نكتة'], chat_types=['group','supergroup','private'])
    def joke(m):
        jokes = [
            "محش سألوه ليش تأخرت؟ قال كنت احلم 😂",
            "واحد غبي راح للدكتور قاله: دكتور انسى كثير. قاله: من متى؟ قاله: من متى ايش؟ 😂",
            "معلم قال لطالب: اذا عندك 10 تفاحات واكلت 8 ايش بيبقى؟ قال: بيبقى انا شبعان 😂"
        ]
        bot.reply_to(m, random.choice(jokes))

    @bot.message_handler(commands=['حكم'], chat_types=['group','supergroup','private'])
    def wisdom(m):
        wisdoms = [
            "من جد وجد ومن زرع حصد",
            "الصبر مفتاح الفرج",
            "لا تؤجل عمل اليوم الى الغد",
            "القناعة كنز لا يفنى"
        ]
        bot.reply_to(m, f"💡 {random.choice(wisdoms)}")
