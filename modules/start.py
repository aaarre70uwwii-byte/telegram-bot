from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

app = Client.get_client("ProtectionBot")

def main_menu(name):
    text = f"- أهلاً بك عزيزي {name} في قائمة الاوامر :\n"
    text += "____________________\n\n"
    text += "1 ◀️ اوامر الادمنيه\n"
    text += "2 ◀️ اوامر الاعدادات\n"
    text += "3 ◀️ اوامر القفل - الفتح\n"
    text += "4 ◀️ اوامر التسليه\n"
    text += "5 ◀️ الاوامر الخدميه\n"
    text += "____________________"

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1", callback_data="cmd_admin"),
            InlineKeyboardButton("2", callback_data="cmd_settings"),
            InlineKeyboardButton("3", callback_data="cmd_locks"),
        ],
        [
            InlineKeyboardButton("4", callback_data="cmd_fun"),
            InlineKeyboardButton("5", callback_data="cmd_service"),
        ]
    ])
    return text, kb

@app.on_message(filters.group & filters.text & filters.regex(r"^(الاوامر)$"))
async def show_commands(_, m: Message):
    name = m.from_user.first_name
    text, kb = main_menu(name)
    await m.reply(text, reply_markup=kb)

@app.on_callback_query()
async def callback_handler(_, query: CallbackQuery):
    data = query.data
    name = query.from_user.first_name

    if data == "cmd_admin":
        text = "📜 اوامر الادمنيه :\n\n🚫 حظر\n✅ الغاء الحظر\n🔇 كتم\n🔊 الغاء الكتم\n👢 طرد"
    elif data == "cmd_settings":  # <-- هنا في :
        text = "⚙️ اوامر الاعدادات :\n\nقفل الروابط\nقفل الصور"
    elif data == "cmd_locks":  # <-- وهنا
        text = "🔒 اوامر القفل - الفتح :\n\n/قفل\n/فتح"
    elif data == "cmd_fun":  # <-- وهنا
        text = "🎭 اوامر التسليه :\n\n/ping"
    elif data == "cmd_service":  # <-- وهنا
        text = "🛠️ الاوامر الخدميه :\n\n/id"
    elif data == "back":  # <-- وهنا
        text, kb = main_menu(name)
        await query.edit_message_text(text, reply_markup=kb)
        await query.answer()
        return
    else:
        return

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]])
    await query.edit_message_text(text, reply_markup=kb)
    await query.answer()
