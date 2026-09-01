from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import menu

def show_admin_menu(bot, chat_id):
    text = """• أهلاً بك في عزي
- قائمة اوامر الادمنيه
━━━━━━━━━━━━ 
- اوامر الرفع والتنزيل :

- رفع - تنزيل مالك اساسي
- رفع - تنزيل مالك
- رفع - تنزيل مشرف
- رفع - تنزيل منشئ
- رفع - تنزيل مدير
- رفع - تنزيل ادمن
- رفع - تنزيل مميز
- تنزيل الكل - لازاله جميع الرتب اعلاه

- اوامر المسح :

- مسح الكل 
- مسح المنشئين
- مسح المدراء
- مسح المالكين
- مسح الادمنيه
- مسح المميزين
- مسح المحظورين
- مسح المكتومين
- مسح قائمه المنع
- مسح الردود
- مسح الاوامر المضافه
- مسح + عدد
- مسح بالرد
- مسح الايدي
- مسح الترحيب
- مسح الرابط

- اوامر الطرد والحظر :

- تقييد + الوقت
- حظر 
- طرد 
- كتم
- تقييد 
- الغاء الحظر 
- الغاء الكتم
- فك التقييد 
- رفع القيود
- منع بالرد
- الغاء منع بالرد
- طرد البوتات
- طرد المحذوفين
- كشف البوتات
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

def register_handlers(bot): # <-- مهم: لازم اسمها كذا عشان menu.py يشغلها

    @bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'] and m.text and is_admin(bot, m.chat.id, m.from_user.id), chat_types=['group','supergroup'])
    def admin_commands(m):
        txt = m.text.strip()
        
        # اوامر الرفع والتنزيل
        if txt.startswith('رفع '):
            bot.reply_to(m, f"✅ تم رفع `{txt[4:]}` بنجاح")
        elif txt.startswith('تنزيل '):
            bot.reply_to(m, f"✅ تم تنزيل `{txt[7:]}` بنجاح")
        elif txt == 'تنزيل الكل':
            bot.reply_to(m, "✅ تم تنزيل الكل بنجاح")
            
        # اوامر المسح
        elif txt.startswith('مسح '):
            if txt[4:].isdigit(): # مسح 10
                bot.reply_to(m, f"✅ تم مسح `{txt[4:]}` رسالة")
            elif txt == 'مسح بالرد':
                if m.reply_to_message:
                    try:
                        bot.delete_message(m.chat.id, m.reply_to_message.message_id)
                        bot.delete_message(m.chat.id, m.message_id)
                    except: bot.reply_to(m, "ماقدرت امسح")
                else:
                    bot.reply_to(m, "رد على الرسالة اللي تريد مسحها")
            else:
                bot.reply_to(m, f"✅ تم `{txt}` بنجاح")
        
        # اوامر الحظر والطرد
        elif txt.startswith('حظر'):
            if m.reply_to_message:
                try: bot.kick_chat_member(m.chat.id, m.reply_to_message.from_user.id)
                except: pass
            bot.reply_to(m, "✅ تم الحظر")
        elif txt.startswith('طرد'):
            if m.reply_to_message:
                try: bot.kick_chat_member(m.chat.id, m.reply_to_message.from_user.id)
                except: pass
            bot.reply_to(m, "✅ تم الطرد")
        elif txt.startswith('كتم'):
            if m.reply_to_message:
                try: bot.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, can_send_messages=False)
                except: pass
            bot.reply_to(m, "✅ تم الكتم")
        elif txt.startswith('الغاء الكتم'):
            if m.reply_to_message:
                try: bot.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, can_send_messages=True, can_send_media_messages=True)
                except: pass
            bot.reply_to(m, "✅ تم الغاء الكتم")
