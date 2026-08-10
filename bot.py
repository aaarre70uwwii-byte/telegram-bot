import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
except: data = {"devs": [], "admins": {}}

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def is_admin(uid, cid): return uid in data["devs"] or uid in data["admins"].get(str(cid), [])

# ========== القائمة الرئيسية مع الازرار ==========
async def show_main_menu(u,c):
    keyboard = [
        [InlineKeyboardButton("1", callback_data='m1'), InlineKeyboardButton("2", callback_data='m2'), InlineKeyboardButton("3", callback_data='m3')],
        [InlineKeyboardButton("Dev اوامر", callback_data='m5'), InlineKeyboardButton("اوامر التسليه", callback_data='m4')],
        [InlineKeyboardButton("اوامر خدميه", callback_data='m6')],
        [InlineKeyboardButton("القفل والفتح", callback_data='m3'), InlineKeyboardButton("التفعيل والتعطيل", callback_data='m2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """- أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه
◂ م2 : اوامر الاعدادات
◂ م3 : اوامر القفل - الفتح
◂ م4 : اوامر التسليه
◂ م5 : اوامر Dev
◂ م6 : الاوامر الخدميه
━━━━━━━━━━━━━━━━━━"""
    await u.message.reply_text(text, reply_markup=reply_markup)

# ========== القوائم الفرعية ==========
async def m1(u,c):
    text = """◂ م1 : اوامر الادمنيه
━━━━━━━━━━━━
رفع ادمن - تنزيل ادمن
رفع مدير - تنزيل مدير
حظر - طرد - كتم - الغاء الكتم
مسح الكل - تنزيل الكل
━━━━━━━━━━━━"""
    await u.message.reply_text(text)

async def m2(u,c): await u.message.reply_text("◂ م2 : اوامر الاعدادات\nالرابط - القوانين - معلوماتي - ضع الترحيب")
async def m3(u,c): await u.message.reply_text("◂ م3 : اوامر القفل\nقفل الروابط - فتح الروابط - قفل الصور - فتح الصور")
async def m4(u,c): await u.message.reply_text("◂ م4 : اوامر التسليه\nنسبه الغباء - نسبه الجمال - صراحه - كرسي الاعتراف")
async def m5(u,c): await u.message.reply_text("◂ م5 : اوامر Dev\nحظر عام - اذاعه - اذاعه بالتوجيه")
async def m6(u,c): await u.message.reply_text("◂ م6 : الاوامر الخدميه\nمعلوماتي - ايدي - جلب الرابط")

# ========== الازرار ==========
async def button(u,c):
    query = u.callback_query
    await query.answer()
    if query.data == 'm1': await m1(query,c)
    elif query.data == 'm2': await m2(query,c)
    elif query.data == 'm3': await m3(query,c)
    elif query.data == 'm4': await m4(query,c)
    elif query.data == 'm5': await m5(query,c)
    elif query.data == 'm6': await m6(query,c)

# ========== الرد التلقائي ==========
async def auto_reply(u,c):
    text = u.message.text
    if text == "الاوامر" or text == "اوامر":
        await show_main_menu(u,c)

# ========== التشغيل ==========
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", show_main_menu))
    app.add_handler(CommandHandler("م1", m1))
    app.add_handler(CommandHandler("م2", m2))
    app.add_handler(CommandHandler("م3", m3))
    app.add_handler(CommandHandler("م4", m4))
    app.add_handler(CommandHandler("م5", m5))
    app.add_handler(CommandHandler("م6", m6))
    
    app.add_handler(CallbackQueryHandler(button)) # للازرار
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply)) # للكلمة
    
    print("Tia شغال")
    app.run_polling()

if __name__ == "__main__": main()
