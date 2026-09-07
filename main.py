import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("TOKEN")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("menu") & filters.group)
async def menu(client, message):
    text = """- اهلا بك عزي في قائمة الاوامر :
——————————————————
• 1م : اوامر الادمنيه
• 2م : اوامر الاعدادات  
• 3م : اوامر القفل - الفتح
• 4م : اوامر التسليه
• 5م : Dev اوامر
• 6م : الاوامر الخدميه
——————————————————"""

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("①", callback_data="m1"), InlineKeyboardButton("②", callback_data="m2")],
            [InlineKeyboardButton("③", callback_data="m3"), InlineKeyboardButton("④", callback_data="m4"), 
             InlineKeyboardButton("⑤", callback_data="m5"), InlineKeyboardButton("⑥", callback_data="m6")],
            [InlineKeyboardButton("اخفاء الاوامر", callback_data="close")]
        ]
    )
    await message.reply_text(text, reply_markup=keyboard)

@app.on_callback_query()
async def button(client, callback_query):
    data = callback_query.data
    
    if data == "close":
        await callback_query.message.delete()
    else:
        await callback_query.answer("• هذا القسم قريباً...", show_alert=True)

print("البوت شغال...")
