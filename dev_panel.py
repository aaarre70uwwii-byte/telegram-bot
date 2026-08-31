import threading
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

bot_status = True
comm_status = True
OWNER_ID = ""
bot_name = "Tia"
channel_link = "https://t.me/your_channel"
secondary_devs = []
groups_list = [] # بديل قائمة العام
welcome_text = "اهلا بيك في المجموعة"

def get_dev_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.row(KeyboardButton("⚙️ إعدادات البوت"), KeyboardButton("📢 أوامر الإذاعة"), KeyboardButton("📋 قائمة العام"))
    markup.row(KeyboardButton("👑 اضافة مطور"), KeyboardButton("👑 حذف مطور"), KeyboardButton("👥 المطورين الثانويين"))
    markup.row(KeyboardButton("✏️ تغيير اسم البوت"), KeyboardButton("📵 تعطيل التواصل"), KeyboardButton("📲 تفعيل التواصل"))
    markup.row(KeyboardButton("⚡ تفعيل البوت"), KeyboardButton("🔴 تعطيل البوت الخدمي"))
    markup.row(KeyboardButton("❌ اخفاء الكيبورد"))
    return markup

def register_handlers(bot, owner_id):
    global bot_status, comm_status, OWNER_ID, bot_name, channel_link, secondary_devs, groups_list, welcome_text
    OWNER_ID = str(owner_id)

    def is_owner(m):
        return str(m.from_user.id) == OWNER_ID and m.chat.type == "private"

    @bot.message_handler(commands=['المطور'])
    def dev_panel_cmd(m):
        if is_owner(m):
            user = m.from_user
            username = f"@{user.username}" if user.username else "مافي يوزر"
            نص = f"""<b>◄ لوحة تحكم المطور ►</b>
━━━━━━━━━━
<b>الاسم:</b> {user.first_name}
<b>اليوزر:</b> {username}
<b>الايدي:</b> <code>{user.id}</code>
<b>اسم البوت:</b> {bot_name}
━━━━━━━━━━
اختر من الكيبورد تحت 👇"""
            bot.send_message(m.chat.id, نص, reply_markup=get_dev_keyboard(), parse_mode="HTML")
        else:
            bot.send_message(m.chat.id, "❌ هذا الامر للمطور فقط")

    @bot.message_handler(func=lambda m: m.text == "❌ اخفاء الكيبورد" and is_owner(m))
    def hide_kb(m):
        bot.send_message(m.chat.id, "✅ تم اخفاء الكيبورد", reply_markup=ReplyKeyboardRemove())

    @bot.message_handler(func=lambda m: m.text == "⚡ تفعيل البوت" and is_owner(m))
    def enable(m):
        global bot_status; bot_status = True
        bot.send_message(m.chat.id, "✅ تم تفعيل البوت")

    @bot.message_handler(func=lambda m: m.text == "🔴 تعطيل البوت الخدمي" and is_owner(m))
    def disable(m):
        global bot_status; bot_status = False
        bot.send_message(m.chat.id, "🔴 تم تعطيل البوت")

    @bot.message_handler(func=lambda m: m.text == "👑 اضافة مطور" and is_owner(m))
    def add_dev(m):
        msg = bot.send_message(m.chat.id, "ارسل ايدي المطور الجديد")
        bot.register_next_step_handler(msg, lambda x: secondary_devs.append(x.text) or bot.send_message(x.chat.id, f"✅ تم اضافة المطور {x.text}"))

    @bot.message_handler(func=lambda m: m.text == "👥 المطورين الثانويين" and is_owner(m))
    def list_devs(m):
        txt = "👥 المطورين الثانويين:\n" + "\n".join(secondary_devs) if secondary_devs else "مافي مطورين"
        bot.send_message(m.chat.id, txt)

    @bot.message_handler(func=lambda m: m.text == "✏️ تغيير اسم البوت" and is_owner(m))
    def ask_name(m):
        msg = bot.send_message(m.chat.id, "ارسل الاسم الجديد")
        bot.register_next_step_handler(msg, lambda x: globals().update(bot_name=x.text) or bot.send_message(x.chat.id, f"✅ تم التغير الى {x.text}"))

    @bot.message_handler(func=lambda m: m.text == "📊 الاحصائيات" and is_owner(m))
    def stats(m):
        bot.send_message(m.chat.id, f"📊 الاحصائيات:\nالبوت: {'شغال' if bot_status else 'متوقف'}\nالتواصل: {'مفعل' if comm_status else 'معطل'}\nالمجموعات: {len(groups_list)}")
