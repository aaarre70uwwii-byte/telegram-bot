import os
import time
import sqlite3
import sys
import random
import uuid
import re
from deep_translator import GoogleTranslator
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
DB = "bot.db"

BOT_NAME = "𝐓𝐢𝐚"

def db(query, params=(), fetch=False):
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute(query, params)
    res = cur.fetchall() if fetch else None
    conn.commit(); conn.close()
    return res

# ===== تعديل مهم: كل جدول لحاله =====
def init_db():
    db("CREATE TABLE IF NOT EXISTS ranks (group_id INTEGER, user_id INTEGER, rank TEXT, type TEXT DEFAULT 'قروب', PRIMARY KEY(group_id, user_id, type))")
    db("CREATE TABLE IF NOT EXISTS group_settings (group_id INTEGER PRIMARY KEY, link TEXT, welcome TEXT, rules TEXT, channel TEXT)")
    db("CREATE TABLE IF NOT EXISTS lock (group_id INTEGER, type TEXT, status TEXT, PRIMARY KEY(group_id, type))")
    db("CREATE TABLE IF NOT EXISTS enable (group_id INTEGER, type TEXT, status INTEGER, PRIMARY KEY(group_id, type))")
    db("CREATE TABLE IF NOT EXISTS marriage (group_id INTEGER, user1 INTEGER, user2 INTEGER, PRIMARY KEY(group_id, user1, user2))")
    db("CREATE TABLE IF NOT EXISTS vote_aktmoh (group_id INTEGER, target_id INTEGER, voters TEXT, count INTEGER, time REAL, PRIMARY KEY(group_id, target_id))")
    db("CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)")
    db("CREATE TABLE IF NOT EXISTS gban (user_id INTEGER, reason TEXT, PRIMARY KEY(user_id))")
    db("CREATE TABLE IF NOT EXISTS gmute (user_id INTEGER, reason TEXT, PRIMARY KEY(user_id))")
    db("CREATE TABLE IF NOT EXISTS global_replies (word TEXT, reply TEXT, type TEXT, PRIMARY KEY(word))")
    db("CREATE TABLE IF NOT EXISTS multi_replies (word TEXT, reply TEXT, id INTEGER)")
    db("CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, value TEXT)")
    db("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY)")
    db("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    db("CREATE TABLE IF NOT EXISTS inline_replies (word TEXT, reply TEXT, url TEXT, PRIMARY KEY(word))")
    db("CREATE TABLE IF NOT EXISTS m6_multi_replies (word TEXT, reply TEXT)")

RANKS_ADM = {"مالك اساسي": "owner_basic", "مالك": "owner", "مشرف": "mod", "منشئ": "creator", "مدير": "manager", "ادمن": "admin", "مميز": "vip"}
RANKS_FUN = {"هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب", "كلبه": "الكلبات", "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج", "لحجيه": "اللحجيات", "خروف": "الخرفان", "خفيفه": "الخفيفات", "خفيف": "الخفيفين"}
LOCK_TYPES = ["السب", "الروابط", "البوتات", "الكتابه", "الصور", "الفيديو", "الملصقات", "الصوت", "التوجيه", "الايرانيه", "الاباحي"]
ENABLE_TYPES = ["الانذار", "التحذير", "الترحيب", "الايدي", "الرفع", "التنزيل", "الحمايه", "التسليه", "اكتموه", "زوجني", "اهمس"]

BAD_WORDS = ["كس", "قحبه", "شرموط", "منيوك", "نيك"]

def get_dev_keyboard():
    keyboard = [
        [KeyboardButton("رفع Dev"), KeyboardButton("تنزيل Dev")],
        [KeyboardButton("حظر عام"), KeyboardButton("كتم عام")],
        [KeyboardButton("الغاء حظر عام"), KeyboardButton("الغاء كتم عام")],
        [KeyboardButton("ذيع"), KeyboardButton("قائمه العام")],
        [KeyboardButton("فتح ردود MY"), KeyboardButton("قفل ردود MY")],
        [KeyboardButton("اعاده تشغيل"), KeyboardButton("اخفاء الكيبورد")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def is_admin(update, context):
    if update.effective_user.id == OWNER_ID: return True
    try: m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id); return m.status in ['creator', 'administrator']
    except: return False

async def is_dev(update, context):
    user_id = update.effective_user.id
    if user_id == OWNER_ID: return True
    res = db("SELECT 1 FROM devs WHERE user_id=?", (user_id,), True)
    return res is not None and len(res) > 0

async def get_lock_status(chat_id, lock_type):
    res = db("SELECT status FROM lock WHERE group_id=? AND type=?", (chat_id, lock_type), True)
    return res[0][0] if res else "مفتوح"

async def get_target(update): return update.message.reply_to_message.from_user.id if update.message.reply_to_message else None

async def restrict_user(context, chat_id, user_id, until=300):
    try: perms = ChatPermissions(can_send_messages=False); await context.bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=int(time.time()+until))
    except: pass

async def broadcast(context, text):
    res = db("SELECT chat_id FROM groups", (), True)
    for chat_id in [r[0] for r in res]:
        try: await context.bot.send_message(chat_id, text)
        except: pass

async def check_locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    msg = update.message; chat_id = msg.chat.id; user_id = msg.from_user.id
    if await is_admin(update, context): return

    res = db("SELECT 1 FROM gban WHERE user_id=?", (user_id,), True)
    if res: await msg.delete(); return
    res = db("SELECT 1 FROM gmute WHERE user_id=?", (user_id,), True)
    if res: await msg.delete(); return

    if await get_lock_status(chat_id, "الكتابه") == "مقفول" and msg.text:
        await msg.delete(); return
    if await get_lock_status(chat_id, "الصور") == "مقفول" and msg.photo:
        await msg.delete(); return
    if await get_lock_status(chat_id, "الفيديو") == "مقفول" and msg.video:
        await msg.delete(); return
    if await get_lock_status(chat_id, "الصوت") == "مقفول" and msg.voice:
        await msg.delete(); return
    if await get_lock_status(chat_id, "الملصقات") == "مقفول" and msg.sticker:
        await msg.delete(); return
    if await get_lock_status(chat_id, "التوجيه") == "مقفول" and msg.forward_date:
        await msg.delete(); return
    if await get_lock_status(chat_id, "الروابط") == "مقفول" and msg.text:
        if re.search(r'(https?://|t.me/|@)', msg.text):
            await msg.delete(); return
    if await get_lock_status(chat_id, "البوتات") == "مقفول" and msg.new_chat_members:
        for member in msg.new_chat_members:
            if member.is_bot:
                await msg.delete(); await context.bot.ban_chat_member(chat_id, member.id)
    if await get_lock_status(chat_id, "السب") == "مقفول" and msg.text:
        text = msg.text.lower()
        if any(word in text for word in BAD_WORDS):
            await msg.delete()
            res = db("SELECT status FROM enable WHERE group_id=? AND type=?", (chat_id, "التحذير"), True)
            if res and res[0][0] == 1:
                await msg.reply_text(f"• {msg.from_user.first_name} ممنوع السب")

async def handle_m1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip(); chat = update.effective_chat; user_id = update.effective_user.id
    if chat.type not in ['group', 'supergroup'] or not text.startswith(("رفع ", "تنزيل ")): return
    if not await is_admin(update, context): return
    db("INSERT OR IGNORE INTO groups VALUES (?)", (chat.id,)); db("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    target = await get_target(update)
    for name, key in RANKS_ADM.items():
        if text == f"رفع {name}" and target: db("INSERT OR IGNORE INTO ranks VALUES (?,?,?,?)", (chat.id, target, key, "قروب")); return await update.message.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم رفع العضو الى {name}")
        if text == f"تنزيل {name}" and target: db("DELETE FROM ranks WHERE group_id=? AND user_id=? AND rank=? AND type=?", (chat.id, target, key, "قروب")); return await update.message.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم تنزيل العضو من {name}")

async def handle_m2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip(); chat = update.effective_chat
    if chat.type not in ['group', 'supergroup'] or not await is_admin(update, context): return
    if text == "الرابط": res = db("SELECT link FROM group_settings WHERE group_id=?", (chat.id,), True); link = res[0][0] if res else None; return await update.message.reply_text(f"• أهلاً بك في {BOT_NAME}\nالرابط: {link if link else 'لا يوجد'}")

async def handle_m3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    text = update.message.text.strip() if update.message.text else ""; chat = update.effective_chat; is_adm = await is_admin(update, context)
    if text == "قائمة القفل":
        res = db("SELECT type, status FROM lock WHERE group_id=?", (chat.id,), True); locks = {r[0]:r[1] for r in res} if res else {}
        msg_text = f"• أهلاً بك في {BOT_NAME}\n- حالة القفل:\n━━━━━━━━━━━━\n"
        for t in LOCK_TYPES: status = locks.get(t, "مفتوح"); emoji = "🔒" if status!= "مفتوح" else "🔓"; msg_text += f"{emoji} {t}: {status}\n"
        return await update.message.reply_text(msg_text)
    if chat.type not in ['group', 'supergroup']: return
    if not is_adm: return
    for t in LOCK_TYPES:
        if text == f"قفل {t}": db("INSERT OR REPLACE INTO lock VALUES (?,?,?)", (chat.id, t, "مقفول")); return await update.message.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم قفل {t}")
        if text == f"فتح {t}": db("INSERT OR REPLACE INTO lock VALUES (?,?,?)", (chat.id, t, "مفتوح")); return await update.message.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم فتح {t}")
    for t in ENABLE_TYPES:
        if text == f"تفعيل {t}": db("INSERT OR REPLACE INTO enable VALUES (?,?,?)", (chat.id, t, 1)); return await update.message.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم تفعيل {t}")
        if text == f"تعطيل {t}": db("INSERT OR REPLACE INTO enable VALUES (?,?,?)", (chat.id, t, 0)); return await update.message.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم تعطيل {t}")

async def handle_m4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    msg = update.message; text = msg.text.strip(); chat_id = msg.chat.id; user_id = msg.from_user.id; name = msg.from_user.first_name; is_adm = await is_admin(update, context)
    res = db("SELECT status FROM enable WHERE group_id=? AND type=?", (chat_id, "التسليه"), True)
    if chat_id < 0 and res and res[0][0] == 0: return
    for r, p in RANKS_FUN.items():
        if text == f"رفع {r}":
            if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
            target = msg.reply_to_message.from_user.id
            db("INSERT OR REPLACE INTO ranks VALUES (?,?,?,?)", (chat_id, target, p, "قروب"))
            return await msg.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم رفع {msg.reply_to_message.from_user.first_name} الى {p}")
        if text == f"تنزيل {r}":
            if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
            target = msg.reply_to_message.from_user.id
            db("DELETE FROM ranks WHERE group_id=? AND user_id=? AND type=?", (chat_id, target, "قروب"))
            return await msg.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم تنزيل {msg.reply_to_message.from_user.first_name} من {p}")
    if text == "رفع بقلبي":
        if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
        target = msg.reply_to_message.from_user.id; db("INSERT OR REPLACE INTO ranks VALUES (?,?,?,?)", (chat_id, target, "في قلبي", "قروب"))
        return await msg.reply_text(f"• أهلاً بك في {BOT_NAME}\n{msg.reply_to_message.from_user.first_name} صار بقلبك ❤️")
    if text == "تنزيل من قلبي":
        if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
        target = msg.reply_to_message.from_user.id; db("DELETE FROM ranks WHERE group_id=? AND user_id=? AND rank=?", (chat_id, target, "في قلبي"))
        return await msg.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم تنزيل {msg.reply_to_message.from_user.first_name} من قلبك")
    if is_adm:
        if text == "مسح رتب التسليه": db("DELETE FROM ranks WHERE group_id=? AND type=?", (chat_id, "قروب")); return await msg.reply_text(f"• أهلاً بك في {BOT_NAME}\nتم مسح كل رتب التسليه")
        if text == "رتب التسليه":
            ranks = db("SELECT rank FROM ranks WHERE group_id=? AND type=?", (chat_id, "قروب"), True)
            msg_text = "• رتب التسليه:\n━━━━━━━━━━━━\n" + "\n".join([f"- {r[0]}" for r in ranks]) if ranks else "• مافي رتب"
            return await msg.reply_text(msg_text)
    res = db("SELECT status FROM enable WHERE group_id=? AND type=?", (chat_id, "زوجني"), True)
    if res and res[0][0] == 1:
        if text == "تتزوجني" and msg.reply_to_message:
            u2 = msg.reply_to_message.from_user.id
            if u2 == user_id: return await msg.reply_text("• ماتقدر تتزوج نفسك")
            res = db("SELECT * FROM marriage WHERE group_id=? AND user1=?", (chat_id, user_id), True)
            if res: return await msg.reply_text("• انت متزوج")
            db("INSERT OR IGNORE INTO marriage VALUES (?,?,?)", (chat_id, user_id, u2)); db("INSERT OR IGNORE INTO marriage VALUES (?,?,?)", (chat_id, u2, user_id))
            return await msg.reply_text(f"💍 مبروك {name} و {msg.reply_to_message.from_user.first_name} تم عقد القران")
        if text == "طلاق" and msg.reply_to_message:
            u2 = msg.reply_to_message.from_user.id; db("DELETE FROM marriage WHERE group_id=? AND ((user1=? AND user2=?) OR (user1=? AND user2=?))", (chat_id, user_id, u2, u2, user_id))
            return await msg.reply_text("• تم الطلاق بنجاح")
        if text == "زوجي": res = db("SELECT user2 FROM marriage WHERE group_id=? AND user1=?", (chat_id, user_id), True); return await msg.reply_text(f"• عندك زوج" if res else "• ماعندك زوج")
        if text == "زوجتي": res = db("SELECT user2 FROM marriage WHERE group_id=? AND user1=?", (chat_id, user_id), True); return await msg.reply_text(f"• عندك زوجة" if res else "• ماعندك زوجة")
    res = db("SELECT status FROM enable WHERE group_id=? AND type=?", (chat_id, "اكتموه"), True)
    if res and res[0][0] == 1 and text == "اكتموه" and msg.reply_to_message:
        target = msg.reply_to_message.from_user.id
        if target == user_id: return await msg.reply_text("• ماتقدر تكتم نفسك")
        res = db("SELECT count, voters, time FROM vote_aktmoh WHERE group_id=? AND target_id=?", (chat_id, target), True)
        now = time.time()
        if res and now - res[0][2] < 60:
            voters = res[0][1].split(",") if res[0][1] else []
            if str(user_id) in voters: return await msg.reply_text("• انت صوتت خلاص")
            voters.append(str(user_id)); new_count = res[0][0] + 1
            db("UPDATE vote_aktmoh SET count=?, voters=?, time=? WHERE group_id=? AND target_id=?", (new_count, ",".join(voters), now, chat_id, target))
        else: new_count = 1; db("INSERT OR REPLACE INTO vote_aktmoh VALUES (?,?,?,?,?)", (chat_id, target, str(user_id), 1, now))
        if new_count >= 3: await restrict_user(context, chat_id, target, 600); db("DELETE FROM vote_aktmoh WHERE group_id=? AND target_id=?", (chat_id, target)); return await msg.reply_text(f"• تم كتم {msg.reply_to_message.from_user.first_name} 10 دقايق بالتصويت")
        else: return await msg.reply_text(f"• تصويت اكتموه: {new_count}/3 على {msg.reply_to_message.from_user.first_name}")

async def handle_m5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    msg = update.message; text = msg.text.strip() if msg.text else ""; chat_id = msg.chat.id; user_id = msg.from_user.id; is_dev_user = await is_dev(update, context)
    if chat_id < 0: db("INSERT OR IGNORE INTO groups VALUES (?)", (chat_id,))
    if chat_id > 0 and is_dev_user:
        if text == "اظهار الكيبورد": return await msg.reply_text(f"• تم اظهار كيبورد {BOT_NAME}", reply_markup=get_dev_keyboard())
        if text == "اخفاء الكيبورد": return await msg.reply_text("• تم اخفاء الكيبورد", reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True))
    res = db("SELECT value FROM bot_settings WHERE key=?", ("my_replies",), True)
    if res and res[0][0] == "مفتوح":
        res = db("SELECT reply FROM global_replies WHERE word=?", (text,), True)
        if res: return await msg.reply_text(res[0][0])
        res = db("SELECT reply FROM multi_replies WHERE word=?", (text,), True)
        if res: return await msg.reply_text(random.choice(res)[0])
    if not is_dev_user: return
    if text == "اوامر المطور" and chat_id > 0: return await msg.reply_text(f"• اهلا بك عزي {BOT_NAME}\nاكتب اي امر من الكيبورد", reply_markup=get_dev_keyboard())
    if text == "رفع Dev":
        if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
        target = msg.reply_to_message.from_user.id; db("INSERT OR IGNORE INTO devs VALUES (?)", (target,)); return await msg.reply_text("• تم رفعه مطور ثانوي")
    if text == "تنزيل Dev":
        if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
        target = msg.reply_to_message.from_user.id; db("DELETE FROM devs WHERE user_id=?", (target,)); return await msg.reply_text("• تم تنزيله من المطورين")
    if text == "حظر عام":
        if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
        target = msg.reply_to_message.from_user.id; db("INSERT OR REPLACE INTO gban VALUES (?,?)", (target, "بدون سبب")); return await msg.reply_text("• تم حظره عام")
    if text == "كتم عام":
        if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
        target = msg.reply_to_message.from_user.id; db("INSERT OR REPLACE INTO gmute VALUES (?,?)", (target, "بدون سبب")); return await msg.reply_text("• تم كتمه عام")
    if text == "الغاء حظر عام":
        if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
        target = msg.reply_to_message.from_user.id; db("DELETE FROM gban WHERE user_id=?", (target,)); return await msg.reply_text("• تم الغاء حظره العام")
    if text == "الغاء كتم عام":
        if not msg.reply_to_message: return await msg.reply_text("• رد على الشخص")
        target = msg.reply_to_message.from_user.id; db("DELETE FROM gmute WHERE user_id=?", (target,)); return await msg.reply_text("• تم الغاء كتمه العام")
    if text.startswith("ذيع "): await broadcast(context, f"📢 اذاعه {BOT_NAME}:\n{text.replace('ذيع ', '')}"); return await msg.reply_text("• تم الاذاعه")
    if text == "ذيع": await msg.reply_text("• ارسل النص بعد كلمة ذيع")
    if text == "قائمه العام":
        gb = db("SELECT COUNT(*) FROM gban", (), True)[0][0]; gm = db("SELECT COUNT(*) FROM gmute", (), True)[0][0]
        return await msg.reply_text(f"• المحظورين عام: {gb}\n• المكتومين عام: {gm}")
    if text == "فتح ردود MY": db("INSERT OR REPLACE INTO bot_settings VALUES (?,?)", ("my_replies", "مفتوح")); return await msg.reply_text("• تم فتح ردود MY")
    if text == "قفل ردود MY": db("INSERT OR REPLACE INTO bot_settings VALUES (?,?)", ("my_replies", "مقفول")); return await msg.reply_text("• تم قفل ردود MY")
    if text == "اعاده تشغيل": await msg.reply_text(f"• جاري اعادة تشغيل {BOT_NAME}..."); os.execl(sys.executable, sys.executable, *sys.argv)

async def handle_m6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    msg = update.message; text = msg.text.strip() if msg.text else ""; user_id = msg.from_user.id; chat_id = msg.chat.id
    res = db("SELECT status FROM enable WHERE group_id=? AND type=?", (chat_id, "اهمس"), True)
    is_enabled = True if not res else res[0][0] == 1
    if text.startswith("اهمس") and msg.reply_to_message:
        if not is_enabled: return
        target = msg.reply_to_message.from_user
        sender = msg.from_user
        msg_text = text.replace("اهمس ", "").strip()
        if not msg_text: return await msg.reply_text("• الصيغه: اهمس + النص بالرد")
        whisper_id = str(uuid.uuid4())
        context.bot_data[whisper_id] = {"from_id": sender.id, "from_name": sender.first_name, "to_id": target.id, "text": msg_text}
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("💌 اظهار الهمسه", callback_data=f"whisper_{whisper_id}")]])
        return await msg.reply_text(f"• تمت همسه لـ {target.first_name}\n• اضغط الزر لعرضها", reply_markup=keyboard)
    res = db("SELECT reply, url FROM inline_replies WHERE word=?", (text,), True)
    if res: kb = InlineKeyboardMarkup([[InlineKeyboardButton("الرابط", url=res[0][1])]]) if res[0][1] else None; return await msg.reply_text(res[0][0], reply_markup=kb)
    res = db("SELECT reply FROM m6_multi_replies WHERE word=?", (text,), True)
    if res: return await msg.reply_text(random.choice(res)[0])
    if text == "الاوامر m6":
        txt = f"• اهلا بك في {BOT_NAME}\n━━━━━━━━━━━━\n• نسبه الحب\n• نسبه الغباء - بالرد\n• تحبه - بالرد\n• اهمس + النص - بالرد\n• زخرف + اسمك\n• ترجم عربي + الكلام\n• ترجم انقليزي + الكلام"
        return await msg.reply_text(txt)
    if text == "نسبه الحب": return await msg.reply_text(f"• نسبة الحب: {random.randint(1,100)}% ❤️")
    if text.startswith("نسبه الغباء") and msg.reply_to_message: return await msg.reply_text(f"• نسبة غباء {msg.reply_to_message.from_user.first_name}: {random.randint(1,100)}% 😂")
    if text.startswith("تحبه") and msg.reply_to_message: return await msg.reply_text(f"• {msg.reply_to_message.from_user.first_name} {random.choice(['يحبك موت ❤️','يكرهك 😂','نص نص'])}")
    if text.startswith("زخرف "): name = text.replace("زخرف ", ""); return await msg.reply_text(f"• الزخرفه:\n『{name}』\n★{name}★")
    if text.startswith("ترجم عربي "): txt = text.replace("ترجم عربي ", ""); return await msg.reply_text(f"• الترجمة: {GoogleTranslator(source='auto', target='ar').translate(txt)}")
    if text.startswith("ترجم انقليزي "): txt = text.replace("ترجم انقليزي ", ""); return await msg.reply_text(f"• الترجمة: {GoogleTranslator(source='auto', target='en').translate(txt)}")
    if user_id == OWNER_ID:
        if text.startswith("اضف رد انلاين "):
            try: word, reply, url = text.replace("اضف رد انلاين ", "").split("|")
            except: return await msg.reply_text("• الصيغه: اضف رد انلاين كلمه | الرد | الرابط")
            db("INSERT OR REPLACE INTO inline_replies VALUES (?,?,?)", (word, reply, url)); return await msg.reply_text("• تم اضافة رد انلاين")
        if text.startswith("اضف رد متعدد "):
            try: word, reply = text.replace("اضف رد متعدد ", "").split("|", 1)
            except: return await msg.reply_text("• الصيغه: اضف رد متعدد كلمه | الرد")
            db("INSERT INTO m6_multi_replies VALUES (?,?)", (word, reply)); return await msg.reply_text("• تم اضافة رد متعدد")

def get_menu():
    keyboard = [
        [InlineKeyboardButton("① اوامر الادمنيه", callback_data="menu1"), InlineKeyboardButton("② اوامر الاعدادات", callback_data="menu2")],
        [InlineKeyboardButton("③ اوامر الحمايه", callback_data="menu3"), InlineKeyboardButton("④ اوامر التسليه", callback_data="menu4")],
        [InlineKeyboardButton(f"⑤ اوامر {BOT_NAME}", callback_data="menu5"), InlineKeyboardButton("⑥ اوامر الخدمات", callback_data="menu6")],
        [InlineKeyboardButton("اخفاء الاوامر", callback_data="hide_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_menu_back(): keyboard = [[InlineKeyboardButton("رجوع ↩️", callback_data="back")], [InlineKeyboardButton("اخفاء الاوامر", callback_data="hide_menu")]]; return InlineKeyboardMarkup(keyboard)
MENU_TEXT = f"- اهلا بك في {BOT_NAME} :\n━━━━━━━━\n- ① : اوامر الادمنيه\n- ② : اوامر الاعدادات\n- ③ : اوامر الحمايه\n- ④ : اوامر التسليه\n- ⑤ : اوامر {BOT_NAME}\n- ⑥ : اوامر الخدمات\n━━━━━━━━"

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "الاوامر" and update.effective_chat.type in ["group", "supergroup"]:
        await update.message.reply_text(MENU_TEXT, reply_markup=get_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    user_id = query.from_user.id
    if query.data.startswith("whisper_"):
        whisper_id = query.data.replace("whisper_", "")
        if whisper_id in context.bot_data:
            whisper = context.bot_data[whisper_id]
            if user_id == whisper["to_id"]:
                await query.answer(f"من {whisper['from_name']}:\n{whisper['text']}", show_alert=True)
            else:
                await query.answer("• الهمسه لا تخصك ❌", show_alert=True)
            del context.bot_data[whisper_id]
        else:
            await query.answer("• انتهت صلاحية الهمسه", show_alert=True)
        return
    if query.data == "menu1": await query.edit_message_text(f"• دخلت: اوامر الادمنيه - {BOT_NAME}", reply_markup=get_menu_back())
    elif query.data == "menu2": await query.edit_message_text(f"• دخلت: اوامر الاعدادات - {BOT_NAME}", reply_markup=get_menu_back())
    elif query.data == "menu3": await query.edit_message_text(f"• دخلت: اوامر الحمايه - {BOT_NAME}", reply_markup=get_menu_back())
    elif query.data == "menu4": await query.edit_message_text(f"• دخلت: اوامر التسليه - {BOT_NAME}", reply_markup=get_menu_back())
    elif query.data == "menu5": await query.edit_message_text(f"• دخلت: اوامر {BOT_NAME}\nللمطور فقط", reply_markup=get_menu_back())
    elif query.data == "menu6": await query.edit_message_text(f"• دخلت: اوامر الخدمات - {BOT_NAME}\nارسل الاوامر m6", reply_markup=get_menu_back())
    elif query.data == "back": await query.edit_message_text(MENU_TEXT, reply_markup=get_menu())
    elif query.data == "hide_menu": await query.delete()

def main():
    if not TOKEN: raise SystemExit("حط TOKEN و OWNER_ID في المتغيرات البيئيه")
    init_db() # <--- اهم سطر اضفته
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, check_locks), group=0)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & filters.Regex("^الاوامر$"), show_menu))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_m1))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_m2))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_m3))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_m4))
    app.add_handler(MessageHandler(filters.TEXT, handle_m5))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_m6))
    app.add_handler(CallbackQueryHandler(button))
    print(f"{BOT_NAME} شغال 100%")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
