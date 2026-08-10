import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

async def show_main_menu(u,c):
    keyboard = [
        [InlineKeyboardButton("1", callback_data='m1'), InlineKeyboardButton("2", callback_data='m2'), InlineKeyboardButton("3", callback_data='m3')],
        [InlineKeyboardButton("Dev اوامر", callback_data='m5'), InlineKeyboardButton("اوامر التسليه", callback_data='m4')],
        [InlineKeyboardButton("اوامر خدميه", callback_data='m6')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """- أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه
━━━━━━━━━━━━━━━━━━"""
    await u.message.reply_text(text, reply_markup=reply_markup)

async def m1(u,c): await u.message.reply_text("◂ م1 : اوامر الادمنيه\nرفع ادمن - تنزيل - حظر - طرد - كتم")
async def m2(u,c): await u.message.reply_text("◂ م2 : اوامر الاعدادات")
async def m3(u,c): await u.message.reply_text("◂ م3 : اوامر القفل")
async def m4(u,c): await u.message.reply_text("◂ م4 : اوامر التسليه")
async def m5(u,c): await u.message.reply_text("◂ م5 : اوامر Dev")
async def m6(u,c): await u.message.reply_text("◂ م6 : الاوامر الخدميه")

async def button(u,c):
    query = u.callback_query
    await query.answer()
    if query.data == 'm1': await m1(query,c)
    elif query.data == 'm2': await m2(query,c)
    elif query.data == 'm3': await m3(query,c)
    elif query.data == 'm4': await m4(query,c)
    elif query.data == 'm5': await m5(query,c)
    elif query.data == 'm6': await m6(query,c)

async def auto_reply(u,c):
    text = u.message.text
    if text == "الاوامر" or text == "اوامر":
        await show_main_menu(u,c)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", show_main_menu))
    app.add_handler(CommandHandler("m1", m1)) # غيرناها من م1 الى m1
    app.add_handler(CommandHandler("m2", m2))
    app.add_handler(CommandHandler("m3", m3))
    app.add_handler(CommandHandler("m4", m4))
    app.add_handler(CommandHandler("m5", m5))
    app.add_handler(CommandHandler("m6", m6))
    
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    
    print("Tia شغال")
    app.run_polling()

if __name__ == "__main__": main() 
