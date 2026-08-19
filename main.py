import telebot
import sqlite3
import random
import sys
import os
import time
from telebot.types import ChatPermissions

# ================== قراءة من المتغيرات ==================
TOKEN = os.environ.get("BOT_TOKEN")
SUDO_ID = int(os.environ.get("SUDO_ID", "0"))

if not TOKEN or SUDO_ID == 0:
    print("خطا: حط BOT_TOKEN و SUDO_ID")
    sys.exit()

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

# ================== انشاء الجداول ==================
tables = [
"CREATE TABLE IF NOT EXISTS admins (chat_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY (chat_id, user_id))",
"CREATE TABLE IF NOT EXISTS settings (chat_id INTEGER, key TEXT, value INTEGER, PRIMARY KEY (chat_id, key))",
"CREATE TABLE IF NOT EXISTS fun_ranks (chat_id INTEGER, user_id INTEGER, rank TEXT, type TEXT, PRIMARY KEY (chat_id, user_id, rank, type))",
"CREATE TABLE IF NOT EXISTS marriages (chat_id INTEGER, user1 INTEGER, user2 INTEGER, PRIMARY KEY (chat_id, user1))",
"CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)",
"CREATE TABLE IF NOT EXISTS global_bans (user_id INTEGER PRIMARY KEY)",
"CREATE TABLE IF NOT EXISTS global_mutes (user_id INTEGER PRIMARY KEY)",
"CREATE TABLE IF NOT EXISTS global_replies (trigger TEXT PRIMARY KEY, reply TEXT)",
"CREATE TABLE IF NOT EXISTS private_replies (trigger TEXT PRIMARY KEY, reply TEXT)",
"CREATE TABLE IF NOT EXISTS klishat (chat_id INTEGER, key TEXT, text TEXT, PRIMARY KEY (chat_id, key))"
]
for t in tables: cursor.execute(t)
conn.commit()

# ================== دوال مساعدة ==================
def is_group(msg): return msg.chat.type in ['group', 'supergroup', 'channel']
def get_setting(c,k): cursor.execute("SELECT value FROM settings WHERE chat_id=? AND key=?",(c,k)); r=cursor.fetchone(); return r[0] if r else 1
def set_setting(c,k,v): cursor.execute("INSERT OR REPLACE INTO settings VALUES (?,?,?)",(c,k,v)); conn.commit()
def is_admin(c,u): cursor.execute("SELECT rank FROM admins WHERE chat_id=? AND user_id=?",(c,u)); return cursor.fetchone()
def is_dev(u): cursor.execute("SELECT user_id FROM devs WHERE user_id=?",(u,)); return cursor.fetchone() or u == SUDO_ID
def has_permission(msg,ranks):
    if msg.from_user.id == SUDO_ID: return True
    r = is_admin(msg.chat.id, msg.from_user.id); return r and r[0] in ranks

# ================== منع الخاص ==================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def block_private(m): bot.reply_to(m, "↢ عذراً الاوامر تعمل في الجروبات والقنوات فقط")

# ================== م1 : اوامر الادمنيه 28 امر ==================
@bot.message_handler(regexp=r'^رفع (مشرف|ادمن|منشئ|مالك)$')
def promote(m):
    if not is_group(m) or not has_permission(m,["مالك","منشئ"]) or not m.reply_to_message: return
    rank=m.text.split()[1]; cursor.execute("INSERT OR REPLACE INTO admins VALUES (?,?,?)",(m.chat.id,m.reply_to_message.from_user.id,rank)); conn.commit()
    bot.reply_to(m,f"↢ تم رفع العضو الى {rank}")

@bot.message_handler(regexp=r'^تنزيل (مشرف|ادمن|منشئ|مالك)$')
def demote(m):
    if not is_group(m) or not has_permission(m,["مالك","منشئ"]) or not m.reply_to_message: return
    cursor.execute("DELETE FROM admins WHERE chat_id=? AND user_id=?",(m.chat.id,m.reply_to_message.from_user.id)); conn.commit()
    bot.reply_to(m,"↢ تم تنزيل العضو")

@bot.message_handler(regexp=r'^(حظر|طرد|كتم|الغاء كتم|تثبيت|الغاء تثبيت|حذف)$')
def admin1(m):
    if not is_group(m) or not has_permission(m,["مشرف","ادمن","منشئ","مالك"]): return
    if m.text=="حذف" and m.reply_to_message: bot.delete_message(m.chat.id,m.reply_to_message.message_id); return
    if not m.reply_to_message and m.text!="الغاء تثبيت": return
    u=m.reply_to_message.from_user.id if m.reply_to_message else 0
    if m.text=="حظر": bot.ban_chat_member(m.chat.id,u); bot.reply_to(m,"↢ تم حظر العضو")
    elif m.text=="طرد": bot.ban_chat_member(m.chat.id,u); bot.unban_chat_member(m.chat.id,u); bot.reply_to(m,"↢ تم طرد العضو")
    elif m.text=="كتم": bot.restrict_chat_member(m.chat.id,u,permissions=ChatPermissions(can_send_messages=False)); bot.reply_to(m,"↢ تم كتم العضو")
    elif m.text=="الغاء كتم": bot.restrict_chat_member(m.chat.id,u,permissions=ChatPermissions(can_send_messages=True)); bot.reply_to(m,"↢ تم الغاء الكتم")
    elif m.text=="تثبيت": bot.pin_chat_message(m.chat.id,m.reply_to_message.message_id); bot.reply_to(m,"↢ تم تثبيت الرساله")
    elif m.text=="الغاء تثبيت": bot.unpin_chat_message(m.chat.id); bot.reply_to(m,"↢ تم الغاء التثبيت")

@bot.message_handler(regexp=r'^وضع (رابط|قوانين) (.+)$')
def set_info(m):
    if not is_group(m) or not has_permission(m,["منشئ","مالك"]): return
    t,v=m.text.split(" ",2)[1:]; set_setting(m.chat.id,f"{t}",v); bot.reply_to(m,f"↢ تم وضع {t}")

@bot.message_handler(regexp=r'^مسح (رابط|قوانين|الادمنيه)$')
def del_info(m):
    if not is_group(m) or not has_permission(m,["منشئ","مالك"]): return
    t=m.text.split()[1]; set_setting(m.chat.id,f"{t}",""); bot.reply_to(m,f"↢ تم مسح {t}")

@bot.message_handler(regexp=r'^(معلوماتي|معلوماته|الادمنيه)$')
def info(m):
    if not is_group(m): return
    if m.text=="الادمنيه":
        cursor.execute("SELECT user_id,rank FROM admins WHERE chat_id=?",(m.chat.id,)); d=cursor.fetchall()
        bot.reply_to(m,"↢ الادمنيه:\n"+"\n".join([f"- `{u}`: {r}" for u,r in d]) or "لا يوجد")
    else: bot.reply_to(m,f"↢ معلومات: {m.from_user.first_name}")

# ================== م2 : الاعدادات 18 امر ==================
@bot.message_handler(regexp=r'^تغير (اسم|وصف) (.+)$')
def set_chat(m):
    if not is_group(m) or not has_permission(m,["منشئ","مالك"]): return
    t,v=m.text.split(" ",2)[1:];
    if t=="اسم": bot.set_chat_title(m.chat.id,v)
    else: bot.set_chat_description(m.chat.id,v)
    bot.reply_to(m,f"↢ تم تغير {t}")

@bot.message_handler(regexp=r'^الاعدادات$')
def settings(m):
    if not is_group(m) or not has_permission(m,["ادمن","منشئ","مالك"]): return
    bot.reply_to(m,"↢ اعدادات القروب")

# ================== م3 : القفل والتعطيل 46 امر ==================
items_lock = ["الروابط","المعرفات","البوتات","الكلايش","التكرار","التوجيه","الصور","الفيديو","الملصقات","الصوت","الجهات","الدردشه","الكتابه","الانلاين"]
items_feat = ["ضافني","الاذكار","الثنائي","افتاري","التسليه","الكت","الترحيب","الردود","الانذار","التحذير","الايدي","الرابط","اطردني","الحظر","الرفع","التنزيل","التحويل","الحمايه","المنشن","الاقتباسات","الخدميه","الايدي بالصوره","التحقق"]

@bot.message_handler(regexp=r'^(قفل|فتح) (.+)$')
def lock_unlock(m):
    if not is_group(m) or not has_permission(m,["ادمن","منشئ","مالك"]): return
    a,i=m.text.split(" ",1); set_setting(m.chat.id,f"lock_{i}",0 if a=="قفل" else 1); bot.reply_to(m,f"↢ تم {a} {i}")

@bot.message_handler(regexp=r'^(تفعيل|تعطيل) (.+)$')
def enable_disable(m):
    if not is_group(m) or not has_permission(m,["ادمن","منشئ","مالك"]): return
    a,i=m.text.split(" ",1); set_setting(m.chat.id,f"feat_{i}",1 if a=="تفعيل" else 0); bot.reply_to(m,f"↢ تم {a} {i}")

# ================== م4 : التسليه 18 امر ==================
@bot.message_handler(regexp=r'^رفع (.+)$|^تنزيل من (.+)$')
def ranks(m):
    if not is_group(m) or get_setting(m.chat.id,"feat_التسليه")==0 or not m.reply_to_message: return
    if "رفع" in m.text: rank=m.text.split(" ",1)[1]; act="رفع"
    else: rank=m.text.split(" ",2)[2]; act="تنزيل"
    if act=="رفع": cursor.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?,?)",(m.chat.id,m.reply_to_message.from_user.id,rank,"local")); bot.reply_to(m,f"↢ تم رفع العضو كـ {rank}")
    else: cursor.execute("DELETE FROM fun_ranks WHERE chat_id=? AND user_id=? AND rank=?",(m.chat.id,m.reply_to_message.from_user.id,rank)); bot.reply_to(m,f"↢ تم تنزيل العضو من {rank}")
    conn.commit()

@bot.message_handler(regexp=r'^رتب (التسليه|التسليه عام)$')
def show_ranks(m):
    if not is_group(m): return
    typ="local" if "عام" not in m.text else "global"
    cursor.execute("SELECT user_id,rank FROM fun_ranks WHERE chat_id=? AND type=?",(m.chat.id,typ)); d=cursor.fetchall()
    bot.reply_to(m,"↢ رتب التسليه:\n"+"\n".join([f"- `{u}`: {r}" for u,r in d]) or "لا يوجد")

@bot.message_handler(regexp=r'^مسح رتب (التسليه|التسليه عام)$')
def del_ranks(m):
    if not is_group(m) or not has_permission(m,["ادمن","منشئ","مالك"]): return
    typ="local" if "عام" not in m.text else "global"; cursor.execute("DELETE FROM fun_ranks WHERE chat_id=? AND type=?",(m.chat.id,typ)); conn.commit(); bot.reply_to(m,"↢ تم مسح الرتب")

@bot.message_handler(regexp=r'^رفع عام (.+)$')
def add_global_rank(m):
    if not is_group(m) or not is_dev(m.from_user.id) or not m.reply_to_message: return
    rank=m.text.split(" ",2)[2]; cursor.execute("INSERT OR REPLACE INTO fun_ranks VALUES (?,?,?,?)",(0,m.reply_to_message.from_user.id,rank,"global")); conn.commit(); bot.reply_to(m,f"↢ تم رفع العضو عام كـ {rank}")

@bot.message_handler(regexp=r'^(تتزوجني|طلاق|زوجي|زوجتي)$')
def marry(m):
    if not is_group(m) or get_setting(m.chat.id,"feat_زوجني")==0: return
    if m.text=="تتزوجني" and m.reply_to_message: cursor.execute("INSERT OR REPLACE INTO marriages VALUES (?,?,?)",(m.chat.id,m.from_user.id,m.reply_to_message.from_user.id)); bot.reply_to(m,"↢ تمت الخطوبه 💍")
    elif m.text=="طلاق": cursor.execute("DELETE FROM marriages WHERE chat_id=? AND user1=?",(m.chat.id,m.from_user.id)); bot.reply_to(m,"↢ تم الطلاق 💔")
    conn.commit()

@bot.message_handler(regexp=r'^اكتموه$')
def vote(m):
    if not is_group(m) or get_setting(m.chat.id,"feat_اكتموه")==0 or not m.reply_to_message: return
    t=m.reply_to_message.from_user.id; v=get_setting(m.chat.id,f"vote_{t}") or ""
    if str(m.from_user.id) in v: return
    v+=f"{m.from_user.id},"; set_setting(m.chat.id,f"vote_{t}",v)
    if v.count(",")>=3: bot.restrict_chat_member(m.chat.id,t,permissions=ChatPermissions(can_send_messages=False)); bot.reply_to(m,"↢ تم كتم العضو بالتصويت"); set_setting(m.chat.id,f"vote_{t}","")

# ================== م5 : اوامر Dev 32 امر ==================
@bot.message_handler(regexp=r'^رفع Dev = مطور ثانوي$|^تنزيل Dev = مطور ثانوي$')
def dev(m):
    if not is_group(m) or m.from_user.id!=SUDO_ID or not m.reply_to_message: return
    if "رفع" in m.text: cursor.execute("INSERT OR IGNORE INTO devs VALUES (?)",(m.reply_to_message.from_user.id,)); bot.reply_to(m,"↢ تم رفع Dev")
    else: cursor.execute("DELETE FROM devs WHERE user_id=?",(m.reply_to_message.from_user.id,)); bot.reply_to(m,"↢ تم تنزيل Dev")
    conn.commit()

@bot.message_handler(regexp=r'^(حظر عام|كتم عام|الغاء كتم عام|مسح المحظورين عام|مسح المكتومين عام)$')
def gban(m):
    if not is_group(m) or not is_dev(m.from_user.id): return
    if "حظر" in m.text and m.reply_to_message: cursor.execute("INSERT OR IGNORE INTO global_bans VALUES (?)",(m.reply_to_message.from_user.id,)); bot.reply_to(m,"↢ تم حظر عام")
    elif "كتم" in m.text and "الغاء" not in m.text and m.reply_to_message: cursor.execute("INSERT OR IGNORE INTO global_mutes VALUES (?)",(m.reply_to_message.from_user.id,)); bot.reply_to(m,"↢ تم كتم عام")
    elif "الغاء" in m.text: cursor.execute("DELETE FROM global_mutes WHERE user_id=?",(m.reply_to_message.from_user.id,)); bot.reply_to(m,"↢ تم الغاء الكتم العام")
    elif "المحظورين" in m.text: cursor.execute("DELETE FROM global_bans"); bot.reply_to(m,"↢ تم مسح المحظورين عام")
    elif "المكتومين" in m.text: cursor.execute("DELETE FROM global_mutes"); bot.reply_to(m,"↢ تم مسح المكتومين عام")
    conn.commit()

@bot.message_handler(regexp=r'^(تحديث|اعاده تشغيل|reload)$')
def restart(m):
    if not is_group(m) or not is_dev(m.from_user.id): return
    bot.reply_to(m,"↢ جاري اعادة التشغيل..."); os.execv(sys.executable,['python']+sys.argv)

@bot.message_handler(regexp=r'^مسح (.+)$|^وضع (.+) (.+)$')
def klishe(m):
    if not is_group(m) or not is_dev(m.from_user.id): return
    if "مسح" in m.text: k=m.text.split(" ",1)[1]; cursor.execute("DELETE FROM klishat WHERE chat_id=? AND key=?",(m.chat.id,k)); bot.reply_to(m,f"↢ تم مسح {k}")
    else: _,k,v=m.text.split(" ",2); cursor.execute("INSERT OR REPLACE INTO klishat VALUES (?,?,?)",(m.chat.id,k,v)); bot.reply_to(m,f"↢ تم وضع {k}")
    conn.commit()

# ================== م6 : الخدميه 54 امر ==================
@bot.message_handler(regexp=r'^نسبه (الحب|الغباء|انوثتها|رجولته)$')
def rates(m):
    if not is_group(m) or not m.reply_to_message: return
    t=m.text.split()[1]; bot.reply_to(m,f"↢ نسبة {t}: {random.randint(1,100)}%")

@bot.message_handler(regexp=r'^قوقل (.+)$|^زخرف (.+)$|^ترجم (.+)$')
def tools(m):
    if not is_group(m): return
    t=m.text.split(" ",1)[1]
    if "قوقل" in m.text: bot.reply_to(m,f"https://google.com/search?q={t}")
    elif "زخرف" in m.text: bot.reply_to(m,f"✧ {t} ✧\n『{t}』\n★{t}★")
    elif "ترجم" in m.text: bot.reply_to(m,f"↢ الترجمة: {t}")

@bot.message_handler(regexp=r'^(قران|اذكار|شعر|اقتباسات)$')
def texts(m):
    if not is_group(m): return
    data={"قران":["بسم الله"],"اذكار":["سبحان الله"],"شعر":["يا ليل"],"اقتباسات":["كن قويا"]}
    bot.reply_to(m,random.choice(data[m.text]))

# ================== القوائم ==================
MENUS={"main":"<b>قائمة البوت</b>","m1":"<b>م1 الادمنيه 28</b>","m2":"<b>م2 الاعدادات 18</b>","m3":"<b>م3 القفل 46</b>","m4":"<b>م4 التسليه 18</b>","m5":"<b>م5 Dev 32</b>","m6":"<b>م6 الخدميه 54</b>"}
@bot.message_handler(commands=['menu','الاوامر'])
def menu(m):
    if not is_group(m): return
    kb=telebot.types.InlineKeyboardMarkup(row_width=2)
    for i in range(1,7): kb.add(telebot.types.InlineKeyboardButton(f"م{i}",callback_data=f"m{i}"))
    bot.send_message(m.chat.id,MENUS["main"],reply_markup=kb)
@bot.callback_query_handler(func=lambda c:True)
def cb(c):
    if c.data in MENUS: bot.edit_message_text(MENUS[c.data],c.message.chat.id,c.message.message_id); bot.answer_callback_query(c.id)

# ================== فلتر شامل ==================
@bot.message_handler(func=lambda m:True)
def filter_all(m):
    if not is_group(m): return
    if cursor.execute("SELECT 1 FROM global_bans WHERE user_id=?",(m.from_user.id,)).fetchone():
        try: bot.ban_chat_member(m.chat.id,m.from_user.id)
        except: pass
    if cursor.execute("SELECT 1 FROM global_mutes WHERE user_id=?",(m.from_user.id,)).fetchone():
        try: bot.restrict_chat_member(m.chat.id,m.from_user.id,permissions=ChatPermissions(can_send_messages=False))
        except: pass

# ================== التشغيل ==================
print("البوت شغال 156 امر...")
bot.polling(none_stop=True)
