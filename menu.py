from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'private': 
        return

    keyboard = [
        [InlineKeyboardButton("🔧 اوامر الادمنية", callback_data="m1")],
        [InlineKeyboardButton("⚙️ اوامر الاعدادات", callback_data="m2")],
        [InlineKeyboardButton("❌ اغلاق", callback_data="close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("• مرحبا بك في قائمة البوت\n• اختر القسم:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    m1_text = """*اوامر الادمنية*
- رفع مالك اساسي - بالرد
- رفع مالك - بالرد
- رفع مدير - بالرد  
- رفع ادمن - بالرد
- تنزيل - بالرد
- تنزيل الكل - بالرد
- حظر - بالرد
- طرد - بالرد
- كتم - بالرد
- تقييد - بالرد
- الغاء الحظر - بالرد
- الغاء الكتم - بالرد
- مسح الكل
- مسح 10
- مسح الردود
"""
    
    m2_text = """*اوامر الاعدادات*
- الرابط
- تعيين الرابط + الرابط
- الايدي
- معلومات - بالرد
- الرتب - بالرد
- المشرفين
- تثبيت - بالرد
- الغاء التثبيت
- اضف رد كلمة - الرد
- حذف رد كلمة
- قفل الصور / الروابط / الكيبورد
- فتح الصور / الروابط / الكيبورد
- الاعدادات
"""

    if query.data == "m1":
        await query.edit_message_text(m1_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ رجوع", callback_data="back")]
        ]))
    elif query.data == "m2":
        await query.edit_message_text(m2_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ رجوع", callback_data="back")]
        ]))
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("🔧 اوامر الادمنية", callback_data="m1")],
            [InlineKeyboardButton("⚙️ اوامر الاعدادات", callback_data="m2")],
            [InlineKeyboardButton("❌ اغلاق", callback_data="close")]
        ]
        await query.edit_message_text("• مرحبا بك في قائمة البوت\n• اختر القسم:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "close":
        await query.message.delete()
