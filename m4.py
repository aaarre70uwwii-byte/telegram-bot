from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json, os
import menu # مهم لزر الرجوع

FILE_RANKS = 'ranks.json'
FILE_GLOBAL = 'global_ranks.json'
FILE_MARRIAGE = 'marriage.json'

ranks = {}
global_ranks = {}
marriages = {}
vote_data = {}

def load_data():
    global ranks, global_ranks, marriages, vote_data
    if not os.path.exists(FILE_RANKS): json.dump({}, open(FILE_RANKS, 'w', encoding='utf-8'))
    if not os.path.exists(FILE_GLOBAL): json.dump({}, open(FILE_GLOBAL, 'w', encoding='utf-8'))
    if not os.path.exists(FILE_MARRIAGE): json.dump({}, open(FILE_MARRIAGE, 'w', encoding='utf-8'))

    ranks = json.load(open(FILE_RANKS, 'r', encoding='utf-8'))
    global_ranks = json.load(open(FILE_GLOBAL, 'r', encoding='utf-8'))
    marriages = json.load(open(FILE_MARRIAGE, 'r', encoding='utf-8'))
    vote_data = {}

def save_data():
    json.dump(ranks, open(FILE_RANKS, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(global_ranks, open(FILE_GLOBAL, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(marriages, open(FILE_MARRIAGE, 'w', encoding='utf-8'), ensure_ascii=False)

load_data()

def show_fun_menu(bot, chat_id):
    text = """• اهلا بك عزي
- اوامر التسليه :
━━━━━━━━━━━━
- رفع - تنزيل : هطف : الهطوف
- رفع - تنزيل : بثر : البثرين
- رفع - تنزيل : حمار : الحمير
- رفع بقلبي : تنزيل من قلبي
━━━━━━━━━━━━
للقروب:
- مسح رتب التسليه
- رتب التسليه
- تعطيل التسليه
━━━━━━━━━━━━
للعام:
- رفع عام +اسم
- رتب التسليه عام
- مسح رتب التسليه عام
━━━━━━━━━━━━
- طلاق - زواج
- زوجي - زوجتي
- تتزوجني
━━━━━━━━━━━━
- اكتموه (تصويت)
━━━━━━━━━━━━"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ الرجوع للقائمة الرئيسية", callback_data="back_to_main"))
    bot.send_message(chat_id, text, reply_markup=markup)

def is_admin(bot, chat_id, user_id):
    try: return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
    except: return False

def register_handlers(bot): # <-- لازم كذا مش register_m4_handlers

    rank_names = {
        'هطف': 'الهطوف', 'بثر': 'البثرين', 'حمار': 'الحمير', 'كلب': 'الكلاب',
        'كلبه': 'الكلبات', 'عتوي': 'العتوين', 'عتويه': 'العتويات', 'لحجي': 'اللحوج',
        'لحجيه': 'اللحجيات', 'خروف': 'الخرفان', 'خفيفه': 'الخفيفات', 'خفيف': 'الخفيفين'
    }

    @bot.message_handler(func=lambda m: m.chat.type in ['group','supergroup'] and m.text)
    def fun_commands(m):
        chat_id = str(m.chat.id)
        user_id = str(m.from_user.id)
        txt = m.text.strip()

        if chat_id not in ranks: ranks[chat_id] = {}
        if chat_id not in marriages: marriages[chat_id] = {}

        if ranks[chat_id].get('disabled') and not is_admin(bot, chat_id, user_id): return
        if ranks[chat_id].get('disabled_zawaj') and txt in ['زواج','طلاق','زوجي','زوجتي','تتزوجني']: return
        if ranks[chat_id].get('disabled_aktmoh') and txt == 'اكتموه': return

        for rank, plural in rank_names.items():
            if txt == f'رفع {rank}' and m.reply_to_message:
                target = str(m.reply_to_message.from_user.id)
                ranks[chat_id][target] = rank; save_data()
                bot.reply_to(m, f"✅ تم رفع {m.reply_to_message.from_user.first_name} الى {plural}"); return
            elif txt == f'تنزيل {rank}' and m.reply_to_message:
                target = str(m.reply_to_message.from_user.id)
                if ranks[chat_id].get(target) == rank: ranks[chat_id].pop(target); save_data()
                bot.reply_to(m, f"✅ تم تنزيل {m.reply_to_message.from_user.first_name} من {plural}"); return

        if txt.startswith('رفع بقلبي') and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            ranks[chat_id][target] = 'بقلبي'; save_data()
            bot.reply_to(m, f"❤️ تم رفع {m.reply_to_message.from_user.first_name} بقلبك"); return
        elif txt.startswith('تنزيل من قلبي') and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            if ranks[chat_id].get(target) == 'بقلبي': ranks[chat_id].pop(target); save_data()
            bot.reply_to(m, f"💔 تم تنزيل {m.reply_to_message.from_user.first_name} من قلبك"); return

        if is_admin(bot, chat_id, user_id):
            if txt == 'مسح رتب التسليه':
                for k in list(ranks[chat_id].keys()):
                    if k not in ['disabled','disabled_zawaj','disabled_aktmoh']: ranks[chat_id].pop(k)
                save_data(); bot.reply_to(m, "✅ تم مسح كل رتب التسليه"); return
            elif txt == 'رتب التسليه':
                msg = "📊 رتب التسليه للقروب:\n"
                for uid, r in ranks[chat_id].items():
                    if uid not in ['disabled','disabled_zawaj','disabled_aktmoh']:
                        try: name = bot.get_chat_member(chat_id, uid).user.first_name
                        except: name = uid
                        msg += f"- {name} : {r}\n"
                bot.reply_to(m, msg or "مافي رتب"); return
            elif txt == 'تعطيل التسليه': ranks[chat_id]['disabled'] = True; save_data(); bot.reply_to(m, "❌ تم تعطيل التسليه"); return
            elif txt == 'تفعيل التسليه': ranks[chat_id]['disabled'] = False; save_data(); bot.reply_to(m, "✅ تم تفعيل التسليه"); return

        if txt.startswith('رفع عام '):
            name = txt[8:]
            global_ranks[user_id] = name; save_data()
            bot.reply_to(m, f"✅ تم رفعك عام الى {name}"); return
        elif txt == 'رتب التسليه عام':
            msg = "📊 رتب التسليه العام:\n"
            for uid, r in global_ranks.items():
                try: name = bot.get_chat(user_id=uid).first_name
                except: name = uid
                msg += f"- {name} : {r}\n"
            bot.reply_to(m, msg or "مافي رتب عام"); return
        elif txt == 'مسح رتب التسليه عام':
            if user_id in global_ranks: global_ranks.pop(user_id); save_data()
            bot.reply_to(m, "✅ تم مسح رتبتك العامة"); return

        if txt == 'تتزوجني' and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            if target in marriages[chat_id].values() or user_id in marriages[chat_id]:
                bot.reply_to(m, "واحد منكم متزوج اصلا")
            else:
                marriages[chat_id][user_id] = target; save_data()
                bot.reply_to(m, f"💍 مبروك {m.from_user.first_name} و {m.reply_to_message.from_user.first_name} تزوجو")
        elif txt == 'طلاق':
            if marriages[chat_id].get(user_id):
                marriages[chat_id].pop(user_id); save_data()
                bot.reply_to(m, "💔 تم الطلاق")
            else: bot.reply_to(m, "انت مش متزوج")

        if txt == 'اكتموه' and m.reply_to_message:
            target = str(m.reply_to_message.from_user.id)
            if chat_id not in vote_data: vote_data[chat_id] = {}
            vote_data[chat_id][target] = 1
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("نعم اكتموه 1", callback_data=f"mute_yes_{target}_{chat_id}"))
            bot.send_message(chat_id, f"تصويت لكتم {m.reply_to_message.from_user.first_name}\nتحتاج 3 اصوات", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('mute_yes_'))
    def vote_mute(call):
        global vote_data
        _,_,target,chat_id = call.data.split('_')
        if chat_id not in vote_data: vote_data[chat_id] = {}
        vote_data[chat_id][target] = vote_data[chat_id].get(target, 0) + 1

        if vote_data[chat_id][target] >= 3:
            try:
                bot.restrict_chat_member(chat_id, target, can_send_messages=False)
                bot.edit_message_text("✅ تم كتم العضو بالتصويت", chat_id, call.message_id)
                vote_data[chat_id].pop(target)
            except: bot.answer_callback_query(call.id, "ماعندي صلاحية كتم")
        else:
            bot.edit_message_reply_markup(chat_id, call.message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(f"نعم اكتموه {vote_data[chat_id][target]}", callback_data=f"mute_yes_{target}_{chat_id}")
                ))
