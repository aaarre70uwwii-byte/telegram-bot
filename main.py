import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# طباعة تشخيصية
print("======== بدء تشغيل البوت ========")
print("BOT_TOK =", "موجود" if os.getenv("BOT_TOK") else "فاضي ❌")
print("API_ID =", os.getenv("API_ID"))
print("OWNER_ID =", os.getenv("OWNER_ID"))
print("==================================")

# نفس اسماء الصورة بالضبط
TOKEN = os.getenv("BOT_TOK")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_ID = os.getenv("OWNER_ID")

if not TOKEN:
    print("❌ خطأ: BOT_TOK فاضي. روح Railway > Variables")
    exit()

bot = telebot.TeleBot(TOKEN)
API_ID = int(API_ID) if API_ID else 0

def main_menu(page=1):
    k = InlineKeyboardMarkup(row_width=3)

    if page == 1:
        text = """- ‌‌‏أهلاً بك عزي في قائمة الاوامر :𝐓𝐢𝐚
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه
━━━━━━━━━━━━"""
        k.row(
            InlineKeyboardButton("1", callback_data="page_1"),
            InlineKeyboardButton("2", callback_data="page_2"),
            InlineKeyboardButton("3", callback_data="page_3"),
        )
        k.row(
            InlineKeyboardButton("4", callback_data="page_4"),
            InlineKeyboardButton("5", callback_data="page_5"),
            InlineKeyboardButton("6", callback_data="page_6"),
        )
    else:
        text = f"""<b>✨ القسم {page} :𝐓𝐢𝐚</b>
<b>━━━━━━━━━━━━</b>
قريباً سيتم اضافة اوامر القسم {page}
<b>━━━━━━━━━━━━</b>"""
        # الازرار فاضي زي ما طلبت
        k.row(
            InlineKeyboardButton("فارغ", callback_data="empty"),
            InlineKeyboardButton("فارغ", callback_data="empty"),
            InlineKeyboardButton("فارغ", callback_data="empty"),
        )
        k.row(
            InlineKeyboardButton("فارغ", callback_data="empty"),
            InlineKeyboardButton("فارغ", callback_data="empty"),
            InlineKeyboardButton("فارغ", callback_data="empty"),
        )

    k.row(InlineKeyboardButton("📢 تحديثات 𝐓𝐢𝐚", url="https://t.me/eeccvu"))

    next_page = page + 1 if page < 6 else 1
    prev_page = page - 1 if page > 1 else 6

    k.row(
        InlineKeyboardButton("◀️ السابق", callback_data=f"page_{prev_page}"),
        InlineKeyboardButton("🏠 الرئيسية", callback_data="page_1"),
        InlineKeyboardButton("التالي ▶️", callback_data=f"page_{next_page}")
    )
    k.row(InlineKeyboardButton("🗑️ اخفاء الاوامر", callback_data="hide"))
    return k, text

@bot.message_handler(commands=['start','help','اوامر'], chat_types=['group','supergroup','private'])
@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["تفعيل", "تفعيل الجروب", "الاوامر"], chat_types=['group','supergroup','private'])
def group_start(m):
    # اي حد يقدر يستخدمه
    menu, text = main_menu(1)
    if m.text and m.text.strip() in ["تفعيل", "تفعيل الجروب"]:
        text = f"<b>✅ تم تفعيل البوت بنجاح</b>\n\n{text}"
    bot.send_message(m.chat.id, text, reply_markup=menu, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    msg_id = call.message_id
    data = call.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        menu, text = main_menu(page)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=menu, parse_mode="HTML")
        bot.answer_callback_query(call.id)
    elif data == "empty":
        bot.answer_callback_query(call.id, "🔒 قريباً", show_alert=False)
    elif data == "hide":
        try:
            bot.delete_message(chat_id, msg_id)
            bot.answer_callback_query(call.id, "✅ تم اخفاء الاوامر")
        except:
            bot.answer_callback_query(call.id, "❌ لا يمكن الحذف")

print("✅ البوت اشتغل بنجاح")
bot.polling(none_stop=True)
