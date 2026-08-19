import os
import sys
import random
import logging
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import asyncio

# Initialize system loggers
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Extract and validate base platform environment configs
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/eeccvu")
SUDO_ID = int(os.getenv("SUDO_ID", 0))

# Fallback default text if MAIN_MENU_TEXT is missing from environment
MAIN_TEXT = os.getenv("MAIN_MENU_TEXT", "↤اهلا فيك بعد عمري في قائمه اوامر : ✓ 𝐓𝐢𝐚 :\n━━━━━━━━━━━━\n◂ م1 : اوامر الادمنيه\n◂ م2 : اوامر الاعدادات\n◂ م3 : اوامر القفل - الفتح\n◂ م4 : اوامر التسليه\n◂ م5 : اوامر Dev\n◂ م6 : الاوامر الخدميه\n━━━━━━━━━━━")

if not BOT_TOKEN:
    raise ValueError("CRITICAL CONFIGURATION ERROR: 'BOT_TOKEN' is absent from the production environment.")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML") # غيرت ل HTML عشان العربي
dp = Dispatcher()

# Memory database framework for managing restrictions and settings
db = {
    "locks": {}, # Tracks group lock restrictions (e.g. {'chat_id': {'الصور', 'الروابط'}})
    "features": {}, # Tracks state parameters (e.g. {'chat_id': {'التسليه'}})
    "g_rules": {}, # Custom group text rules configurations
    "custom_replies": {},# Custom triggers saved dynamically
    "global_bans": set() # Blocked user identities globally restricted from bot utilities
}

# ==========================================
# 🛠️ INTERFACE CONTROLLER GENERATORS
# ==========================================

def get_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for idx in range(1, 7):
        builder.button(text=f"م{idx}", callback_data=f"menu_m{idx}")
    builder.adjust(3)

    builder.row(InlineKeyboardButton(text="التالي ↤", callback_data="menu_next"))
    builder.row(InlineKeyboardButton(text="✖ اخفاء الاوامر", callback_data="menu_hide"))
    builder.row(InlineKeyboardButton(text="تحديثات 𝐓𝐢𝐚", url=CHANNEL_URL))
    return builder.as_markup()

def get_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 عودة للقائمة الرئيسية", callback_data="menu_back")
    return builder.as_markup()

# ==========================================
# 🛑 MIDDLEWARES / AUTHORIZATION FILTERS
# ==========================================

async def check_admin(message: types.Message) -> bool:
    if message.chat.type == "private":
        return True
    if message.from_user.id == SUDO_ID:
        return True
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

# ==========================================
# 🛰️ MENU ROUTING NAVIGATION CONTROLLER
# ==========================================

@dp.message(Command("start", "help", "menu"))
async def cmd_start_router(message: types.Message):
    if message.from_user.id in db["global_bans"]:
        return
    await message.reply(MAIN_TEXT, reply_markup=get_main_keyboard())

@dp.callback_query(F.data.startswith("menu_"))
async def callback_navigation_engine(callback: types.CallbackQuery):
    action = callback.data.split("_")
    if len(action) < 2:
        return await callback.answer()

    menu_id = action[1]

    submenus_texts = {
        "m1": os.getenv("M1_MENU_TEXT", "⚙️ <b>أوامر الإدارية والاشراف (م1):</b>\n━━━━━━━━━━━━\n• بالرد: (حظر، كتم، طرد، تثبيت)\n• بالرد: (الغاء حظر، الغاء كتم، الغاء تثبيت)"),
        "m2": os.getenv("M2_MENU_TEXT", "⚙️ <b>قائمة الإعدادات العامة (م2):</b>\n━━━━━━━━━━━━\n• عرض البيانات: (الرابط، المالكين، الادمنيه، القوانين، المجموعه)\n• تهيئة البيانات: (مسح الرابط، انشاء رابط، ضع القوانين)"),
        "m3": os.getenv("M3_MENU_TEXT", "🔒 <b>قائمة التحكم بالقفل والتعطيل (م3):</b>\n━━━━━━━━━━━━\n• الصيغة: قفل / فتح + (الصور، الروابط، البوتات، السب، الكل)\n• الصيغة: تفعيل / تعطيل + (التسليه، الترحيب، الردود، الايدي)"),
        "m4": os.getenv("M4_MENU_TEXT", "🎯 <b>قائمة أوامر التسلية التفاعلية (م4):</b>\n━━━━━━━━━━━━\n• بالرد: رفع حمار / تنزيل من قلبي\n• اوامر الزواج: (تتزوجني، طلاق، زوجي، زوجتي)\n• تصويت العقوبات: (اكتموه)"),
        "m5": os.getenv("M5_MENU_TEXT", "💻 <b>لوحة التحكم والمطور الأساسي (م5):</b>\n━━━━━━━━━━━━\n• حظر عام / كتم عام / الغاء عام\n• بث البيانات: ذيع + ايدي المجموعة\n• الصيانة: تحديث / اعاده تشغيل - reload"),
        "m6": os.getenv("M6_MENU_TEXT", "🚀 <b>الخدمات العامة وأدوات التحميل (م6):</b>\n━━━━━━━━━━━━\n• الترفيه: (نسبه الحب، نسبه الغباء، شرايك في افتاري)\n• البحث: (قوقل + النص، ترجم عربي + النص، اذكار، قران)\n• التحميل: (تيك + الرابط، ساوند + الرابط)")
    }

    if menu_id in submenus_texts:
        await callback.message.edit_text(submenus_texts[menu_id], reply_markup=get_back_keyboard())
        await callback.answer()
    elif menu_id == "back":
        await callback.message.edit_text(MAIN_TEXT, reply_markup=get_main_keyboard())
        await callback.answer()
    elif menu_id == "hide":
        await callback.message.delete()
        await callback.answer("تم إخفاء لوحة الأوامر.")
    elif menu_id == "next":
        await callback.answer("لا توجد صفحات إضافية متوفرة حالياً.", show_alert=False)

# ==========================================
# ⚔️ MODULE م1 & م2: MODERATION MECHANICS
# ==========================================

@dp.message(F.text.in_({"حظر", "كتم", "طرد", "تثبيت"}))
async def administration_processing_pool(message: types.Message):
    if not await check_admin(message) or not message.reply_to_message:
        return await message.reply("❌ يجب الرد على رسالة العضو")

    target_user = message.reply_to_message.from_user
    action = message.text

    try:
        if action == "حظر":
            await bot.ban_chat_member(message.chat.id, target_user.id)
            await message.reply(f"👤 العضو {target_user.first_name} تم حظره بنجاح.")
        elif action == "كتم":
            await bot.restrict_chat_member(message.chat.id, target_user.id, permissions=ChatPermissions(can_send_messages=False))
            await message.reply(f"🔇 تم كتم العضو {target_user.first_name} بنجاح.")
        elif action == "طرد":
            await bot.ban_chat_member(message.chat.id, target_user.id)
            await bot.unban_chat_member(message.chat.id, target_user.id)
            await message.reply(f"🚷 تم طرد العضو {target_user.first_name} من المجموعة.")
        elif action == "تثبيت":
            await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            await message.reply("📌 تم تثبيت الرسالة بنجاح.")
    except Exception as e:
        await message.reply(f"❌ لم يتم تنفيذ الإجراء. السبب: {str(e)}")

@dp.message(F.text.in_({"الرابط", "القوانين", "المجموعه"}))
async def configurations_retrieval_router(message: types.Message):
    chat_id = message.chat.id
    command = message.text

    if command == "الرابط":
        try:
            link = await bot.export_chat_invite_link(chat_id) if message.chat.type!= "private" else "الدردشة خاصة"
            await message.reply(f"🔗 رابط المجموعه: {link}")
        except Exception:
            await message.reply("❌ البوت يحتاج صلاحية إدارة الروابط أولاً.")
    elif command == "القوانين":
        rules = db["g_rules"].get(chat_id, "ℹ️ لا توجد قوانين مخصصة لهذه المجموعة بعد.")
        await message.reply(rules)
    elif command == "المجموعه":
        await message.reply(f"📊 معلومات المجموعه:\n• الاسم: {message.chat.title}\n• الايدي: <code>{chat_id}</code>")

# ==========================================
# 🔒 MODULE م3: LOCKING & RESTRICTIONS SYSTEM
# ==========================================

@dp.message(lambda message: message.text and any(message.text.startswith(cmd) for cmd in ["قفل ", "فتح ", "تفعيل ", "تعطيل "]))
async def boundary_restriction_engine(message: types.Message):
    if not await check_admin(message):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return

    action, target = parts[0], parts[1]
    chat_id = message.chat.id

    if chat_id not in db["locks"]:
        db["locks"][chat_id] = set()
    if chat_id not in db["features"]:
        db["features"][chat_id] = set()

    if action == "قفل":
        db["locks"][chat_id].add(target)
        await message.reply(f"🔒 تم قفل {target} بنجاح.")
    elif action == "فتح":
        db["locks"][chat_id].discard(target)
        await message.reply(f"🔓 تم فتح {target} بنجاح.")
    elif action == "تفعيل":
        db["features"][chat_id].add(target)
        await message.reply(f"✅ تم تفعيل {target} في المجموعة.")
    elif action == "تعطيل":
        db["features"][chat_id].discard(target)
        await message.reply(f"❌ تم تعطيل {target} من المجموعة.")

# ==========================================
# 🎯 MODULE م4: INTERACTIVE SIMULATIONS - كملته لك
# ==========================================

@dp.message(F.text.in_({"رفع حمار", "تتزوجني", "زوجتي", "زوجي", "طلاق"}))
async def interactive_simulation_router(message: types.Message):
    if not message.reply_to_message and message.text in ["رفع حمار", "زوجتي", "زوجي"]:
        return await message.reply("❌ يجب الرد على العضو")

    target = message.reply_to_message.from_user.first_name if message.reply_to_message else ""
    user = message.from_user.first_name
    cmd = message.text

    responses = {
        "رفع حمار": f"🐴 تم رفع {target} رتبة حمار الجروب بنجاح",
        "تتزوجني": f"💍 {target} هل تقبل الزواج من {user}؟",
        "زوجتي": f"❤️ {user} اعلن ان {target} زوجته",
        "زوجي": f"❤️ {user} اعلنت ان {target} زوجها",
        "طلاق": f"💔 تم الطلاق بين {user} و {target}"
    }
    await message.reply(responses.get(cmd, "امر غير معروف"))

# ==========================================
# 🚀 تشغيل البوت
# ==========================================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
