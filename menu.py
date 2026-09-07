from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'private': 
        return

    text = """- اهلا بك عزيزي في قائمة الاوامر :
————————————————
◉ 1 م : اوامر الادمنيه
◉ 2 م : اوامر الاعدادات
◉ 3 م : اوامر القفل - الفتح
◉ 4 م : اوامر التسليه
◉ 5 م : Dev اوامر
◉ 6 م : الاوامر الخدميه
————————————————"""

    keyboard = [
        [InlineKeyboardButton("①", callback_data="m1"), InlineKeyboardButton("②", callback_data="m2")],
        [InlineKeyboardButton("③", callback_data="m3"), InlineKeyboardButton("④", callback_data="m4"), InlineKeyboardButton("⑤", callback_data="m5"), InlineKeyboardButton("⑥", callback_data="m6")],
        [InlineKeyboardButton("اخفاء الاوامر", callback_data="close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "close":
        await query.message.delete()
    
    # باقي الازرار فاضيه حاليا - هنبرمجها بعدين
    elif query.data in ["m1","m2","m3","m4","m5","m6"]:
        await query.answer("• القسم قريباً", show_alert=True)
