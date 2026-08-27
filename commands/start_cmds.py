# -*- coding: utf-8 -*-
from pyrogram import Client, filters
from pyrogram.types import Message
from bot import app, main_menu

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "**• اهلا بك عزي**\n**اختر القسم اللي تريده من الازرار بالاسفل**",
        reply_markup=main_menu
    )
