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
- قفل - فتح الايرانيه
- قفل - فتح الكتابه
- قفل - فتح الاباحي
- قفل - فتح تعديل الميديا
- قفل - فتح التعديل
- قفل - فتح الفيديو
- قفل - فتح الصور
- قفل - فتح الملصقات
- قفل - فتح المتحركه
- قفل - فتح الدردشه
- قفل - فتح الروابط
- قفل - فتح التاك
- قفل - فتح البوتات
- قفل - فتح المعرفات
- قفل البوتات بالطرد
- قفل - فتح الكلايش
-️ قفل - فتح التكرار
- قفل - فتح التوجيه
- قفل - فتح الانلاين
- قفل - فتح الجهات
- قفل - فتح الكل
- قفل - فتح الدخول
- قفل - فتح الصوت
- قفل - فتح التوجيه بالتقييد
- قفل - فتح الروابط بالتقييد
- قفل - فتح المتحركه بالتقييد
- قفل - فتح الصور بالتقييد
- قفل - فتح الفيديو بالتقييد
*- اوامر التفعيل - التعطيل :*
- تفعيل - تعطيل ضافني
- تفعيل - تعطيل الاذكار
- تفعيل - تعطيل الثنائي
- تفعيل - تعطيل افتاري
- تفعيل - تعطيل التسليه
- تفعيل - تعطيل الكت
- تفعيل - تعطيل الترحيب
- تفعيل - تعطيل الردود
- تفعيل - تعطيل الانذار
- تفعيل - تعطيل التحذير
- تفعيل - تعطيل الايدي
- تفعيل - تعطيل الرابط
- تفعيل - تعطيل اطردني
- تفعيل - تعطيل الحظر
- تفعيل - تعطيل الرفع
- تفعيل - تعطيل التنزيل
- تفعيل - تعطيل التحويل
- تفعيل - تعطيل الحمايه
- تفعيل - تعطيل المنشن
- تفعيل - تعطيل وضع الاقتباسات
- تفعيل - تعطيل الخدميه
- تفعيل - تعطيل اليوتيوب
- تفعيل - تعطيل الايدي بالصوره
- تفعيل - تعطيل التحقق
- تفعيل - تعطيل ردود السورس
━━━━━━━━━━━━
- الحالة : لعرض حالة القفل"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ الرجوع للقائمة الرئيسية", callback_data="back_to_main"))
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

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

        # امر الحالة
        if txt == 'الحالة':
            msg = "📊 حالة القفل:\n"
            for k,v in locks[chat_id].items():
                msg += f"- {k}: {'🔒' if v else '🔓'}\n"
            bot.reply_to(m, msg or "كل شي مفتوح")
            return

        lock_list = ['جمثون','السب','الايرانيه','الكتابه','الاباحي','تعديل الميديا','التعديل','الفيديو','الصور','الملصقات','المتحركه','الدردشه','الروابط','التاك','البوتات','المعرفات','الكلايش','التكرار','التوجيه','الانلاين','الجهات','الكل','الدخول','الصوت']
        for item in lock_list:
            if txt == f'قفل {item}': locks[chat_id][item] = True; bot.reply_to(m, f"🔒 تم قفل `{item}`"); return
            elif txt == f'فتح {item}': locks[chat_id][item] = False; bot.reply_to(m, f"🔓 تم فتح `{item}`"); return

        if txt == 'قفل البوتات بالطرد': locks[chat_id]['البوتات_طرد'] = True; bot.reply_to(m, "🔒 تم قفل البوتات بالطرد")
        elif txt == 'فتح البوتات بالطرد': locks[chat_id]['البوتات_طرد'] = False; bot.reply_to(m, "🔓 تم فتح البوتات بالطرد")

        tقييد_list = ['التوجيه','الروابط','المتحركه','الصور','الفيديو']
        for item in tقييد_list:
            if txt == f'قفل {item} بالتقييد': locks[chat_id][f'{item}_تقييد'] = True; bot.reply_to(m, f"🔒 تم قفل `{item}` بالتقييد"); return
            elif txt == f'فتح {item} بالتقييد': locks[chat_id][f'{item}_تقييد'] = False; bot.reply_to(m, f"🔓 تم فتح `{item}` بالتقييد"); return

        settings_list = ['ضافني','الاذكار','الثنائي','افتاري','التسليه','الكت','الترحيب','الردود','الانذار','التحذير','الايدي','الرابط','اطردني','الحظر','الرفع','التنزيل','التحويل','الحمايه','المنشن','وضع الاقتباسات','الخدميه','اليوتيوب','الايدي بالصوره','التحقق','ردود السورس']
        for item in settings_list:
            if txt == f'تفعيل {item}': settings[chat_id][item] = True; bot.reply_to(m, f"✅ تم تفعيل `{item}`"); return
            elif txt == f'تعطيل {item}': settings[chat_id][item] = False; bot.reply_to(m, f"❌ تم تعطيل `{item}`"); return

    @bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'], content_types=['text','photo','video','sticker','animation','voice','document','contact','audio','new_chat_members'])
    def delete_locked(m):
        chat_id = m.chat.id
        if chat_id not in locks or is_admin(bot, chat_id, m.from_user.id): return
        try:
            if locks[chat_id].get('الكتابه') and m.content_type == 'text': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الصور') and m.content_type == 'photo': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الفيديو') and m.content_type == 'video': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الملصقات') and m.content_type == 'sticker': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('المتحركه') and m.content_type == 'animation': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الصوت') and m.content_type == 'voice': bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الدردشه'): bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('الروابط') and m.text and re.search(r'(http|t.me|www\.|\.com)', m.text): bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('التاك') and m.text and '@' in m.text: bot.delete_message(chat_id, m.message_id)
            if locks[chat_id].get('التوجيه') and m.forward_from: bot.delete_message(chat_id, m.message_id)
            # طرد البوتات
            if locks[chat_id].get('البوتات_طرد') and m.content_type == 'new_chat_members':
                for user in m.new_chat_members:
                    if user.is_bot: bot.kick_chat_member(chat_id, user.id)
        except: pass
