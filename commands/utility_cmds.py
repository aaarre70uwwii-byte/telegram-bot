# -*- coding: utf-8 -*-
import os
import json
import random
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

app = Client("MyShieldBot")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

DB_FILE = "data.json"
try:
    with open(DB_FILE,"r", encoding="utf-8") as f: db = json.load(f)
except: db = {"ranks": {"dev": []}, "contact_replies": {}, "global_replies": {}}

def save():
    with open(DB_FILE,"w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

def is_dev(user_id):
    return user_id == OWNER_ID or user_id in db["ranks"].get("dev", [])

# ========== عرض قائمة م6 الاوامر الخدميه ==========
@app.on_callback_query(filters.regex("menu_6"))
async def show_service_menu(client, query: CallbackQuery):
    text = """**• اهلا بك عزي**
**- اوامر الخدميه :**
━━━━━━━━━━━━
**- النسب واللعب:**
`نسبه الحب` `نسبه الغباء - بالرد` `تحبه - بالرد` `شبيهي - شبيهتي`
`اهديه بالرد` `اهديه + يوزر الشخص` `نسبه انوثتها - بالرد` `نسبه رجولته - بالرد`
`البوت السحري`

**- البحث والترجمة:**
`قوقل + كلام البحث` `تطبيق + اسم التطبيق` `تحميل لعبه + اسم اللعبه`
`معنى + اسمك` `العمر + عمرك` `زخرف + اسمك`
`ترجم عربي + الكلام` `ترجم انقليزي + الكلام`

**- المحتوى:**
`قران` `اذكار` `شعر ، قصائد` `اقتباسات` `ثريد` `قصص ، كتب` `اطربني`
`اغاني` `هيدرات` `جداريات` `ميمز` `ايدت`
`قيفات: اطفال ، رومنسيه ، كوكسال ، كيبوب ، عيال ، بنات`
`افتارات: بنات ، عيال ، فنانين ، تطقيم ، كيبوب ، انمي`

**- اوامر اخرى:**
`ارسل + الكلام + اليوزر زاجل` `صيح` `صيح + اليوزر يزعجه خاص`
`افتاره بالرد` `البايو بالرد` `شرايك في افتاري` `افلام` `من ضافني`
`اضف رد المالك` `اضف رد انلاين` `اضف رد متعدد`
`تفعيل كليشة المطور : الافتار والبايو`

**- التحميل:**
`ساوند + الرابط` `تيك + الرابط` `تويتر + الرابط`
`تحويل الصيغ : صوت - تحويل - متحركه - بصمه`
━━━━━━━━━━━━"""
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ رجوع", callback_data="back_menu")]]))
    await query.answer()

# ========== 1. النسب واللعب ==========
@app.on_message(filters.group & filters.command("نسبه الحب"))
async def love(client, m: Message):
    if not m.reply_to_message: return await m.reply("❌ رد على الشخص")
    p = random.randint(1,100)
    u1 = m.from_user.first_name; u2 = m.reply_to_message.from_user.first_name
    await m.reply(f"**نسبه الحب بين {u1} و {u2}:** {p}% ❤️")

@app.on_message(filters.group & filters.command(["نسبه الغباء","نسبه انوثتها","نسبه رجولته"]))
async def percent(client, m: Message):
    if not m.reply_to_message: return await m.reply("❌ بالرد على الشخص")
    await m.reply(f"**{m.command[0]}:** {random.randint(1,100)}% 😂")

@app.on_message(filters.group & filters.command("تحبه"))
async def love_him(client, m: Message):
    if not m.reply_to_message: return await m.reply("❌ بالرد")
    ans = random.choice(['اي احبه', 'لا والله', 'نص ونص', 'بمووت فيه'])
    await m.reply(f"{m.reply_to_message.from_user.first_name} {ans}")

@app.on_message(filters.group & filters.command(["شبيهي","شبيهتي"]))
async def looklike(client, m: Message):
    animals = ['قطه', 'اسد', 'كلب', 'ارنب', 'ثعلب', 'ذئب', 'قرد']
    await m.reply(f"**شبيهك هو:** {random.choice(animals)} 😂")

@app.on_message(filters.group & filters.command("اهديه"))
async def gift(client, m: Message):
    if m.reply_to_message: user = m.reply_to_message.from_user.first_name
    elif len(m.command) > 1: user = m.command[1]
    else: return await m.reply("❌ رد على الشخص او اكتب اليوزر")
    gifts = ["🌹 وردة", "💍 خاتم", "🎁 هدية", "🍫 شوكولاته", "💎 الماس"]
    await m.reply(f"اهديت {user} {random.choice(gifts)}")

# ========== 2. البحث والترجمة ==========
@app.on_message(filters.group & filters.command("قوقل"))
async def google(client, m: Message):
    if len(m.command) < 2: return await m.reply("❌ الاستخدام: قوقل + كلام البحث")
    q = " ".join(m.command[1:])
    await m.reply(f"🔍 **بحث قوقل:** {q}\nhttps://www.google.com/search?q={q}")

@app.on_message(filters.group & filters.command(["ترجم عربي","ترجم انقليزي"]))
async def trans(client, m: Message):
    if len(m.command) < 2: return await m.reply("❌ الاستخدام: ترجم + النص")
    await m.reply(f"**الترجمة:** {' '.join(m.command[1:])}\n*ملاحظة: اربط API للترجمة الحقيقية*")

@app.on_message(filters.group & filters.command("زخرف"))
async def zakrf(client, m: Message):
    if len(m.command) < 2: return await m.reply("❌ الاستخدام: زخرف + اسمك")
    name = " ".join(m.command[1:])
    styles = [f"『{name}』", f"๖{name}๖", f"♛{name}♛", f"★{name}★", f"꧁{name}꧂", f"≪{name}≫"]
    await m.reply("**زخرفة اسمك:**\n" + "\n".join(styles))

@app.on_message(filters.group & filters.command(["معنى","العمر"]))
async def info(client, m: Message):
    if len(m.command) < 2: return await m.reply(f"❌ الاستخدام: {m.command[0]} + الكلمة")
    await m.reply(f"**{m.command[0]} {m.command[1]}:** قريباً *اربط API*")

# ========== 3. المحتوى ==========
quran_list = ["قل هو الله احد", "اية الكرسي", "سورة الفاتحة", "قل اعوذ برب الفلق"]
zekr_list = ["سبحان الله", "الحمد لله", "الله اكبر", "استغفر الله", "لا اله الا الله"]
poem_list = ["اذا الشعب يوما اراد الحياة", "وما نيل المطالب بالتمني", "قم للمعلم وفه التبجيلا"]

@app.on_message(filters.group & filters.command("قران"))
async def quran(client, m: Message): await m.reply(f"📖 **اية:**\n{random.choice(quran_list)}")
@app.on_message(filters.group & filters.command("اذكار"))
async def zekr(client, m: Message): await m.reply(f"📿 **ذكر:**\n{random.choice(zekr_list)}")
@app.on_message(filters.group & filters.command(["شعر","اقتباسات","ثريد"]))
async def quotes(client, m: Message): await m.reply(f"✍️ **{m.command[0]}:**\n{random.choice(poem_list)}")
@app.on_message(filters.group & filters.command(["ميمز","ايدت","هيدرات","جداريات","اغاني","اطربني"]))
async def media(client, m: Message): await m.reply(f"✅ سيتم ارسال {m.command[0]} عشوائي\n*اربط قاعدة ميديا*")

# ========== 4. اوامر اخرى ==========
@app.on_message(filters.group & filters.command("ارسل"))
async def zagel(client, m: Message):
    if len(m.command) < 4: return await m.reply("❌ الاستخدام: ارسل الكلام @اليوزر زاجل")
    text = " ".join(m.command[1:-1]); user = m.command[-1]
    await m.reply(f"📨 **زاجل الى {user}:**\n{text}")

@app.on_message(filters.group & filters.command("صيح"))
async def sayah(client, m: Message):
    if len(m.command) > 1: await m.reply(f"📢 تم ازعاج {m.command[1]} بالخاص")
    else: await m.reply("📢 صييييح 😂😂")

@app.on_message(filters.group & filters.command(["افتاره","البايو"]))
async def get_info(client, m: Message):
    if not m.reply_to_message: return await m.reply("❌ بالرد على الشخص")
    user = m.reply_to_message.from_user
    if "افتاره" in m.text: await m.reply(f"🖼️ **صورة {user.first_name}**")
    else: await m.reply(f"📝 **بايو {user.first_name}:**\n{user.bio or 'مافي بايو'}")

@app.on_message(filters.group & filters.command("نادي المطور"))
async def call_dev(client, m: Message):
    devs = db["ranks"].get("dev", []) + [OWNER_ID]
    await m.reply(f"📢 **المطورين:**\n{' '.join([f'`{d}`' for d in devs])}")

# ========== 5. التحميل ==========
@app.on_message(filters.group & filters.command(["ساوند","تيك","تويتر"]))
async def download(client, m: Message):
    if len(m.command) < 2: return await m.reply("❌ الاستخدام: الامر + الرابط")
    await m.reply(f"✅ جاري تحميل من {m.command[0]}:\n{m.command[1]}\n*اربط API تحميل*")

@app.on_message(filters.group & filters.command("تحويل"))
async def convert(client, m: Message):
    if not m.reply_to_message: return await m.reply("❌ رد على الفيديو/الصوت")
    await m.reply("✅ جاري التحويل... *اربط FFmpeg*")
