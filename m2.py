from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def show_settings_menu(bot, chat_id):
    text = """- اهلا بك في قائمة اوامر الاعدادات :
━━━━━━━━━━━━ 

- اوامر رؤية الاعدادات :

- الرابط
- المالكين
- المالكين الاساسين
- المنشئين 
- الادمنيه
- المدراء
- المميزين
- المحظورين
- القوانين
- المكتومين 
- معلوماتي 
- الحمايه  
- الاعدادت
- المجموعه

- اوامر وضع الاعدادات :

- اضف رابط = بخاص البوت
- مسح الرابط
- انشاء رابط
- ضع الترحيب
- ضع قوانين
- ضـع رابط
- اضف امر
- تعيين الايدي
- اضف قناه (باليوزر ، بالايدي)
- حذف قناه (باليوزر ، بالايدي)

- اوامر التحميل
- تفعيل - تعطيل التحميل
- لليوتيوب
- بحث + اسم الاغنيه
- للتيك توك
- تيك + الرابط
- للساوند
- ساوند + الرابط
━━━━━━━━━━━━"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ الرجوع للقائمة الرئيسية", callback_data="back_to_main"))
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

def is_admin(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def register_m2_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'] and m.text and is_admin(bot, m.chat.id, m.from_user.id), chat_types=['group','supergroup'])
    def settings_commands(m):
        txt = m.text.strip()
        txt_low = txt.lower()
        
        # اوامر الرؤية
        if txt_low == 'الرابط': bot.reply_to(m, "الرابط: `لا يوجد رابط`")
        elif txt_low == 'المالكين': bot.reply_to(m, "قائمة المالكين: فارغة")
        elif txt_low == 'المالكين الاساسين': bot.reply_to(m, "قائمة المالكين الاساسين: فارغة")
        elif txt_low == 'المنشئين': bot.reply_to(m, "قائمة المنشئين: فارغة")
        elif txt_low == 'الادمنيه': bot.reply_to(m, "قائمة الادمنيه: فارغة")
        elif txt_low == 'المدراء': bot.reply_to(m, "قائمة المدراء: فارغة")
        elif txt_low == 'المميزين': bot.reply_to(m, "قائمة المميزين: فارغة")
        elif txt_low == 'المحظورين': bot.reply_to(m, "قائمة المحظورين: فارغة")
        elif txt_low == 'القوانين': bot.reply_to(m, "لا توجد قوانين")
        elif txt_low == 'المكتومين': bot.reply_to(m, "قائمة المكتومين: فارغة")
        elif txt_low == 'معلوماتي': bot.reply_to(m, f"اسمك: {m.from_user.first_name}\nايديك: `{m.from_user.id}`")
        elif txt_low == 'الحمايه': bot.reply_to(m, "حالة الحماية: مفعلة")
        elif txt_low == 'الاعدادت': bot.reply_to(m, "الاعدادات الافتراضية")
        elif txt_low == 'المجموعه': bot.reply_to(m, f"اسم المجموعة: {m.chat.title}")
        
        # اوامر الوضع - نخليها قبل m1 عشان ما يتعارض مع "مسح"
        elif txt_low.startswith('اضف رابط'): bot.reply_to(m, "ارسل الرابط في الخاص")
        elif txt_low == 'مسح الرابط': bot.reply_to(m, "✅ تم مسح الرابط")
        elif txt_low == 'انشاء رابط': bot.reply_to(m, "✅ تم انشاء رابط جديد")
        elif txt_low.startswith('ضع الترحيب'): bot.reply_to(m, "✅ تم وضع الترحيب")
        elif txt_low.startswith('ضع قوانين'): bot.reply_to(m, "✅ تم وضع القوانين")
        elif txt_low.startswith('ضـع رابط'): bot.reply_to(m, "✅ تم وضع الرابط")
        elif txt_low.startswith('اضف امر'): bot.reply_to(m, "ارسل: `اضف امر الكلمة`")
        elif txt_low.startswith('تعيين الايدي'): bot.reply_to(m, "✅ تم تعيين الايدي")
        elif txt_low.startswith('اضف قناه'): bot.reply_to(m, "✅ تم اضافة القناة")
        elif txt_low.startswith('حذف قناه'): bot.reply_to(m, "✅ تم حذف القناة")
        
        # اوامر التحميل
        elif txt_low == 'تفعيل التحميل': bot.reply_to(m, "✅ تم تفعيل التحميل")
        elif txt_low == 'تعطيل التحميل': bot.reply_to(m, "✅ تم تعطيل التحميل")
        elif txt_low.startswith('بحث '): bot.reply_to(m, f"جاري البحث عن: `{txt[4:]}`")
        elif txt_low.startswith('تيك '): bot.reply_to(m, "✅ جاري تحميل تيك توك...")
        elif txt_low.startswith('ساوند '): bot.reply_to(m, "✅ جاري تحميل ساوند...")
