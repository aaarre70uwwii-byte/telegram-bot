import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

print("======== بدء تشغيل البوت ========")
TOKEN = os.getenv("BOT_TOK")

if not TOKEN:
    print("❌ خطأ: BOT_TOK غير موجود في المتغيرات")
    exit()
else:
    print("✅ BOT_TOK تم تحميله بنجاح")

bot = telebot.TeleBot(TOKEN)

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
        k.row(InlineKeyboardButton("1", callback_data="page_1"),InlineKeyboardButton("2", callback_data="page_2"),InlineKeyboardButton("3", callback_data="page_3"))
        k.row(InlineKeyboardButton("4", callback_data="page_4"),InlineKeyboardButton("5", callback_data="page_5"),InlineKeyboardButton("6", callback_data="page_6"))
    else:
        text = f"<b>✨ القسم {page} :𝐓𝐢𝐚</b>\n<b>━━━━━━━━━━━━</b>\nقريباً\n<b>━━━━━━━━━━━━</b>"
        k.row(*[InlineKeyboardButton("-", callback_data="empty") for _ in range(3)])
        k.row(*[InlineKeyboardButton("-", callback_data="empty") for _ in range(3)])

    k.row(InlineKeyboardButton("📢 تحديثات 𝐓𝐢𝐚", url="https://t.me/eeccvu"))
    next_page = page + 1 if page < 6 else 1
    prev_page = page - 1 if page > 1 else 6
    k.row(InlineKeyboardButton("◀️ السابق", callback_data=f"page_{prev_page}"),InlineKeyboardButton("🏠 الرئيسية", callback_data="page_1"),InlineKeyboardButton("التالي ▶️", callback_data=f"page_{next_page}"))
    k.row(InlineKeyboardButton("🗑️ اخفاء الاوامر", callback_data="hide"))
    return k, text

@bot.message_handler(commands=['start','help','اوامر'], chat_types=['group','supergroup','private'])
@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["تفعيل", "تفعيل الجروب", "الاوامر"])
def group_start(m):
    menu, text = main_menu(1)
    if m.text.strip() in ["تفعيل", "تفعيل الجروب"]:
        text = f"<b>✅ تم تفعيل المجموعة بنجاح</b>\n\n{text}"
    bot.send_message(m.chat.id, text, reply_markup=menu, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("page_"):
        page = int(call.data.split("_")[1])
        menu, text = main_menu(page)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=menu, parse_mode="HTML")
    elif call.data == "empty":
        bot.answer_callback_query(call.id, "🔒 قريباً")
    elif call.data == "hide":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
    bot.answer_callback_query(call.id)

print("✅ البوت اشتغل")
bot.polling(none_stop=True)
