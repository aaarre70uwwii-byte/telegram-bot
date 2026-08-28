import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOK")
bot = telebot.TeleBot(TOKEN)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def main_menu(page=1):
    k = InlineKeyboardMarkup(row_width=3)

    icons = ["💎", "👑", "⚡", "🔥", "🌟", "🖤"]

    k.row(
        InlineKeyboardButton(f"{icons[0]} القسم {page}-1", callback_data=f"p{page}_1"),
        InlineKeyboardButton(f"{icons[1]} القسم {page}-2", callback_data=f"p{page}_2"),
        InlineKeyboardButton(f"{icons[2]} القسم {page}-3", callback_data=f"p{page}_3"),
    )
    k.row(
        InlineKeyboardButton(f"{icons[3]} القسم {page}-4", callback_data=f"p{page}_4"),
        InlineKeyboardButton(f"{icons[4]} القسم {page}-5", callback_data=f"p{page}_5"),
        InlineKeyboardButton(f"{icons[5]} القسم {page}-6", callback_data=f"p{page}_6"),
    )

    k.row(InlineKeyboardButton("📢 تحديثات 𝐓𝐢𝐚 @eeccvu", url="https://t.me/eeccvu"))

    next_page = page + 1 if page < 6 else 1
    prev_page = page - 1 if page > 1 else 6

    k.row(
        InlineKeyboardButton("◀️ السابق", callback_data=f"page_{prev_page}"),
        InlineKeyboardButton(f"📄 {page}/6", callback_data="info"),
        InlineKeyboardButton("التالي ▶️", callback_data=f"page_{next_page}")
    )

    k.row(InlineKeyboardButton("🗑️ اخفاء القائمة", callback_data="hide"))
    return k

# امر التفعيل التلقائي + /start + /help
@bot.message_handler(commands=['start','help'], chat_types=['group','supergroup'])
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["تفعيل", "تفعيل الجروب"], chat_types=['group','supergroup'])
def group_start(m):
    if not is_admin(m.chat.id, m.from_user.id):
        return bot.reply_to(m, "❌ | عذراً، هذا الامر للادمنية فقط")

    text = f"""<b>✅ تم تفعيل الجروب بنجاح</b>
<b>✨ هلا بقائمه اوامر 𝐓𝐢𝐚 ✨</b>
<b>━━━━━━━━━━━━</b>
مرحباً بك في لوحة التحكم الملكية
اختر القسم المناسب من الازرار ادناه
<b>━━━━━━━━━━━━</b>"""
    bot.send_message(m.chat.id, text, reply_markup=main_menu(1), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    msg_id = call.message_id

    if not is_admin(chat_id, call.from_user.id):
        return bot.answer_callback_query(call.id, "❌ | للادمنية فقط", show_alert=True)

    data = call.data

    if data.startswith("p"):
        bot.answer_callback_query(call.id, "🔒 قريباً", show_alert=True)

    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        text = f"""<b>✨ هلا بقائمه اوامر 𝐓𝐢𝐚 ✨</b>
<b>━━━━━━━━━━━━</b>
مرحباً بك في لوحة التحكم الملكية
اختر القسم المناسب من الازرار ادناه
<b>━━━━━━━━━━━━</b>"""
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text,
            reply_markup=main_menu(page),
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)

    elif data == "info":
        bot.answer_callback_query(call.id, f"انت في الصفحة", show_alert=False)

    elif data == "hide":
        bot.delete_message(chat_id, msg_id)
        bot.answer_callback_query(call.id, "✅ تم اخفاء القائمة")

bot.polling(none_stop=True)
