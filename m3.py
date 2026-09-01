from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

locks = {}
settings = {}

def show_lock_menu(bot, chat_id):
    text = """- اهلا بك في قائمة القفل - التعطيل :
- اوامر القفل والفتح :
━━━━━━━━━━━━
- قفل - فتح جمثون
- قفل - فتح السب
- قفل - فتح الكتابه
- قفل - فتح الصور
- قفل - فتح الفيديو
- قفل - فتح الروابط
- قفل - فتح الدردشه
- قفل - فتح الكل
- الحالة : لعرض حالة القفل
━━━━━━━━━━━━"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ الرجوع للقائمة الرئيسية", callback_data="back_to_main"))
    bot.send_message(chat_id, text, reply_markup=markup) # شلت Markdown

def is_admin(bot, chat_id, user_id):
    try: return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
    except: return False

def register_m3_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'] and m.text and is_admin(bot, m.chat.id, m.from_user.id))
    def lock_commands(m):
        chat_id = m.chat.id
        txt = m.text.strip()
        if chat_id not in locks: locks[chat_id] = {}
        if chat_id not in settings: settings[chat_id] = {}

        if txt == 'الحالة':
            msg = "📊 حالة القفل:\n"
            for k,v in locks[chat_id].items():
                msg += f"- {k}: {'🔒' if v else '🔓'}\n"
            bot.reply_to(m, msg or "كل شي مفتوح")
            return

        lock_list = ['جمثون','السب','الكتابه','الصور','الفيديو','الروابط','الدردشه','الكل']
        for item in lock_list:
            if txt == f'قفل {item}': locks[chat_id][item] = True; bot.reply_to(m, f"🔒 تم قفل {item}"); return
            elif txt == f'فتح {item}': locks[chat_id][item] = False; bot.reply_to(m, f"🔓 تم فتح {item}"); return

        # صلحت الاسم هنا
        restrict_list = ['التوجيه','الروابط','المتحركه','الصور','الفيديو']
        for item in restrict_list:
            if txt == f'قفل {item} بالتقييد': locks[chat_id][f'{item}_تقييد'] = True; bot.reply_to(m, f"🔒 تم قفل {item} بالتقييد"); return
            elif txt == f'فتح {item} بالتقييد': locks[chat_id][f'{item}_تقييد'] = False; bot.reply_to(m, f"🔓 تم فتح {item} بالتقييد"); return

    @bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'], content_types=['text','photo','video','sticker','animation','voice','document','contact','audio','new_chat_members'])
    def delete_locked(m):
        chat_id = m.chat.id
        if chat_id not in locks or is_admin(bot, chat_id, m.from_user.id): return
        try:
            if locks[chat_id].get('الكتابه') and m.content_type == 'text': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الصور') and m.content_type == 'photo': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الفيديو') and m.content_type == 'video': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الروابط') and m.text and re.search(r'(http|t.me|www\.|\.com)', m.text): bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الدردشه'): bot.delete_message(chat_id, m.message_id)
        except: pass
