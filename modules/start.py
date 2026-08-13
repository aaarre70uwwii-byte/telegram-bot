from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import app
from database import cursor, conn

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
@app.on_message(filters.group & filters.text & filters.regex(r"^(الاوامر|الاوامر)$"))
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
        text += "🚫 حظر - بالرد\n✅ فك حظر - بالرد\n🔇 كتم - بالرد\n🔊 فك كتم - بالرد\n👢 طرد - بالرد\n⬆️ رفع مدير - بالرد\n⬇️ تنزيل - بالرد"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]])
        await query.edit_message_text(text, reply_markup=kb)

    elif data == "cmd_settings":
        text = "⚙️ اوامر الاعدادات :\n\nتفعيل - لتفعيل البوت\nضع ترحيب - رد على صورة"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]])
        await query.edit_message_text(text, reply_markup=kb)

    elif data == "cmd_locks":
        text = "🔒 اوامر القفل - الفتح :\n\nقفل الروابط\nفتح الروابط\nقفل الكل\nفتح الكل"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]])
        await query.edit_message_text(text, reply_markup=kb)

    elif data == "cmd_fun":
        text = "🎭 اوامر التسليه :\n\nهمسه @id النص - ارسال همسه سرية"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]])
        await query.edit_message_text(text, reply_markup=kb)

    elif data == "cmd_service":
        text = "🛠️ الاوامر الخدميه :\n\na - اظهار ايديك\nid - اظهار ايديك"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]])
        await query.edit_message_text(text, reply_markup=kb)

    elif data == "back":
        # يرجع للقائمة الرئيسية
        text, kb = main_menu(name)
        await query.edit_message_text(text, reply_markup=kb)
