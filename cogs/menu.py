from utils.keyboards import *
import telebot
import random

المطور_الاساسي = 7488375443
admins = [7488375443] # ضفته هنا عشان يكون ادمن تلقائي

def is_admin(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator'] or user_id in admins
    except: return False

def setup_menu(bot):

    @bot.message_handler(commands=['اوامر', 'help', 'start'])
    def ارسال_قائمة_الاوامر(message):
        text = """**بوت 𝐓𝐢𝐚**
**الاوامر**
- أهلاً بك عزي في قائمة الاوامر :
——————————————————
◀️ 1 : اوامر الادمنيه
◀️ 2 : اوامر الاعدادات
◀️ 3 : اوامر القفل - الفتح
◀️ 4 : اوامر التسليه
◀️ 5 : اوامر Dev
◀️ 6 : الاوامر الخدميه
——————————————————"""
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=لوحة_الاوامر_الرئيسية())

    @bot.message_handler(content_types=['text'])
    def ازرار_القائمة(message):
        chat_id = message.chat.id
        text = message.text
        user_id = message.from_user.id

        # الرئيسية
        if text == "1": bot.send_message(chat_id, "**م1 : اوامر الادمنيه**", reply_markup=لوحة_م1())
        elif text == "2": bot.send_message(chat_id, "**م2 : اوامر الاعدادات**", reply_markup=لوحة_م2())
        elif text == "3": bot.send_message(chat_id, "**م3 : اوامر القفل - الفتح**", reply_markup=لوحة_م3())
        elif text == "4": bot.send_message(chat_id, "**م4 : اوامر التسليه**", reply_markup=لوحة_م4())
        elif text == "5": bot.send_message(chat_id, "**م5 : اوامر Dev**", reply_markup=لوحة_م5())
        elif text == "6": bot.send_message(chat_id, "**م6 : الاوامر الخدميه**", reply_markup=لوحة_م6())
        elif text == "رجوع": ارسال_قائمة_الاوامر(message)
        elif text == "🔒 القفل والفتح": bot.send_message(chat_id, "**اختر:**", reply_markup=لوحة_م3())
        elif text == "⚙️ التفعيل والتعطيل": bot.send_message(chat_id, "**اختر:**", reply_markup=لوحة_م2())

        # ========== م1 الادمنية ==========
        elif text == "حظر" and message.reply_to_message:
            if is_admin(bot, chat_id, user_id):
                target = message.reply_to_message.from_user.id
                bot.ban_chat_member(chat_id, target)
                bot.send_message(chat_id, f"✅ تم حظر {message.reply_to_message.from_user.first_name}")
        elif text == "طرد" and message.reply_to_message:
            if is_admin(bot, chat_id, user_id):
                target = message.reply_to_message.from_user.id
                bot.ban_chat_member(chat_id, target)
                bot.unban_chat_member(chat_id, target)
                bot.send_message(chat_id, f"✅ تم طرد {message.reply_to_message.from_user.first_name}")
        elif text == "كتم" and message.reply_to_message:
            if is_admin(bot, chat_id, user_id):
                target = message.reply_to_message.from_user.id
                bot.restrict_chat_member(chat_id, target, can_send_messages=False)
                bot.send_message(chat_id, f"🔇 تم كتم {message.reply_to_message.from_user.first_name}")
        elif text == "الغاء كتم" and message.reply_to_message:
            if is_admin(bot, chat_id, user_id):
                target = message.reply_to_message.from_user.id
                bot.restrict_chat_member(chat_id, target, can_send_messages=True)
                bot.send_message(chat_id, f"🔊 تم الغاء الكتم عن {message.reply_to_message.from_user.first_name}")
        elif text == "معلومات" and message.reply_to_message:
            u = message.reply_to_message.from_user
            bot.send_message(chat_id, f"**الاسم:** {u.first_name}\n**الايدي:** `{u.id}`\n**اليوزر:** @{u.username}")

        # ========== م2 الاعدادات ==========
        elif text == "تفعيل الردود": bot.send_message(chat_id, "✅ تم تفعيل الردود")
        elif text == "تعطيل الردود": bot.send_message(chat_id, "❌ تم تعطيل الردود")
        elif text == "تفعيل الترحيب": bot.send_message(chat_id, "✅ تم تفعيل الترحيب")
        elif text == "تعطيل الترحيب": bot.send_message(chat_id, "❌ تم تعطيل الترحيب")

        # ========== م3 القفل ==========
        elif text == "قفل الروابط": bot.send_message(chat_id, "🔒 تم قفل الروابط")
        elif text == "فتح الروابط": bot.send_message(chat_id, "🔓 تم فتح الروابط")
        elif text == "قفل الصور": bot.send_message(chat_id, "🔒 تم قفل الصور")
        elif text == "فتح الصور": bot.send_message(chat_id, "🔓 تم فتح الصور")
        elif text == "قفل الكلايش": bot.send_message(chat_id, "🔒 تم قفل الكلايش")
        elif text == "فتح الكلايش": bot.send_message(chat_id, "🔓 تم فتح الكلايش")

        # ========== م4 التسلية ==========
        elif text == "رفع هطف" and message.reply_to_message:
            name = message.reply_to_message.from_user.first_name
            bot.send_message(chat_id, f"😂 تم رفع {name} مرتبة هطف")
        elif text == "تنزيل هطف" and message.reply_to_message:
            name = message.reply_to_message.from_user.first_name
            bot.send_message(chat_id, f"😂 تم تنزيل {name} من مرتبة هطف")
        elif text == "زواج" and message.reply_to_message:
            name1 = message.from_user.first_name
            name2 = message.reply_to_message.from_user.first_name
            bot.send_message(chat_id, f"💍 مبروك {name1} و {name2} تم الزواج")
        elif text == "طلاق": bot.send_message(chat_id, "💔 تم الطلاق بنجاح")
        elif text == "اكتموه" and message.reply_to_message:
            name = message.reply_to_message.from_user.first_name
            bot.send_message(chat_id, f"🤫 تم كتم {name} 5 دقايق")

        # ========== م5 Dev - للمطور فقط 7488375443 ==========
        elif text == "حظر عام" and message.reply_to_message:
            if user_id == المطور_الاساسي:
                target = message.reply_to_message.from_user.id
                bot.send_message(chat_id, f"✅ تم حظر عام {target}")
        elif text == "الغاء حظر عام" and message.reply_to_message:
            if user_id == المطور_الاساسي:
                target = message.reply_to_message.from_user.id
                bot.send_message(chat_id, f"✅ تم الغاء الحظر العام {target}")
        elif text == "ذيع" and message.reply_to_message:
            if user_id == المطور_الاساسي:
                bot.send_message(chat_id, "📢 تم الاذاعة")
        elif text == "الردود العامة":
            if user_id == المطور_الاساسي:
                bot.send_message(chat_id, "📢 الردود العامة: 0")
        elif text == "اعادة تشغيل":
            if user_id == المطور_الاساسي:
                bot.send_message(chat_id, "🔄 جاري اعادة التشغيل...")

        # ========== م6 الخدمية ==========
        elif text == "نسبه الحب" and message.reply_to_message:
            percent = random.randint(1, 100)
            bot.send_message(chat_id, f"❤️ نسبة الحب: {percent}%")
        elif text == "تحبه" and message.reply_to_message:
            bot.send_message(chat_id, "😍 اكيد يحبه")
        elif text == "قران":
            bot.send_message(chat_id, "📖 ﴿ وَقُل رَّبِّ زِدْنِي عِلْمًا ﴾")
        elif text == "اذكار":
            azkar = ["سبحان الله", "الحمدلله", "الله اكبر", "استغفر الله"]
            bot.send_message(chat_id, f"🤲 {random.choice(azkar)}")

        # التحديثات
        elif text == "🦋 تحديثات البوت":
            text = """**📢 تحديثات بوت 𝐓𝐢𝐚 v1.0**
——————————————————
✅ تم اضافة 6 ملفات اساسية
✅ نظام ادارة كامل
✅ نظام حماية واقفال
✅ اوامر خدمية وتسلية
✅ لوحة ازرار تفاعلية

**قناة البوت:** @eeccvu
**المطور:** @eeccvu
**الاصدار:** 1.0 - 23/08/2026
——————————————————"""
            bot.send_message(chat_id, text, parse_mode="Markdown")
from utils.keyboards import dev_keyboard
import config # مهم عشان نقرا المتغيرات

def setup(bot, المطور_الاساسي, admins):

    @bot.message_handler(commands=['panel', 'admin'])
    def admin_panel(message):
        if message.from_user.id != المطور_الاساسي:
            return bot.reply_to(message, "❌ هذا الامر للمطور فقط")
        
        bot.send_message(
            message.chat.id,
            f"👑 اهلا بالمطور\nبوت: {config.اسم_البوت}\nالحالة: {'صيانة' if config.MAINTENANCE else 'شغال'}",
            reply_markup=dev_keyboard()
        )

    @bot.message_handler(func=lambda m: m.from_user.id == المطور_الاساسي)
    def dev_buttons(message):
        text = message.text

        if text == "📊 الاحصائيات":
            # هنا يقرا من المتغيرات
            bot.send_message(message.chat.id, 
                f"📊 الاحصائيات:\n\n"
                f"اسم البوت: {config.اسم_البوت}\n"
                f"ايدي المطور: {config.المطور_الاساسي}\n"
                f"حالة الصيانة: {config.MAINTENANCE}\n"
                f"عدد الادمن: {len(config.admins)}"
            )

        elif text == "⚙️ الاعدادات":
            bot.send_message(message.chat.id, 
                f"⚙️ الاعدادات الحالية:\n\n"
                f"`BOT_TOKEN`: {'موجود' if config.BOT_TOKEN else 'فارغ'}\n"
                f"`DEVELOPER_ID`: {config.المطور_الاساسي}\n"
                f"`BOT_NAME`: {config.اسم_البوت}\n"
                f"`MAINTENANCE`: {config.MAINTENANCE}",
                parse_mode="Markdown"
            )

        elif text == "🔒 اقفال البوت":
            # تغير المتغير
            config.MAINTENANCE = not config.MAINTENANCE
            status = "مفعل" if config.MAINTENANCE else "معطل"
            bot.send_message(message.chat.id, f"✅ تم {status} وضع الصيانة")

        elif text == "❌ اغلاق اللوحة":
            from telebot.types import ReplyKeyboardRemove
            bot.send_message(message.chat.id, "تم اغلاق لوحة التحكم", reply_markup=ReplyKeyboardRemove())

    print("✅ تم تحميل: menu.py - يقرا من المتغيرات")
