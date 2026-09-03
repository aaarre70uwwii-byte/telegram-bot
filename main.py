import os
import sys
import logging
import random
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatMemberStatus
from menu import * # <-- عدلتها هنا
import database as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
DEV_ID = 7488375443
GROUP_FILTER = filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP

async def is_admin(update, context):
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

async def is_dev(update, context):
    return update.effective_user.id == DEV_ID or update.effective_user.id in db.get_devs()

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_menu_text(), reply_markup=get_main_markup())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    msg = update.message
    user = update.effective_user

    if text == "①": await msg.reply_text("قائمة الادارة", reply_markup=get_admin_markup())
    elif text == "②": await msg.reply_text("قائمة الاعدادات", reply_markup=get_settings_markup())
    elif text == "③": await msg.reply_text(get_lock_text(), reply_markup=get_lock_markup())
    elif text == "④": await msg.reply_text(get_fun_text(), reply_markup=get_fun_markup())
    elif text == "⑤":
        if not await is_dev(update, context): return await msg.reply_text("⛔ للمطور فقط")
        await msg.reply_text(get_dev_text(), reply_markup=get_dev_markup())
    elif text == "⑥": await msg.reply_text(get_service_text(), reply_markup=get_service_markup())
    elif text == "رجوع": await msg.reply_text(get_menu_text(), reply_markup=get_main_markup())
    elif text == "اخفاء الاوامر": await msg.reply_text("تم ✅", reply_markup=remove_menu())

    # باقي الاكواد ...

def main():
    db.init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler(["start", "menu"], show_menu, filters=GROUP_FILTER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & GROUP_FILTER, handle_buttons))
    logger.info(f"البوت شغال - المطور: {DEV_ID}")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
