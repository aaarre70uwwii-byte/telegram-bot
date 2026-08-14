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

# امر اظهار القائمة
@app.on_message(filters.group & filters.text & filters.regex(r"^(الاوامر)$"))
async def show_commands(_, m: Message):
    name = m.from_user.first_name
    text, kb = main_menu(name)
    await m.reply(text, reply_markup=kb)

# التعامل مع الازرار
@app.on_callback_query()
async def callback_handler(_, query: CallbackQuery):
    data = query.data
    name = query.from_user.first_name

    if data == "cmd_admin":
        text = "📜 اوامر الادمنيه :\n\n"
        text += "🚫 حظر - بالرد\n✅ فك حظر - بالرد\n🔇 كتم - بالرد
