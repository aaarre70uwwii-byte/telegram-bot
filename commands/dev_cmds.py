# -*- coding: utf-8 -*-
import os
import sys
from pyrogram import Client, filters # 1. ضفت Client هنا
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, ReplyKeyboardRemove
)

MAIN_DEV_ID = int(os.getenv("DEV_ID", 0))
secondary_devs = set()

def is_dev(user_id: int) -> bool:
    return user_id == MAIN_DEV_ID or user_id in secondary_devs

def get_dev_reply_keyboard():
    keyboard = [
        [KeyboardButton("إعدادات البوت ⚙️"), KeyboardButton("أوامر الإذاعة 📣"), KeyboardButton("قائمه العام 📊")],
        [KeyboardButton("تغيير المطور الاساسي 👑"), KeyboardButton("مسح المطورين 🧹")],
        [KeyboardButton("مسح اسم البوت 🗑️"), KeyboardButton("مسح قائمه العام ❌")],
        [KeyboardButton("تغيير اسم البوت ✏️"), KeyboardButton("مسح المطورين الثانويين 👥")],
        [KeyboardButton("تعطيل التواصل 📴"), KeyboardButton("جلب النسخه الاحتياطيه 📦")],
        [KeyboardButton("تفعيل التواصل 📲"), KeyboardButton("تحديث الملفات 🔄")],
        [KeyboardButton("تفعيل التفعيل التلقائي ✅"), KeyboardButton("تحديث السورس 🚀")],
        [KeyboardButton("• رجوع • الى قائمة البدء ↩️")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_m5_inline_keyboard():
    buttons = [
        [InlineKeyboardButton("أوامر التواصل 📬", callback_data="dev_contact_cmds"), InlineKeyboardButton("الحظر والكتم العام 🚫", callback_data="dev_global_punish")],
        [InlineKeyboardButton("إدارة الردود العامة 📝", callback_data="dev_replies_cmds"), InlineKeyboardButton("إعداد الكليشات ⚙️", callback_data="dev_cliches_cmds")],
        [InlineKeyboardButton("أوامر التحديث والتحكم 🔄", callback_data="dev_system_cmds")],
        [InlineKeyboardButton("إغلاق القائمة ✖️", callback_data="dev_close_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

@app.on_message(filters.text, group=5)
async def dev_master_handler(client: Client, message: Message): # 2. ضفت : Client
    cmd = message.text.strip()
    user_id = message.from_user.id if message.from_user else 0

    # الجروب
    if message.chat.type != "private":
        if cmd in ["م5", "اوامر م5"]:
            return await message.reply_text(
                text="⭐️ **قائمة أوامر المطور م5**\n\nالأزرار بالأسفل خاصة بالمطورين فقط",
                reply_markup=get_m5_inline_keyboard()
            )
        return

    # الخاص
    if not is_dev(user_id):
        return await message.reply_text("❌ هذا الكيبورد خاص بالمطور فقط")

    if cmd in ["لوحة المطور", "المطور", "مطور", "/start", "م5"]:
        return await message.reply_text("🎛️ **تم تفعيل لوحة تحكم المطور**", reply_markup=get_dev_reply_keyboard())

    if cmd == "تحديث الملفات 🔄":
        await message.reply_text("🔄 جاري تحديث ملفات البوت...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    elif cmd == "جلب النسخه الاحتياطيه 📦":
        return await message.reply_text("📦 جاري تجميع النسخة الاحتياطية...")
    elif cmd == "تفعيل البوت ⚡":
        return await message.reply_text("⚡ تم تفعيل البوت")
    elif cmd == "تعطيل البوت الخدمي 🛑":
        return await message.reply_text("🛑 تم تعطيل البوت")
    elif cmd == "• رجوع • الى قائمة البدء ↩️":
        return await message.reply_text("↩️ تم إخفاء الكيبورد", reply_markup=ReplyKeyboardRemove())
    else:
        return await message.reply_text(f"تم الضغط على: {cmd}")

@app.on_callback_query()
async def dev_inline_callback_handler(client: Client, callback_query: CallbackQuery): # 3. ضفت : Client
    user_id = callback_query.from_user.id
    data = callback_query.data
    if not data.startswith("dev_"): return
    if not is_dev(user_id): return await callback_query.answer("❌ خاص بالمطورين فقط", show_alert=True)

    try:
        if data == "dev_contact_cmds": text = "📬 **أوامر التواصل:**\n• اضف رد تواصل"
        elif data == "dev_global_punish": text = "🚫 **الحظر والكتم العام:**\n• حظر عام"
        elif data == "dev_replies_cmds": text = "📝 **إدارة الردود العامة:**\n• اضف رد عام"
        elif data == "dev_cliches_cmds": text = "⚙️ **إعداد الكليشات:**\n• وضع كليشه م1"
        elif data == "dev_system_cmds": text = "🔄 **أوامر التحديث:**\n• تحديث السورس"
        elif data == "dev_close_menu": return await callback_query.message.delete()
        else: text = "قسم غير موجود"
        
        await callback_query.message.edit_text(text, reply_markup=get_m5_inline_keyboard())
        await callback_query.answer()
    except: pass
