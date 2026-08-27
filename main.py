# -*- coding: utf-8 -*-
import os
import sys
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEV_ID = os.getenv("DEV_ID")

if not all([API_ID, API_HASH, BOT_TOKEN, DEV_ID]):
    print("❌ خطأ حرج: يرجى التأكد من إدخال المتغيرات الأربعة")
    sys.exit(1)

app = Client(
    "MyShieldBot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="commands")
)

# 1. القائمة الرئيسية بالازرار
@app.on_message(filters.command(["الاوامر", "help", "اوامري"]) | filters.regex("^(الاوامر|اوامري|help)$"))
async def main_menu_handler(client: Client, message: Message):
    menu_text = """
**- ‌‌‏أهلاً بك عزيزي في قائمة الاوامر :**
━━━━━━━━━━━━
اختر القسم اللي تشتيه من الازرار 👇
"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("م1 الادمنية 👮‍♂️", callback_data="menu_1"),
                InlineKeyboardButton("م2 الاعدادات ⚙️", callback_data="menu_2")
            ],
            [
                InlineKeyboardButton("م3 القفل والفتح 🔒", callback_data="menu_3"),
                InlineKeyboardButton("م4 التسلية 😂", callback_data="menu_4")
            ],
            [
                InlineKeyboardButton("م5 Dev 👑", callback_data="menu_5"),
                InlineKeyboardButton("م6 الخدمية 🛠️", callback_data="menu_6")
            ],
            [InlineKeyboardButton("🔄 تحديث القائمة", callback_data="main_menu")]
        ]
    )
    await message.reply_text(text=menu_text, reply_markup=keyboard)

# 2. لما يضغط على الزر
@app.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    
    if data == "menu_1":
        text = "◂ قائمة الادمنيه 👮‍♂️\n━━━━━━━━━━━━\n/ban - حظر\n/kick - طرد\n/mute - كتم"
    elif data == "menu_2":
        text = "◂ قائمة الاعدادات ⚙️\n━━━━━━━━━━━━\n/ضع_رابط - وضع رابط\n/الترحيب - تفعيل الترحيب"
    elif data == "menu_3":
        text = "◂ قائمة القفل والفتح 🔒\n━━━━━━━━━━━━\n/قفل_الصور\n/فتح_الصور"
    elif data == "menu_4":
        text = "◂ قائمة التسلية 😂\n━━━━━━━━━━━━\n/نكتة\n/صراحة"
    elif data == "menu_5":
        text = "◂ قائمة Dev 👑\n━━━━━━━━━━━━\n/اذاعة\n/المطورين"
    elif data == "menu_6":
        text = "◂ القائمة الخدمية 🛠️\n━━━━━━━━━━━━\n/ايدي\n/المعلومات"
    elif data == "main_menu":
        return await main_menu_handler(client, callback_query.message)
    else:
        text = "قائمة غير موجودة"
    
    await callback_query.message.edit_text(text, reply_markup=callback_query.message.reply_markup)
    await callback_query.answer()

@app.on_message(filters.text & filters.regex("^(تست|test)$"))
async def test_handler(client: Client, message: Message):
    await message.reply_text("✅ البوت شغال 100% ويسمعك")

print("⚡ جاري تهيئة وفحص ملفات الحماية والـ Plugins...")
app.run()
