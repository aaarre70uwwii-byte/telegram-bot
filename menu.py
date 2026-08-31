from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 الادمنية", callback_data="menu_admin"),
        InlineKeyboardButton("⚙️ الاعدادات", callback_data="menu_settings")
    )
    markup.add(
        InlineKeyboardButton("🛡️ الحماية", callback_data="menu_protect"),
        InlineKeyboardButton("😂 التسلية", callback_data="menu_fun")
    )
    markup.add(
        InlineKeyboardButton("🔧 الخدمية", callback_data="menu_service"),
        InlineKeyboardButton("👑 المطور", callback_data="menu_dev")
    )
    markup.add(InlineKeyboardButton("❌ اغلاق", callback_data="menu_close"))
    return markup

def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="menu_back"))
    return markup

def register_handlers(bot):

    @bot.message_handler(commands=['القائمة', 'menu'], chat_types=['group','supergroup','private'])
    def show_menu(m):
        text = "◂ **قائمة بوت Tia الرئيسية**\n━━━━━━━━━━━━\nاختر القسم اللي تريده من الازرار 👇"
        bot.reply_to(m, text, parse_mode="Markdown", reply_markup=get_main_menu())

    @bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
    def menu_callback(call):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        msg_id = call.message_id
        data = call.data

        if data == "menu_back":
            bot.edit_message_text("◂ **قائمة بوت Tia الرئيسية**\n━━━━━━━━━━━━\nاختر القسم اللي تريده من الازرار 👇", 
            chat_id, msg_id, parse_mode="Markdown", reply_markup=get_main_menu())

        elif data == "menu_admin":
            text = "◂ **قائمة الادمنية**\n━━━━━━━━━━━━\n`ترقية` - رفع ادمن\n`تنزيل` - تنزيل ادمن\n`كتم` - كتم عضو\n`الغاء الكتم` - فك الكتم\n`حظر` - حظر عضو\n`الغاء الحظر` - فك الحظر\n`تقييد` - تقييد عضو"
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

        elif data == "menu_settings":
            text = "◂ **قائمة الاعدادات**\n━━━━━━━━━━━━\n`الرابط` - جلب رابط القروب\n`الترحيب` - تفعيل/تعطيل الترحيب\n`الايدي` - تفعيل/تعطيل الايدي\n`الردود` - اضافة رد تلقائي"
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

        elif data == "menu_protect":
            text = "◂ **قائمة الحماية**\n━━━━━━━━━━━━\n`قفل الروابط` - منع نشر الروابط\n`قفل الصور` - منع الصور\n`قفل الملصقات` - منع الملصقات\n`قفل الفيديو` - منع الفيديو\n`الانذار` - نظام 3 انذارات"
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

        elif data == "menu_fun":
            text = "◂ **قائمة التسلية**\n━━━━━━━━━━━━\n`نكتة` - نكتة عشوائية\n`حكم` - حكمة اليوم\n`تحويل` - تحويل ملصق لنص\n`صراحة` - لعبة صراحة"
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

        elif data == "menu_service":
            text = "◂ **قائمة الخدمية**\n━━━━━━━━━━━━\n`id` - معلوماتك\n`الوقت` - الوقت والتاريخ\n`احذف` - حذف رسالة بالرد\n`مسح_الانذارات` - مسح انذارات عضو"
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

        elif data == "menu_dev":
            text = "◂ **قائمة المطور**\n━━━━━━━━━━━━\n`المطور2` - لوحة المطور\n`رفع Dev` - بالرد\n`حظر عام` - بالرد\n`اذاعه` - بالرد\n`تحديث` - تحديث البوت"
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown", reply_markup=get_back_button())

        elif data == "menu_close":
            try: bot.delete_message(chat_id, msg_id)
            except: pass
