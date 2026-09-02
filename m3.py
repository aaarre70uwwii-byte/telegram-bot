# m3.py - النسخة النهائية 100%
import json
import os
import re
from telebot.types import ChatPermissions

DATA_FILE = "m3_data.json"
LAST_MSG = {} # لتخزين اخر رسالة للتكرار

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_chat_data(chat_id):
    data = load_data()
    chat_id = str(chat_id)
    if chat_id not in data:
        data[chat_id] = {"lock": {}, "feature": {}}
    return data[chat_id]

def set_lock(chat_id, key, status):
    data = load_data()
    chat_id = str(chat_id)
    if chat_id not in data: data[chat_id] = {"lock": {}, "feature": {}}
    data[chat_id]["lock"][key] = status
    save_data(data)

def set_feature(chat_id, key, status):
    data = load_data()
    chat_id = str(chat_id)
    if chat_id not in data: data[chat_id] = {"lock": {}, "feature": {}}
    data[chat_id]["feature"][key] = status
    save_data(data)

def get_m3_commands():
    text = "- اهلا بك في قائمة القفل - التعطيل :\n"
    text += "- اوامر القفل والفتح :\n━━━━━━━━━━━━ \n"
    text += "• قفل - فتح الروابط \n• قفل - فتح الصور \n• قفل - فتح الفيديو \n"
    text += "• قفل - فتح الملصقات \n• قفل - فتح المتحركه \n• قفل - فتح الجهات \n"
    text += "• قفل - فتح التوجيه \n• قفل - فتح التاك \n• قفل - فتح المعرفات \n"
    text += "• قفل - فتح البوتات \n• قفل - فتح الكتابه \n• قفل - فتح الدردشه \n"
    text += "• قفل - فتح السب \n• قفل - فتح جمثون \n• قفل - فتح التكرار \n"
    text += "• قفل - فتح التعديل \n• قفل - فتح الكل \n━━━━━━━━━━━━"
    return text

def is_admin(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except: return False

def register_m3_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
    def m3_handler(m):
        txt = m.text.strip() if m.text else ""
        chat_id = m.chat.id
        if not is_admin(bot, chat_id, m.from_user.id): return

        if txt == "③":
            bot.send_message(chat_id, get_m3_commands())
            return

        if txt.startswith("قفل "):
            set_lock(chat_id, txt.replace("قفل ", ""), True)
            bot.send_message(chat_id, f"🔒 تم قفل {txt.replace('قفل ', '')}")
        elif txt.startswith("فتح "):
            set_lock(chat_id, txt.replace("فتح ", ""), False)
            bot.send_message(chat_id, f"🔓 تم فتح {txt.replace('فتح ', '')}")

    @bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'sticker', 'animation', 'contact', 'forward', 'edit_message'])
    def check_locks(m):
        if is_admin(bot, m.chat.id, m.from_user.id): return
        chat_data = get_chat_data(m.chat.id)
        locks = chat_data.get("lock", {})
        text = m.text or m.caption or ""
        user_id = m.from_user.id

        delete = False

        if locks.get("الكل"): delete = True
        if locks.get("الروابط") and re.search(r'(http|t.me|telegram.me)', text): delete = True
        if locks.get("الصور") and m.content_type == 'photo': delete = True
        if locks.get("الفيديو") and m.content_type == 'video': delete = True
        if locks.get("الملصقات") and m.content_type == 'sticker': delete = True
        if locks.get("المتحركه") and m.content_type == 'animation': delete = True
        if locks.get("الجهات") and m.content_type == 'contact': delete = True
        if locks.get("التوجيه") and m.forward_from: delete = True
        if locks.get("التاك") and '@' in text: delete = True
        if locks.get("المعرفات") and '#' in text: delete = True
        if locks.get("الكتابه") and m.content_type == 'text': delete = True
        if locks.get("الدردشه") and m.content_type in ['text', 'photo', 'video', 'sticker', 'animation']: delete = True
        if locks.get("السب") and re.search(r'(كس|شرموط|قحبه|عرص)', text): delete = True
        if locks.get("جمثون") and re.search(r'(جمثون|jmathon)', text, re.IGNORECASE): delete = True
        if locks.get("التعديل") and m.content_type == 'edit_message': delete = True

        # قفل التكرار
        if locks.get("التكرار"):
            key = f"{m.chat.id}_{user_id}"
            if key in LAST_MSG and LAST_MSG[key] == text:
                delete = True
            LAST_MSG[key] = text

        if delete:
            try: bot.delete_message(m.chat.id, m.message_id)
            except: pass

    @bot.message_handler(content_types=['new_chat_members'])
    def check_bots_join(m):
        if is_admin(bot, m.chat.id, m.from_user.id): return
        chat_data = get_chat_data(m.chat.id)
        if chat_data.get("lock", {}).get("البوتات"):
            for user in m.new_chat_members:
                if user.is_bot:
                    try: bot.kick_chat_member(m.chat.id, user.id)
                    except: pass
