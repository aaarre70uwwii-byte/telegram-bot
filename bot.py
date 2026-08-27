# -*- coding: utf-8 -*-
import os
import json
import sys
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ========== استدعاء كل الاوامر ==========
import commands.start_cmds      # م1 البداية
import commands.admin_cmds      # م2 الادارة
import commands.fun_cmds        # م3 التسلية
import commands.media_cmds      # م4 الميديا
import commands.dev_cmds        # م5 المطور
import commands.utility_cmds    # م6 الاوامر الخدميه

app = Client("MyShieldBot")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

DB_FILE = "data.json"
try:
    with open(DB_FILE,"r", encoding="utf-8") as f: db = json.load(f)
except: 
    db = {
        "ranks": {"admin": [], "dev": []}, 
        "texts": {}, 
        "contact_replies": {}, 
        "global_replies": {},
        "gban": [], "gmute": [], "chats": []
    }
    with open(DB_FILE,"w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

def save():
    with open(DB_FILE,"w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

# ========== القائمة الرئيسية ==========
main_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("م1", callback_data="menu_1"), InlineKeyboardButton("م2", callback_data="menu_2")],
    [InlineKeyboardButton("م3", callback_data="menu_3"), InlineKeyboardButton("م4", callback_data="menu_4")],
    [InlineKeyboardButton("م5", callback_data="menu_5"), InlineKeyboardButton("م6 الاوامر الخدميه", callback_data="menu_6")],
])

@app.on_callback_query(filters.regex("back_menu"))
async def back_to_main(client, query: CallbackQuery):
    text = """**• اهلا بك عزي**
**اختر القسم اللي تريده من الازرار بالاسفل**"""
    await query.message.edit_text(text, reply_markup=main_menu)
    await query.answer()

# ========== امر الاوامر ==========
@app.on_message(filters.command(["الاوامر","اوامر"]))
async def show_menu(client, message: Message):
    await message.reply(
        "**• اهلا بك عزي**\n**اختر القسم اللي تريده من الازرار بالاسفل**",
        reply_markup=main_menu
    )

# ========== لوحة المطور الخاصة ==========
dev_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("م5 المطور", callback_data="menu_5")],
    [InlineKeyboardButton("م6 الاوامر الخدميه", callback_data="menu_6")],
    [InlineKeyboardButton("📊 الاحصائيات", callback_data="stats")],
    [InlineKeyboardButton("🔄 تحديث", callback_data="update")],
])

@app.on_message(filters.command("مطور") & filters.private & filters.user(OWNER_ID))
async def dev_panel(client, message: Message):
    await message.reply("**• اهلا بك عزي Dev**\n**لوحة المطور الخاصة**", reply_markup=dev_keyboard)

# ========== تشغيل البوت ==========
print("✅ البوت شغال...")
app.run()
