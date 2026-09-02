# m4.py - اوامر التسليه 100%
import json
import os
import time

DATA_FILE = "m4_data.json"
VOTE = {} # لتخزين تصويت اكتموه

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"global": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_chat_data(chat_id):
    data = load_data()
    chat_id = str(chat_id)
    if chat_id not in data:
        data[chat_id] = {"group": {}, "settings": {"التسليه": True, "زوجني": True, "اكتموه": True}}
    return data[chat_id], data

def is_admin(bot, chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except: return False

def get_m4_commands():
    text = "• اهلا بك عزي\n- اوامر التسليه :\n━━━━━━━━━━━━\n"
    text += "• رفع بقلبي : تنزيل من قلبي\n• رفع - تنزيل : خروف : الخرفان\n• رفع - تنزيل : حمار : الحمير\n"
    text += "━━━━━━━━━━━\nللقروب: \n• مسح رتب التسليه\n• رتب التسليه\n•تفعيل - تعطيل التسليه\n"
    text += "━━━━━━━━━━━━\nللعام:\n• رفع عام +اسم اختياري\n• رتب التسليه عام\n• مسح رتب التسليه عام\n"
    text += "━━━━━━━━━━━━\n• طلاق - زواج \n• زوجي - زوجتي\n• تتزوجني\n"
    text += "━━━━━━━━━━━━\n•اكتموه (تصويت)\n• تفعيل - تعطيل : اكتموه\n• تفعيل - تعطيل : زوجني"
    return text

def register_m4_handlers(bot):

    @bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
    def m4_handler(m):
        txt = m.text.strip() if m.text else ""
        chat_id = m.chat.id
        user_id = m.from_user.id
        chat_data, data = get_chat_data(chat_id)

        if not chat_data["settings"].get("التسليه", True): return

        # 1. اوامر الادمن
        if is_admin(bot, chat_id, user_id):
            if txt == "مسح رتب التسليه":
                keys_to_del = [k for k in chat_data["group"] if not k.startswith("زوج_")]
                for k in keys_to_del: chat_data["group"].pop(k)
                save_data(data)
                bot.send_message(chat_id, "✅ تم مسح كل رتب التسليه في القروب")
                return
            if txt == "رتب التسليه":
                res = "📊 رتب التسليه في القروب:\n"
                for k,v in chat_data["group"].items():
                    if not k.startswith("زوج_"): res += f"• {v} : <code>{k}</code>\n"
                bot.send_message(chat_id, res if res!= "📊 رتب التسليه في القروب:\n" else "مافي رتب", parse_mode="HTML")
                return
            if txt == "تعطيل التسليه": chat_data["settings"]["التسليه"] = False; save_data(data); bot.send_message(chat_id, "🔒 تم تعطيل اوامر التسليه"); return
            if txt == "تفعيل التسليه": chat_data["settings"]["التسليه"] = True; save_data(data); bot.send_message(chat_id, "🔓 تم تفعيل اوامر التسليه"); return
            if txt == "تعطيل اكتموه": chat_data["settings"]["اكتموه"] = False; save_data(data); bot.send_message(chat_id, "🔒 تم تعطيل اكتموه"); return
            if txt == "تفعيل اكتموه": chat_data["settings"]["اكتموه"] = True; save_data(data); bot.send_message(chat_id, "🔓 تم تفعيل اكتموه"); return
            if txt == "تعطيل زوجني": chat_data["settings"]["زوجني"] = False; save_data(data); bot.send_message(chat_id, "🔒 تم تعطيل زوجني"); return
            if txt == "تفعيل زوجني": chat_data["settings"]["زوجني"] = True; save_data(data); bot.send_message(chat_id, "🔓 تم تفعيل زوجني"); return

        # 2. اوامر الرفع بالرد
        if m.reply_to_message:
            target = m.reply_to_message.from_user
            target_id = str(target.id)
            name = target.first_name
            if txt == "رفع بقلبي": chat_data["group"][target_id] = "بقلبي"; save_data(data); bot.send_message(chat_id, f"❤️ تم رفع {name} بقلبي")
            elif txt == "تنزيل من قلبي": chat_data["group"].pop(target_id, None); save_data(data); bot.send_message(chat_id, f"💔 تم تنزيل {name} من قلبي")
            elif txt == "رفع خروف": chat_data["group"][target_id] = "خروف"; save_data(data); bot.send_message(chat_id, f"🐑 تم رفع {name} خروف")
            elif txt == "تنزيل خروف": chat_data["group"].pop(target_id, None); save_data(data); bot.send_message(chat_id, f"تم تنزيل {name} من الخرفان")
            elif txt == "رفع حمار": chat_data["group"][target_id] = "حمار"; save_data(data); bot.send_message(chat_id, f"🫏 تم رفع {name} حمار")
            elif txt == "تنزيل حمار": chat_data["group"].pop(target_id, None); save_data(data); bot.send_message(chat_id, f"تم تنزيل {name} من الحمير")

            # الزواج
            if chat_data["settings"].get("زوجني", True):
                if txt == "تتزوجني":
                    if f"زوج_{user_id}" in chat_data["group"]: bot.send_message(chat_id, "❌ انت متزوج اصلا"); return
                    if f"زوج_{target.id}" in chat_data["group"]: bot.send_message(chat_id, "❌ هو/هي متزوج/ة اصلا"); return
                    chat_data["group"][f"زوج_{user_id}"] = target.id
                    chat_data["group"][f"زوج_{target.id}"] = user_id
                    save_data(data)
                    bot.send_message(chat_id, f"💍 مبروك {m.from_user.first_name} و {name} تزوجتو")
                if txt == "طلاق":
                    chat_data["group"].pop(f"زوج_{user_id}", None)
                    chat_data["group"].pop(f"زوج_{target.id}", None)
                    save_data(data)
                    bot.send_message(chat_id, f"💔 تم الطلاق بينكم")
                if txt in ["زوجي", "زوجتي"]:
                    partner = chat_data["group"].get(f"زوج_{user_id}")
                    if partner:
                        try: p_name = bot.get_chat_member(chat_id, partner).user.first_name
                        except: p_name = "غير معروف"
                        bot.send_message(chat_id, f"زوجك/زوجتك: {p_name}")
                    else: bot.send_message(chat_id, "انت اعزب/عزباء")

        # 3. تصويت اكتموه
        if chat_data["settings"].get("اكتموه", True) and txt == "اكتموه" and m.reply_to_message:
            target_id = m.reply_to_message.from_user.id
            key = f"{chat_id}_{target_id}"
            if key not in VOTE: VOTE[key] = []
            if user_id not in VOTE[key]:
                VOTE[key].append(user_id)
                bot.send_message(chat_id, f"🗳️ تصويت {len(VOTE[key])}/3 لكتم {m.reply_to_message.from_user.first_name}")
                if len(VOTE[key]) >= 3:
                    try: bot.restrict_chat_member(chat_id, target_id, until_date=int(time.time()+3600))
                    except: pass
                    bot.send_message(chat_id, f"🔇 تم كتم {m.reply_to_message.from_user.first_name} ساعه بالتصويت")
                    VOTE.pop(key)

    # اوامر العام
    @bot.message_handler(func=lambda m: m.text and m.text.startswith("رفع عام"))
    def global_handler(m):
        data = load_data()
        user_id = str(m.from_user.id)
        name = m.text.replace("رفع عام ", "").strip() or m.from_user.first_name
        data["global"][user_id] = name
        save_data(data)
        bot.send_message(m.chat.id, f"✅ تم رفعك عام بأسم: {name}")

    @bot.message_handler(func=lambda m: m.text == "رتب التسليه عام")
    def global_list(m):
        data = load_data()
        res = "🌍 رتب التسليه العام:\n"
        for k,v in data.get("global", {}).items():
            res += f"• {v}\n"
        bot.send_message(m.chat.id, res if res!= "🌍 رتب التسليه العام:\n" else "مافي احد")

    @bot.message_handler(func=lambda m: m.text == "مسح رتب التسليه عام" and is_admin(bot, m.chat.id, m.from_user.id))
    def clear_global(m):
        data = load_data()
        data["global"] = {}
        save_data(data)
        bot.send_message(m.chat.id, "✅ تم مسح رتب التسليه العام")
