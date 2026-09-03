import os
import sys
import logging
import random
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatMemberStatus
from keyboards import * # <-- هنا غيرتها من menu الى keyboards
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

    # ادارة
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

    # اعدادات
    elif text == "وضع ترحيب":
        await msg.reply_text("ارسل الترحيب الجديد")
        context.user_data["set"] = "welcome"
    elif text == "وضع رابط":
        await msg.reply_text("ارسل الرابط الجديد")
        context.user_data["set"] = "link"
    elif text == "الرابط":
        s = db.get_settings(chat_id)
        await msg.reply_text(f"الرابط: {s['link']}")

    # قفل
    elif text == "قفل الروابط":
        if not await is_admin(update, context): return
        await context.bot.set_chat_permissions(chat_id, permissions=ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_polls=True, can_send_other_messages=False, can_add_web_page_previews=False
        ))
        await msg.reply_text("✅ تم قفل الروابط")
    elif text == "فتح الروابط":
        if not await is_admin(update, context): return
        await context.bot.set_chat_permissions(chat_id, permissions=ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True
        ))
        await msg.reply_text("✅ تم فتح الروابط")

    # تسليه
    elif text.startswith("رفع بقلبي"):
        if not msg.reply_to_message: return await msg.reply_text("رد على الشخص")
        db.set_rank(chat_id, msg.reply_to_message.from_user.id, "قلبي")
        await msg.reply_text("💕 تم رفعه بقلبك")
    elif text == "رتب التسليه":
        ranks = db.get_ranks(chat_id)
        if ranks:
            txt = "\n".join([f"- {r[1]}" for r in ranks])
            await msg.reply_text(f"رتب التسليه:\n{txt}")
        else: await msg.reply_text("لا يوجد رتب")
    elif text.startswith("زواج"):
        if not msg.reply_to_message: return await msg.reply_text("رد على الشخص")
        db.add_marriage(chat_id, user.id, msg.reply_to_message.from_user.id)
        await msg.reply_text("💍 تم الزواج")
    elif text == "طلاق":
        db.remove_marriage(chat_id, user.id)
        await msg.reply_text("💔 تم الطلاق")
    elif text == "اكتموه":
        if not msg.reply_to_message: return
        votes = db.add_vote(chat_id, msg.reply_to_message.from_user.id, user.id)
        if votes >= 3:
            await context.bot.restrict_chat_member(chat_id, msg.reply_to_message.from_user.id, ChatPermissions(can_send_messages=False))
            await msg.reply_text("🔇 تم كتمه بالتصويت")

    # Dev
    elif text.startswith("رفع Dev"):
        if not await is_dev(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على المطور")
        db.add_dev(msg.reply_to_message.from_user.id)
        await msg.reply_text("✅ تم رفع مطور ثانوي")
    elif text.startswith("تنزيل Dev"):
        if not await is_dev(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على المطور")
        db.remove_dev(msg.reply_to_message.from_user.id)
        await msg.reply_text("✅ تم تنزيل مطور ثانوي")
    elif text == "قائمه الرتب العامه":
        devs = db.get_devs()
        await msg.reply_text(f"المطورين الثانويين: {len(devs)}")
    elif text.startswith("حظر عام"):
        if not await is_dev(update, context): return
        if not msg.reply_to_message: return await msg.reply_text("رد على العضو")
        db.add_gban(msg.reply_to_message.from_user.id)
        await msg.reply_text("⛔ تم حظره عام")
    elif text == "تحديث":
        if not await is_dev(update, context): return
        await msg.reply_text("✅ جاري التحديث...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif text == "غادر":
        if not await is_dev(update, context): return
        await msg.reply_text("غادرت")
        await context.bot.leave_chat(chat_id)

    # خدمية
    elif text == "نسبه الحب":
        if not msg.reply_to_message: return await msg.reply_text("رد على الشخص")
        await msg.reply_text(f"نسبه حب {msg.reply_to_message.from_user.first_name} لك: {random.randint(0,100)}% 💕")
    elif text == "نسبه الغباء":
        if not msg.reply_to_message: return await msg.reply_text("رد على الشخص")
        await msg.reply_text(f"نسبه غباء {msg.reply_to_message.from_user.first_name}: {random.randint(0,100)}% 😂")
    elif text == "تحبه":
        if not msg.reply_to_message: return await msg.reply_text("رد على الشخص")
        await msg.reply_text(random.choice(["ايوا احبه ❤️", "لا اكرهه 😒"]))
    elif text == "صيح": await msg.reply_text("صياحك وصل 😂")
    elif text == "شبيهي": await msg.reply_text("شبيهك نسبة 95% 😂")
    elif text == "شبيهتي": await msg.reply_text("شبيهتك نسبة 97% 😂")
    elif text == "اهديني": await msg.reply_text(f"اهديتك: {random.choice(['🌹', '💎', '🎁'])}")
    elif text == "اهديه":
        if msg.reply_to_message: await msg.reply_text(f"اهديت {msg.reply_to_message.from_user.first_name} 🎁")
        else: await msg.reply_text("رد على الشخص")
    elif text == "شرايك في افتاري": await msg.reply_text("افتارك 10/10 🔥")
    elif text == "افتاره":
        if msg.reply_to_message: await msg.reply_text(f"افتار {msg.reply_to_message.from_user.first_name} جميل 😍")
        else: await msg.reply_text("رد على الشخص")
    elif text == "البايو":
        if msg.reply_to_message:
            try:
                bio = await context.bot.get_chat(msg.reply_to_message.from_user.id)
                await msg.reply_text(f"بايو: {bio.bio or 'لا يوجد'}")
            except: await msg.reply_text("ما اقدر")
    elif text == "نادي المطور": await msg.reply_text(f"المطور: [{user.first_name}](tg://user?id={DEV_ID})", parse_mode="Markdown")
    elif text == "من ضافني": await msg.reply_text("تحتاج صلاحية ادمن كاملة")

    # رسائل عادية للاعدادات
    if "set" in context.user_data:
        if context.user_data["set"] == "welcome":
            db.set_welcome(chat_id, text)
            await msg.reply_text("✅ تم وضع الترحيب")
            del context.user_data["set"]
        elif context.user_data["set"] == "link":
            db.set_link(chat_id, text)
            await msg.reply_text("✅ تم وضع الرابط")
            del context.user_data["set"]

def main():
    db.init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler(["start", "menu"], show_menu, filters=GROUP_FILTER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & GROUP_FILTER, handle_buttons))
    logger.info(f"البوت شغال - المطور: {DEV_ID}")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
