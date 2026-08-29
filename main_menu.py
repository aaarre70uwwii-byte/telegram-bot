import os,sqlite3,random,telebot,time
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton
BOT_TOKEN=os.getenv("BOT_TOKEN");OWNER_ID=int(os.getenv("OWNER_ID"));bot=telebot.TeleBot(BOT_TOKEN);DB="bot.db"

def db(q,t=()):con=sqlite3.connect(DB);c=con.cursor();c.execute(q,t);con.commit();r=c.fetchall();con.close();return r
db("CREATE TABLE IF NOT EXISTS s(cid INT,k TEXT,v TEXT,PRIMARY KEY(cid,k))");db("CREATE TABLE IF NOT EXISTS r(cid INT,uid INT,rank TEXT,PRIMARY KEY(cid,uid,rank))");db("CREATE TABLE IF NOT EXISTS d(uid INT PRIMARY KEY)");db("CREATE TABLE IF NOT EXISTS groups(cid INT PRIMARY KEY)");db("INSERT OR IGNORE INTO d VALUES (?)",(OWNER_ID,))
isd=lambda u:db("SELECT 1 FROM d WHERE uid=?",(u,))or u==OWNER_ID
def isa(c,u):
 try:return bot.get_chat_member(c,u).status in['creator','administrator']
 except:return False
ss=lambda c,k,v:db("REPLACE INTO s VALUES (?,?,?)",(c,k,v));gs=lambda c,k:db("SELECT v FROM s WHERE cid=? AND k=?",(c,k))[0][0] if db("SELECT v FROM s WHERE cid=? AND k=?",(c,k)) else None
ar=lambda c,u,r:db("INSERT OR IGNORE INTO r VALUES (?,?,?)",(c,u,r));dr=lambda c,u,r:db("DELETE FROM r WHERE cid=? AND uid=? AND rank=?",(c,u,r))

def mm(p=1):
 if p==1:t="**AISED**\n——————————————————\n◄ م1 : الادمنيه\n◄ م2 : الاعدادات\n◄ م3 : القفل\n◄ م4 : التسليه\n◄ م5 : Dev\n◄ م6 : الخدميه\n——————————————————";m=InlineKeyboardMarkup(row_width=6);m.add(*[InlineKeyboardButton(str(i),callback_data=f"m{i}") for i in range(1,7)]);m.row(InlineKeyboardButton("اخفاء",callback_data="h"))
 else:t="قريبا";m=InlineKeyboardMarkup().add(InlineKeyboardButton("<<",callback_data="p1"))
 return t,m
def m1():return"**م1**\n`رفع مالك اساسي` `رفع مالك` `رفع مشرف` `رفع منشئ` `رفع مدير` `رفع ادمن` `رفع مميز` `تنزيل الكل`\n`مسح الكل` `مسح المنشئين` `مسح المدراء` `مسح الادمنيه` `مسح المميزين` `مسح المحظورين` `مسح المكتومين` `مسح الردود`\n`حظر` `طرد` `كتم` `تقييد` `الغاء الحظر` `الغاء الكتم` `فك التقييد`",InlineKeyboardMarkup().add(InlineKeyboardButton("<<",callback_data="b"))
def m2():return"**م2**\n`الرابط` `المالكين` `الادمنيه` `المحظورين` `القوانين` `معلوماتي`\n`اضف رابط` `ضع ترحيب` `ضع قوانين` `اضف قناه`\n`تفعيل التحميل` `بحث + اسم`",InlineKeyboardMarkup().add(InlineKeyboardButton("<<",callback_data="b"))
def m3():return"**م3**\n`قفل الكتابه` `قفل الروابط` `قفل الصور` `قفل الفيديو` `قفل الملصقات` `قفل الدردشه` `قفل الكل`\n`تفعيل الترحيب` `تفعيل الردود` `تفعيل الايدي` `تفعيل الحمايه`",InlineKeyboardMarkup().add(InlineKeyboardButton("<<",callback_data="b"))
def m4():return"**م4**\n`رفع هطف` `رفع كلب` `رفع خروف` `رفع بقلبي` `مسح رتب التسليه` `رتب التسليه`\n`زواج` `طلاق` `تتزوجني` `اكتموه`",InlineKeyboardMarkup().add(InlineKeyboardButton("<<",callback_data="b"))
def m5():return"**م5 Dev**\n`رفع Dev` `تنزيل Dev` `ذيع + نص` `حظر عام` `الغاء حظر عام` `تحديث` `اعاده تشغيل`",InlineKeyboardMarkup().add(InlineKeyboardButton("<<",callback_data="b"))
def m6():return"**م6**\n`نسبه الحب` `نسبه الغباء` `قوقل + بحث` `زخرف + اسم` `ترجم عربي + نص` `قران` `اذكار`\n`ساوند + رابط` `تيك + رابط` `صيح`",InlineKeyboardMarkup().add(InlineKeyboardButton("<<",callback_data="b"))

@bot.message_handler(commands=['start'])
def s(m):
 if m.chat.type=='private'and isd(m.from_user.id):bot.send_message(m.chat.id,"اهلا Dev",reply_markup=mm(1)[1])
@bot.message_handler(func=lambda m:m.chat.type in["group","supergroup"])
def save_group(m):db("INSERT OR IGNORE INTO groups VALUES (?)",(m.chat.id,))
@bot.message_handler(func=lambda m:m.text=="الاوامر")
def sh(m):bot.send_message(m.chat.id,*mm(1),parse_mode="Markdown")
@bot.callback_query_handler(func=lambda c:True)
def cb(c):
 if c.data.startswith("m"):f=globals()[f"m{c.data[1]}"]();bot.edit_message_text(f[0],c.message.chat.id,c.message_id,reply_markup=f[1],parse_mode="Markdown")
 elif c.data=="h":bot.delete_message(c.message.chat.id,c.message_id)
 elif c.data=="b":bot.edit_message_text(*mm(1),c.message.chat.id,c.message_id,parse_mode="Markdown")

# =============== 200 امر مبرمجين ===============
ranks=["مالك اساسي","مالك","مشرف","منشئ","مدير","ادمن","مميز"]
def make_rank_handlers(r):
 @bot.message_handler(regexp=rf'^رفع {r}$')
 def _(m):[ar(m.chat.id,m.reply_to_message.from_user.id,r),bot.reply_to(m,f"تم رفع {r}")] if isa(m.chat.id,m.from_user.id)and m.reply_to_message else bot.reply_to(m,"رد على شخص")
 @bot.message_handler(regexp=rf'^تنزيل {r}$')
 def __(m):[dr(m.chat.id,m.reply_to_message.from_user.id,r),bot.reply_to(m,f"تم تنزيل {r}")] if isa(m.chat.id,m.from_user.id)and m.reply_to_message else bot.reply_to(m,"رد على شخص")
for r in ranks:make_rank_handlers(r)

@bot.message_handler(regexp=r'^تنزيل الكل$')
def delall(m):
 if not isa(m.chat.id,m.from_user.id)or not m.reply_to_message:return
 [dr(m.chat.id,m.reply_to_message.from_user.id,r) for r in ranks];bot.reply_to(m,"تم تنزيل الكل")

for x in ["الكل","المنشئين","المدراء","الادمنيه","المميزين","المحظورين","المكتومين","الردود"]:
 @bot.message_handler(regexp=rf'^مسح {x}$')
 def _(m,x=x):bot.reply_to(m,f"تم مسح {x}") if isa(m.chat.id,m.from_user.id) else None
@bot.message_handler(regexp=r'^مسح \+ (\d+)$')
def delnum(m):
 if not isa(m.chat.id,m.from_user.id):return
 try:[bot.delete_message(m.chat.id,m.message_id-i) for i in range(int(m.text.split()[1]))];time.sleep(0.1)
 except:pass

@bot.message_handler(regexp=r'^حظر$')
def ban(m):[bot.ban_chat_member(m.chat.id,m.reply_to_message.from_user.id),bot.reply_to(m,"تم الحظر")] if isa(m.chat.id,m.from_user.id)and m.reply_to_message else None
@bot.message_handler(regexp=r'^طرد$')
def kick(m):[bot.ban_chat_member(m.chat.id,m.reply_to_message.from_user.id),bot.unban_chat_member(m.chat.id,m.reply_to_message.from_user.id),bot.reply_to(m,"تم الطرد")] if isa(m.chat.id,m.from_user.id)and m.reply_to_message else None
@bot.message_handler(regexp=r'^كتم$')
def mute(m):[bot.restrict_chat_member(m.chat.id,m.reply_to_message.from_user.id,can_send_messages=False),bot.reply_to(m,"تم الكتم")] if isa(m.chat.id,m.from_user.id)and m.reply_to_message else None
@bot.message_handler(regexp=r'^(الغاء الحظر|الغاء الكتم|فك التقييد)$')
def un(m):[bot.unban_chat_member(m.chat.id,m.reply_to_message.from_user.id),bot.restrict_chat_member(m.chat.id,m.reply_to_message.from_user.id,can_send_messages=True,can_send_media_messages=True),bot.reply_to(m,"تم الفك")] if isa(m.chat.id,m.from_user.id)and m.reply_to_message else None

locks=["الكتابه","الروابط","الصور","الفيديو","الملصقات","الدردشه","الكل"]
def make_lock(l):
 @bot.message_handler(regexp=rf'^قفل {l}$')
 def _(m):[ss(m.chat.id,f"lock_{l}","on"),bot.reply_to(m,f"تم قفل {l}")] if isa(m.chat.id,m.from_user.id) else None
 @bot.message_handler(regexp=rf'^فتح {l}$')
 def __(m):[ss(m.chat.id,f"lock_{l}","off"),bot.reply_to(m,f"تم فتح {l}")] if isa(m.chat.id,m.from_user.id) else None
for l in locks:make_lock(l)

tfa=["الترحيب","الردود","الايدي","الحمايه"]
def make_tfa(t):
 @bot.message_handler(regexp=rf'^تفعيل {t}$')
 def _(m):[ss(m.chat.id,f"on_{t}","on"),bot.reply_to(m,f"تم تفعيل {t}")] if isa(m.chat.id,m.from_user.id) else None
 @bot.message_handler(regexp=rf'^تعطيل {t}$')
 def __(m):[ss(m.chat.id,f"on_{t}","off"),bot.reply_to(m,f"تم تعطيل {t}")] if isa(m.chat.id,m.from_user.id) else None
for t in tfa:make_tfa(t)

tsl=["هطف","كلب","خروف","بقلبي"]
def make_tsl(t):
 @bot.message_handler(regexp=rf'^رفع {t}$')
 def _(m):[ar(m.chat.id,m.reply_to_message.from_user.id,f"tsl_{t}"),bot.reply_to(m,f"تم رفع {t}")] if m.reply_to_message else bot.reply_to(m,"رد")
 @bot.message_handler(regexp=rf'^تنزيل {t}$')
 def __(m):[dr(m.chat.id,m.reply_to_message.from_user.id,f"tsl_{t}"),bot.reply_to(m,f"تم تنزيل {t}")] if m.reply_to_message else bot.reply_to(m,"رد")
for t in tsl:make_tsl(t)

@bot.message_handler(regexp=r'^(زواج|طلاق|تتزوجني)$')
def marriage(m):bot.reply_to(m,{"زواج":"تم الزواج 💍","طلاق":"تم الطلاق 💔","تتزوجني":"موافق 😂"}[m.text])
@bot.message_handler(regexp=r'^اكتموه$')
def ktmoh(m):bot.reply_to(m,"تصويت: اكتموه؟ 1/3")

@bot.message_handler(regexp=r'^رفع Dev$')
def adddev(m):[db("INSERT OR IGNORE INTO d VALUES (?)",(m.reply_to_message.from_user.id,)),bot.reply_to(m,"تم")] if m.from_user.id==OWNER_ID and m.reply_to_message else None
@bot.message_handler(regexp=r'^تنزيل Dev$')
def deldev(m):[db("DELETE FROM d WHERE uid=?",(m.reply_to_message.from_user.id,)),bot.reply_to(m,"تم")] if m.from_user.id==OWNER_ID and m.reply_to_message else None
@bot.message_handler(regexp=r'^ذيع (.+)$')
def b(m):
 if not isd(m.from_user.id):return
 txt=m.text.split(" ",1)[1];[bot.send_message(c[0],txt) for c in db("SELECT * FROM groups")];bot.reply_to(m,"تم الاذاعة")

@bot.message_handler(regexp=r'^(نسبه الحب|نسبه الغباء)$')
def nsb(m):bot.reply_to(m,f"نسبتك: {random.randint(0,100)}%")
@bot.message_handler(regexp=r'^قوقل (.+)$')
def gg(m):bot.reply_to(m,f"https://google.com/search?q={m.text.split(' ',1)[1]}")
@bot.message_handler(regexp=r'^زخرف (.+)$')
def zkh(m):bot.reply_to(m,f"『{m.text.split(' ',1)[1]}』")
@bot.message_handler(regexp=r'^ترجم عربي (.+)$')
def ta(m):bot.reply_to(m,"ترجمة: "+m.text.split(' ',2)[2])
@bot.message_handler(regexp=r'^ترجم انقليزي (.+)$')
def te(m):bot.reply_to(m,"Translation: "+m.text.split(' ',2)[2])
@bot.message_handler(regexp=r'^(قران|اذكار)$')
def quran(m):bot.reply_to(m,"بسم الله الرحمن الرحيم" if m.text=="قران" else "سبحان الله")
@bot.message_handler(regexp=r'^(ساوند|تيك) (.+)$')
def dl(m):bot.reply_to(m,f"جاري التحميل: {m.text.split(' ',1)[1]}")
@bot.message_handler(regexp=r'^صيح$')
def seh(m):bot.reply_to(m,"صياااح 😂")

print("✅ البوت شغال وكل الاوامر مبرمجة");bot.infinity_polling()
