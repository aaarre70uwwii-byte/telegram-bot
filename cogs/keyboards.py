from telebot import types

# 1. قائمة المطور الرئيسية
def main_developer_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("⚙️ إعدادات البوت", callback_data="settings_menu")
    btn2 = types.InlineKeyboardButton("📢 أوامر الإذاعة والقائمة العامة", callback_data="broadcast_menu")
    btn3 = types.InlineKeyboardButton("🛠️ قائمة المطورين والملفات", callback_data="dev_menu")
    btn4 = types.InlineKeyboardButton("➕ اضف ترحيب", callback_data="add_welcome")
    btn5 = types.InlineKeyboardButton("📢 قناه تحديثات البوت", callback_data="bot_updates_channel")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# 2. قائمة إعدادات البوت
def settings_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔄 تغيير المطور الاساسي", callback_data="change_main_dev"),
        types.InlineKeyboardButton("🗑️ مسح اسم البوت", callback_data="delete_bot_name")
    )
    markup.add(types.InlineKeyboardButton("✏️ تغيير اسم البوت", callback_data="edit_bot_name"))
    markup.add(
        types.InlineKeyboardButton("❌ تعطيل التواصل", callback_data="disable_contact"),
        types.InlineKeyboardButton("✅ تفعيل التواصل", callback_data="enable_contact")
    )
    markup.add(
        types.InlineKeyboardButton("✅ تفعيل التفعيل التلقائي", callback_data="enable_auto_active"),
        types.InlineKeyboardButton("❌ تعطيل التفعيل التلقائي", callback_data="disable_auto_active")
    )
    markup.add(
        types.InlineKeyboardButton("❌ تعطيل البوت الخدمي", callback_data="disable_service_bot"),
        types.InlineKeyboardButton("✅ تفعيل البوت الخدمي", callback_data="enable_service_bot")
    )
    markup.add(types.InlineKeyboardButton("👁️ اظهار _ اخفا • قائمة اعداد البوت", callback_data="toggle_settings_list"))
    markup.add(types.InlineKeyboardButton("• رجوع • الى قائمة البدء", callback_data="back_to_main"))
    return markup

# 3. قائمة أوامر الإذاعة
def broadcast_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("1️⃣ توجيه", callback_data="bc_forward"),
        types.InlineKeyboardButton("2️⃣ رسالة", callback_data="bc_message")
    )
    markup.add(types.InlineKeyboardButton("🔗 جلب روابط المجموعات", callback_data="get_group_links"))
    markup.add(
        types.InlineKeyboardButton("💬 الردود العامه", callback_data="public_replies"),
        types.InlineKeyboardButton("📊 الاحصائيات", callback_data="stats")
    )
    markup.add(types.InlineKeyboardButton("🗑️ مسح الردود العامه", callback_data="clear_public_replies"))
    markup.add(
        types.InlineKeyboardButton("🗑️ مسح رد عام", callback_data="delete_public_reply"),
        types.InlineKeyboardButton("➕ اضف رد عام", callback_data="add_public_reply")
    )
    markup.add(types.InlineKeyboardButton("✨ اذكار _ اقتباسات _ قران _ شعر", callback_data="islamic_content"))
    markup.add(types.InlineKeyboardButton("🎵 اطربني _ قصص _ تغيير قناة البوت", callback_data="entertainment_content"))
    markup.add(types.InlineKeyboardButton("🚀 تفعيل البوت", callback_data="activate_bot"))
    markup.add(types.InlineKeyboardButton("• رجوع • الى قائمة البدء", callback_data="back_to_main"))
    return markup

# 4. قائمة المطورين والملفات
def dev_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📋 قائمه العام", callback_data="general_list"),
        types.InlineKeyboardButton("👥 المطورين", callback_data="developers_list")
    )
    markup.add(
        types.InlineKeyboardButton("🗑️ مسح قائمه العام", callback_data="clear_general_list"),
        types.InlineKeyboardButton("🗑️ مسح المطورين", callback_data="clear_devs")
    )
    markup.add(types.InlineKeyboardButton("📥 جلب النسخه الاحتياطيه", callback_data="get_backup"))
    markup.add(types.InlineKeyboardButton("🗑️ مسح المطورين الثانويين", callback_data="clear_sub_devs"))
    markup.add(
        types.InlineKeyboardButton("📂 تحديث الملفات", callback_data="update_files"),
        types.InlineKeyboardButton("💻 تحديث السورس", callback_data="update_source")
    )
    markup.add(types.InlineKeyboardButton("👁️ اخفاء + اظهار قائمه العام", callback_data="toggle_general_list"))
    markup.add(types.InlineKeyboardButton("• رجوع • الى قائمة البدء", callback_data="back_to_main"))
    return markup
