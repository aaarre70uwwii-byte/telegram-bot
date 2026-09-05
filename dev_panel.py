import os
import time
import sqlite3
import yt_dlp
import sys
import random
import asyncio
import uuid
import datetime
from deep_translator import GoogleTranslator
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, ReplyKeyboardMarkup, KeyboardButton, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
BOT_NAME = "Tia"
BOT_CHANNEL = "@channel"

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

# ===== كل الجداول =====
cur.execute("CREATE TABLE IF NOT EXISTS ranks_admin (group_id INTEGER, user_id INTEGER, rank TEXT, PRIMARY KEY(group_id, user_id, rank))")
cur.execute("CREATE TABLE IF NOT EXISTS settings (group_id INTEGER PRIMARY KEY, link TEXT, welcome TEXT, rules TEXT, channel TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS banned (group_id INTEGER, user_id INTEGER, PRIMARY KEY(group_id, user_id))")
cur.execute("CREATE TABLE IF NOT EXISTS muted (group_id INTEGER, user_id INTEGER, PRIMARY KEY(group_id, user_id))")
cur.execute("CREATE TABLE IF NOT EXISTS lock (group_id INTEGER, type TEXT, status TEXT, PRIMARY KEY(group_id, type))")
cur.execute("CREATE TABLE IF NOT EXISTS enable_group (group_id INTEGER, type TEXT, status INTEGER, PRIMARY KEY(group_id, type))")
cur.execute("CREATE TABLE IF NOT EXISTS warns (group_id INTEGER, user_id INTEGER, count INTEGER, PRIMARY KEY(group_id, user_id))")
cur.execute("CREATE TABLE IF NOT EXISTS filter_words (group_id INTEGER, type TEXT, word TEXT, PRIMARY KEY(group_id, type, word))")
cur.execute("CREATE TABLE IF NOT EXISTS ranks_fun (group_id INTEGER, user_id INTEGER, rank TEXT, type TEXT, PRIMARY KEY(group_id, user_id, type))")
cur.execute("CREATE TABLE IF NOT EXISTS marriage (group_id INTEGER, user1 INTEGER, user2 INTEGER, PRIMARY KEY(group_id, user1, user2))")
cur.execute("CREATE TABLE IF NOT EXISTS vote_aktmoh (group_id INTEGER, target_id INTEGER, voters TEXT, count INTEGER, time REAL, PRIMARY KEY(group_id, target_id))")
cur.execute("CREATE TABLE IF NOT EXISTS devs (user_id INTEGER PRIMARY KEY)")
cur.execute("CREATE TABLE IF NOT EXISTS gban (user_id INTEGER, reason TEXT, PRIMARY KEY(user_id))")
cur.execute("CREATE TABLE IF NOT EXISTS gmute (user_id INTEGER, reason TEXT, PRIMARY KEY(user_id))")
cur.execute("CREATE TABLE IF NOT EXISTS dev_ranks (user_id INTEGER, rank TEXT, PRIMARY KEY(user_id))")
cur.execute("CREATE TABLE IF NOT EXISTS global_replies (word TEXT, reply TEXT, type TEXT, PRIMARY KEY(word))")
cur.execute("CREATE TABLE IF NOT EXISTS multi_replies (word TEXT, reply TEXT, id INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS contact_replies (word TEXT, reply TEXT, type TEXT DEFAULT 'text', PRIMARY KEY(word))")
cur.execute("CREATE TABLE IF NOT EXISTS settings_global (key TEXT PRIMARY KEY, value TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS klisha (key TEXT PRIMARY KEY, value TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS inline_replies (word TEXT, reply TEXT, url TEXT, PRIMARY KEY(word))")
cur.execute("CREATE TABLE IF NOT EXISTS m6_multi_replies (word TEXT, reply TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
cur.execute("CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY)")
cur.execute("CREATE TABLE IF NOT EXISTS replies_private (word TEXT PRIMARY KEY, reply TEXT)")
cur.execute("INSERT OR IGNORE INTO settings_global VALUES ('welcome', 'اهلا بك في بوت Tia ❤️')")
cur.execute("INSERT OR IGNORE INTO settings_global VALUES ('bot_status', 'on')")
cur.execute("INSERT OR IGNORE INTO settings_global VALUES ('zajel', 'مفتوح')")
cur.execute("INSERT OR IGNORE INTO devs VALUES (?)", (OWNER_ID,))
conn.commit()

RANKS_ADMIN = {"مالك اساسي": "owner_basic", "مالك": "owner", "مشرف": "mod", "منشئ": "creator", "مدير": "manager", "ادمن": "admin", "مميز": "vip"}
RANKS_FUN = {"هطف": "الهطوف", "بثر": "البثرين", "حمار": "الحمير", "كلب": "الكلاب", "كلبه": "الكلبات", "عتوي": "العتوين", "عتويه": "العتويات", "لحجي": "اللحوج", "لحجيه": "اللحجيات", "خروف": "الخرفان", "خفيفه": "الخفيفات", "خفيف": "الخفيفين"}
LOCK_TYPES = ["جمثون","السب","الايرانيه","الكتابه","الاباحي","تعديل الميديا","التعديل","الفيديو","الصور","الملصقات","المتحركه","الدردشه","الروابط","التاك","البوتات","المعرفات","الكلايش","التكرار","التوجيه","الانلاين","الجهات","الدخول","الصوت"]

def get_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("م1", callback_data="admin"), InlineKeyboardButton("م2", callback_data="settings")],
        [InlineKeyboardButton("م3", callback_data="lock"), InlineKeyboardButton("م4", callback_data="fun")],
        [InlineKeyboardButton("م5", callback_data="dev"), InlineKeyboardButton("م6", callback_data="service")],
        [InlineKeyboardButton("اخفاء الاوامر", callback_data="close")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_dev_keyboard():
    keyboard = [
        [KeyboardButton("أعدادات ألبوت"), KeyboardButton("قائمة ألعام")],
        [KeyboardButton("تغير المطور الاساسي"), KeyboardButton("أضف رد عام")],
        [KeyboardButton("تغير أسم البوت"), KeyboardButton("مسح رد عام")],
        [KeyboardButton("تفعيل ألبوت"), KeyboardButton("تحديث الملفات")],
        [KeyboardButton("أضف الترحيب نص+بصوره"), KeyboardButton("جلب ألنسخه الأحتياطيه")],
        [KeyboardButton("تعطيل البوت ألخدمي"), KeyboardButton("تفعيل البوت ألخدمي")],
        [KeyboardButton("تعطيل التواصل"), KeyboardButton("تفعيل التواصل")],
        [KeyboardButton("الاحصايات"), KeyboardButton("الاذاعه خاص+مجموعات")],
        [KeyboardButton("ألمطورين"), KeyboardButton("تغير قناه البوت")],
        [KeyboardButton("اخفاء قائمة البوت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def is_admin(u,c):
    if u.effective_user.id == OWNER_ID: return True
    try: m = await c.bot.get_chat_member(u.effective_chat.id, u.effective_user.id); return m.status in ['creator','administrator']
    except: return False
async def is_dev(u,c):
    if u.effective_user.id == OWNER_ID: return True
    cur.execute("SELECT 1 FROM devs WHERE user_id=?", (u.effective_user.id,)); return cur.fetchone() is not None
async def get_target(u): return u.message.reply_to_message.from_user.id if u.message.reply_to_message else None
async def get_global_setting(k): cur.execute("SELECT value FROM settings_global WHERE key=?", (k,)); r=cur.fetchone(); return r[0] if r else "مفتوح"
async def set_global_setting(k,v): cur.execute("INSERT OR REPLACE INTO settings_global VALUES (?,?)", (k,v)); conn.commit()
async def set_lock(g,t,s): cur.execute("INSERT OR REPLACE INTO lock VALUES (?,?,?)", (g,t,s)); conn.commit()
async def get_lock(g,t): cur.execute("SELECT status FROM lock WHERE group_id=? AND type=?", (g,t)); r=cur.fetchone(); return r[0] if r else "مفتوح"
async def set_enable(g,t,s): cur.execute("INSERT OR REPLACE INTO enable_group VALUES (?,?,?)", (g,t,s)); conn.commit()
async def get_enable(g,t): cur.execute("SELECT status FROM enable_group WHERE group_id=? AND type=?", (g,t)); r=cur.fetchone(); return r[0] if r else 1
async def broadcast(c,t): cur.execute("SELECT id FROM groups"); [await c.bot.send_message(g[0],t) for g in cur.fetchall()]

async def menu(u,c):
    if u.effective_chat.type=='private': return
    txt="- اهلا بك عزيزي في قائمة الاوامر :\n────────────────────────────────\nم1 : اوامر الادمنيه\nم2 : اوامر الاعدادات\nم3 : اوامر القفل - الفتح\nم4 : اوامر التسليه\nم5 : Dev اوامر\nم6 : الاوامر الخدميه\n────────────────────────────────"
    await u.message.reply_text(txt, reply_markup=get_menu_keyboard())

async def start(u,c):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?)", (u.effective_user.id,)); conn.commit()
    if u.effective_user.id!=OWNER_ID and u.effective_chat.type=='private':
        try: await c.bot.send_message(OWNER_ID,f"🚨 دخول جديد\nالاسم: {u.effective_user.first_name}\nالايدي: `{u.effective_user.id}`",parse_mode='Markdown')
        except: pass
    await u.message.reply_text(await get_global_setting('welcome'))

async def panel(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text(f"اهلا بك عزي Dev في لوحة تحكم {BOT_NAME}\n👇", reply_markup=get_dev_keyboard())

async def buttons(u,c):
    q=u.callback_query; await q.answer()
    menus={"admin":"**م1 الادمنيه:**\n`رفع ادمن` `تنزيل ادمن` `حظر` `كتم` `مسح الكل`","settings":"**م2 الاعدادات:**\n`الرابط` `اضف رابط` `ضع قوانين` `ضع ترحيب`","lock":"**م3 القفل:**\n`قفل الروابط` `قفل الكل` `قائمة القفل`","fun":"**م4 التسليه:**\n`رفع هطف` `زواج` `طلاق` `اكتموه`","dev":"**م5 Dev:**\n`اضف رد عام` `حظر عام` `رفع Dev` `ذيع` `تحديث`","service":"**م6 الخدميه:**\n`نسبه الحب` `ترجم` `ساوند` `تحويل`"}
    if q.data=="close": await q.delete()
    elif q.data in menus: await q.edit_message_text(menus[q.data],parse_mode="Markdown")

async def handle(u,c):
    if not u.message: return
    msg=u.message; text=msg.text.strip() if msg.text else ""; chat=msg.chat; uid=msg.from_user.id
    cur.execute("INSERT OR IGNORE INTO groups VALUES (?)", (chat.id,)); conn.commit()
    os.makedirs("downloads",exist_ok=True)

    # الخاص
    if chat.type=='private' and uid==OWNER_ID:
        d=c.user_data
        if text=="الاحصايات": cur.execute("SELECT COUNT(*) FROM users");us=cur.fetchone()[0];cur.execute("SELECT COUNT(*) FROM groups");gs=cur.fetchone()[0];return await msg.reply_text(f"الاعضاء: {us}\nالمجموعات: {gs}")
        if text=="جلب ألنسخه الأحتياطيه": return await msg.reply_document(InputFile('bot.db'))
        if text=="الاذاعه خاص+مجموعات": d['step']='bc'; return await msg.reply_text("ارسل الاذاعة")
        if d.get('step')=='bc': cur.execute("SELECT id FROM users");[await c.bot.send_message(x[0],text) for x in cur.fetchall()];cur.execute("SELECT id FROM groups");[await c.bot.send_message(x[0],text) for x in cur.fetchall()];d['step']=None;return await msg.reply_text("تم ✅")
        if text=="اخفاء قائمة البوت": return await msg.reply_text("تم",reply_markup=ReplyKeyboardRemove())
        cur.execute("SELECT reply FROM replies_private WHERE word=?",(text,));r=cur.fetchone();return await msg.reply_text(r[0] if r else "اختر من الازرار")

    # القروبات
    if chat.type in ['group','supergroup']:
        cur.execute("SELECT reply,url FROM inline_replies WHERE word=?",(text,));r=cur.fetchone();
        if r: return await msg.reply_text(r[0],reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("الرابط",url=r[1])]]))
        cur.execute("SELECT reply FROM m6_multi_replies WHERE word=?",(text,));r=cur.fetchall();
        if r: return await msg.reply_text(random.choice(r)[0])
        if await get_global_setting("my_replies")=="مفتوح": cur.execute("SELECT reply FROM global_replies WHERE word=?",(text,));r=cur.fetchone();
        if r: return await msg.reply_text(r[0])

        adm=await is_admin(u,c); dev=await is_dev(u,c); tar=await get_target(u)

        # م1
        if adm:
            for n,k in RANKS_ADMIN.items():
                if text==f"رفع {n}" and tar: cur.execute("INSERT OR IGNORE INTO ranks_admin VALUES (?,?,?)",(chat.id,tar,k));conn.commit();return await msg.reply_text(f"تم رفع {n}")
                if text==f"تنزيل {n}" and tar: cur.execute("DELETE FROM ranks_admin WHERE group_id=? AND user_id=? AND rank=?",(chat.id,tar,k));conn.commit();return await msg.reply_text(f"تم تنزيل {n}")
            if text=="حظر" and tar: await c.bot.ban_chat_member(chat.id,tar);cur.execute("INSERT OR IGNORE INTO banned VALUES (?,?)",(chat.id,tar));conn.commit();return await msg.reply_text("تم الحظر")
            if text=="كتم" and tar: await c.bot.restrict_chat_member(chat.id,tar,ChatPermissions());cur.execute("INSERT OR IGNORE INTO muted VALUES (?,?)",(chat.id,tar));conn.commit();return await msg.reply_text("تم الكتم")
            if text=="مسح الكل": cur.execute("DELETE FROM ranks_admin WHERE group_id=?",(chat.id,));conn.commit();return await msg.reply_text("تم مسح كل الرتب")

        # م2
        if adm and text.startswith("اضف رابط "): link=text.replace("اضف رابط ","");cur.execute("INSERT OR REPLACE INTO settings VALUES (?,?,?,?,?)",(chat.id,link,None,None,None));conn.commit();return await msg.reply_text("تم حفظ الرابط")
        if text=="الرابط": cur.execute("SELECT link FROM settings WHERE group_id=?",(chat.id,));r=cur.fetchone();return await msg.reply_text(f"الرابط: {r[0] if r else 'لا يوجد'}")

        # م3
        if text=="قائمة القفل":
            t="• حالة القفل:\n━━━━━━━━━━━━\n"
            for x in LOCK_TYPES: s=await get_lock(chat.id,x); t+=f"{'🔒' if s!='مفتوح' else '🔓'} {x}: {s}\n"
            return await msg.reply_text(t)
        if adm:
            for x in LOCK_TYPES:
                if text==f"قفل {x}": await set_lock(chat.id,x,"مقفول");return await msg.reply_text(f"تم قفل {x}")
                if text==f"فتح {x}": await set_lock(chat.id,x,"مفتوح");return await msg.reply_text(f"تم فتح {x}")
            if text=="قفل الكل": [await set_lock(chat.id,x,"مقفول") for x in LOCK_TYPES];return await msg.reply_text("تم قفل الكل")

        # م4
        if await get_enable(chat.id,"التسليه")==1:
            if text=="الاوامر":
                t="• اوامر التسليه :\n━━━━━━━━━━━━\n"
                t+="\n".join([f"• رفع - تنزيل : {r} : {p}" for r,p in RANKS_FUN.items()])
                t+="\n• زواج\n• طلاق\n• اكتموه"
                return await msg.reply_text(t)
            for r,p in RANKS_FUN.items():
                if text==f"رفع {r}" and tar: cur.execute("INSERT OR REPLACE INTO ranks_fun VALUES (?,?,?,?)",(chat.id,tar,p,"قروب"));conn.commit();return await msg.reply_text(f"تم رفع {msg.reply_to_message.from_user.first_name} الى {p}")
                if text==f"تنزيل {r}" and tar: cur.execute("DELETE FROM ranks_fun WHERE group_id=? AND user_id=? AND type=?",(chat.id,tar,"قروب"));conn.commit();return await msg.reply_text(f"تم تنزيل {msg.reply_to_message.from_user.first_name}")
            if text=="زواج" and tar: cur.execute("INSERT OR IGNORE INTO marriage VALUES (?,?,?)",(chat.id,uid,tar));cur.execute("INSERT OR IGNORE INTO marriage VALUES (?,?,?)",(chat.id,tar,uid));conn.commit();return await msg.reply_text("💍 مبروك تم الزواج")
            if text=="طلاق" and tar: cur.execute("DELETE FROM marriage WHERE group_id=? AND ((user1=? AND user2=?) OR (user1=? AND user2=?))",(chat.id,uid,tar,tar,uid));conn.commit();return await msg.reply_text("💔 تم الطلاق")
            if text=="اكتموه" and tar: cur.execute("SELECT count FROM vote_aktmoh WHERE group_id=? AND target_id=?",(chat.id,tar));r=cur.fetchone();n=r[0]+1 if r else 1;cur.execute("INSERT OR REPLACE INTO vote_aktmoh VALUES (?,?,?,?,?)",(chat.id,tar,str(uid),n,time.time()));conn.commit();
            if n>=3: await restrict_user(c,chat.id,tar,600);return await msg.reply_text("تم كتمه 10 دقايق")
            return await msg.reply_text(f"تصويت: {n}/3")

        # م5
        if dev:
            if text.startswith("اضف رد عام "):w,r=text.replace("اضف رد عام ","").split("|",1);cur.execute("INSERT OR REPLACE INTO global_replies VALUES (?,?,?)",(w,r,"text"));conn.commit();return await msg.reply_text(f"تم اضافة رد: {w}")
            if text.startswith("حظر عام") and tar: cur.execute("INSERT OR REPLACE INTO gban VALUES (?,?)",(tar,"سبب"));conn.commit();return await msg.reply_text("تم حظره عام")
            if text.startswith("كتم عام") and tar: cur.execute("INSERT OR REPLACE INTO gmute VALUES (?,?)",(tar,"سبب"));conn.commit();return await msg.reply_text("تم كتمه عام")
            if text.startswith("رفع Dev") and tar: cur.execute("INSERT OR IGNORE INTO devs VALUES (?)",(tar,));conn.commit();return await msg.reply_text("تم رفعه Dev")
            if text.startswith("ذيع "):
                if await get_global_setting("zajel")=="مقفول": return await msg.reply_text("الزاجل مقفول")
                await broadcast(c,f"📢 {text.replace('ذيع ','')}");return await msg.reply_text("تم الاذاعه")
            if text=="تحديث": os.system("git pull");return await msg.reply_text("تم التحديث")
            if text=="اعاده تشغيل": await msg.reply_text("جاري...");os.execl(sys.executable,sys.executable,*sys.argv)

        # م6
        if text=="نسبه الحب": return await msg.reply_text(f"نسبة الحب: {random.randint(1,100)}% ❤️")
        if text.startswith("ترجم عربي "): return await msg.reply_text(f"الترجمة: {GoogleTranslator(source='auto',target='ar').translate(text.replace('ترجم عربي ',''))}")
        if text.startswith("ساوند "): await msg.reply_text("جاري التحميل...")

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("menu",menu))
    app.add_handler(CommandHandler("panel",panel))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.ALL,handle))
    print("Tia شغال 100%")
    app.run_polling(drop_pending_updates=True)

if __name__=="__main__": main()
