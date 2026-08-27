# -*- coding: utf-8 -*-
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot import app, save, db

# ========== م4 الميديا ==========
@app.on_callback_query(filters.regex("menu_4"))
async def menu_media(client, query: CallbackQuery):
    text = """**• قسم الميديا م4**
    
**الاوامر المتاحه:**
`/تحميل` - تحميل من اليوتيوب
`/صوره` - البحث عن صور
`/اغنيه` - البحث عن اغاني

**اضغط رجوع للقائمة الرئيسية**"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_menu")]
    ])
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

@app.on_message(filters.command("تحميل"))
async def download_cmd(client, message: Message):
    await message.reply("**• ارسل الرابط بعد الامر**\n**مثال:** `/تحميل https://youtube.com/...`")

@app.on_message(filters.command("صوره"))
async def image_cmd(client, message: Message):
    await message.reply("**• امر البحث عن صور قريب**")

@app.on_message(filters.command("اغنيه"))
async def song_cmd(client, message: Message):
    await message.reply("**• امر البحث عن اغاني قريب**")
