import os
import sys
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatMemberStatus
from menu import *  # <-- الازرار من ملف menu.py
import database as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OWNER_ID = int(os.getenv("OWNER_ID", 7488375443)) # يقرا من Railway
GROUP_FILTER = filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP
PRIVATE_FILTER = filters.ChatType.PRIVATE

async def is_admin(update, context):
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def is_dev(update, context):
    return update.effective_user.id == OWNER_ID or update.effective_user.id in db.get_devs()

# ----------------- أمر /start -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    if chat_type == "private":
        if await is_dev(update, context):
            await update.message.reply_text(get_dev_text(), reply_markup=get_dev_markup())
        else:
            await update.message.reply_text("اهلا بك في 𝐓𝐢𝐚")
    else:
        await show_menu(update, context)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_menu_text(), reply_markup=get_main_markup())

# ----------------- معالجة الأزرار -----------------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    chat_id = update.effective_chat.id
    msg = update.message

    # فحص الحظر العام
    if db.is_gbanned(user_id):
        return await msg.reply_text("⛔ انت محظور عام من استخدام البوت")

    # ----------------- قائمة المطور -----------------
    if text == "⑤":
        if not await is_dev(update, context): return await msg.reply_text("⛔ للمطور فقط")
        return await msg.reply_text(get_dev_text(), reply_markup=get_dev_markup())
    
    # ازرار لوحة المطور
    if text == "رفع Dev":
        if not await is_dev(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على العضو")
        db.add_dev(msg.reply_to_message.from_user.id)
        await msg.reply_text("✅ تم رفع مطور ثانوي")
    elif text == "تنزيل Dev":
        if not await is_dev(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على العضو")
        db.remove_dev(msg.reply_to_message.from_user.id)
        await msg.reply_text("✅ تم تنزيل مطور ثانوي")
    elif text == "قائمه الرتب العامه":
        devs = db.get_devs()
        txt = "\n".join([f"- `{d}`" for d in devs]) if devs else "لا يوجد"
        await msg.reply_text(f"👑 المطورين الثانويين:\n{txt}")
    elif text == "حظر عام":
        if not await is_dev(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على العضو")
        db.add_gban(msg.reply_to_message.from_user.id)
        await msg.reply_text("⛔ تم حظره عام")
    elif text == "الغاء حظر عام":
        if not await is_dev(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على العضو")
        db.remove_gban(msg.reply_to_message.from_user.id)
        await msg.reply_text("✅ تم فك الحظر العام")
    elif text == "تحديث":
        if not await is_dev(update, context): return
        await msg.reply_text("✅ جاري التحديث...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif text == "غادر":
        if not await is_dev(update, context): return
        await msg.reply_text("غادرت")
        await context.bot.leave_chat(chat_id)

    # ----------------- القوائم الاخرى من menu.py -----------------
    elif text == "①": await msg.reply_text("قائمة الادارة", reply_markup=get_admin_markup())
    elif text == "②": await msg.reply_text("قائمة الاعدادات", reply_markup=get_settings_markup())
    elif text == "③": await msg.reply_text(get_lock_text(), reply_markup=get_lock_markup())
    elif text == "④": await msg.reply_text(get_fun_text(), reply_markup=get_fun_markup())
    elif text == "⑥": await msg.reply_text(get_service_text(), reply_markup=get_service_markup())
    elif text == "رجوع": await msg.reply_text(get_menu_text(), reply_markup=get_main_markup())
    elif text == "اخفاء الاوامر": await msg.reply_text("تم ✅", reply_markup=remove_menu())

    # ----------------- اوامر الادارة -----------------
    elif text.startswith("رفع ادمن"):
        if not await is_admin(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على العضو")
        db.set_rank(chat_id, msg.reply_to_message.from_user.id, "admin")
        await msg.reply_text("✅ تم رفعه ادمن")
    elif text.startswith("تنزيل ادمن"):
        if not await is_admin(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على العضو")
        db.set_rank(chat_id, msg.reply_to_message.from_user.id, "member")
        await msg.reply_text("✅ تم تنزيله")

    # ----------------- الاعدادات -----------------
    elif text == "وضع ترحيب":
        if not await is_admin(update, context): return
        await msg.reply_text("ارسل الترحيب الجديد")
        context.user_data["set"] = "welcome"
    elif text == "وضع رابط":
        if not await is_admin(update, context): return
        await msg.reply_text("ارسل الرابط الجديد")
        context.user_data["set"] = "link"
    elif text == "الرابط":
        s = db.get_settings(chat_id)
        await msg.reply_text(f"الرابط: {s['link']}")
    
    # ----------------- تسليه وخدمية -----------------
    elif text.startswith("زواج"):
        if not msg.reply_to_message: return await msg.reply_text("رد على الشخص")
        db.add_marriage(chat_id, user_id, msg.reply_to_message.from_user.id)
        await msg.reply_text("💍 تم الزواج")
    elif text == "طلاق":
        db.remove_marriage(chat_id, user_id)
        await msg.reply_text("💔 تم الطلاق")

    # ----------------- استقبال الاعدادات -----------------
    if "set" in context.user_data:
        if context.user_data["set"] == "welcome":
            db.set_welcome(chat_id, text)
            await msg.reply_text("✅ تم وضع الترحيب")
            del context.user_data["set"]
        elif context.user_data["set"] == "link":
            db.set_link(chat_id, text)
            await msg.reply_text("✅ تم وضع الرابط")
            del context.user_data["set"]

# ----------------- دالة الربط -----------------
def register_dev_handlers(application: Application):
    application.add_handler(CommandHandler(["start", "menu"], start, filters=GROUP_FILTER | PRIVATE_FILTER))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
