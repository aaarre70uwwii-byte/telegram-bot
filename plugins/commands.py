# -*- coding: utf-8 -*-
#━━━━━━━━━━━━━━━━━━━━━━━━━━
#        ⚡ 𝐁𝐎𝐓 𝐓𝐢𝐚 ⚡
#     🤖 البوت المطور الرسمي 🤖
#━━━━━━━━━━
#   📌 ملف اوامر 𝐓𝐢𝐚 للجروبات والقنوات
#   📢 قناة التحديثات : https://t.me/eeccvu
#   👑 المطور : @rrrrxe | ID : 7488375443
#━━━━━━━━━━━━━━━━━━━━━━━━━━

from telethon import events

# دالة للتحقق انه جروب او قناة
def is_group(event):
    return event.is_group or event.is_channel

# ╭───❨ 🌟 𝐌1 : اوامر الاداره 🌟 ❩───╮
@bot.on(events.NewMessage(pattern=r'^رفع ادمن$'))
async def _(event):
    if not is_group(event): return
    # حط كود رفع الادمن هنا
    await event.reply("✅ تم رفع العضو ادمن")

@bot.on(events.NewMessage(pattern=r'^تنزيل ادمن$'))
async def _(event):
    if not is_group(event): return
    await event.reply("✅ تم تنزيل العضو من الادمنية")

@bot.on(events.NewMessage(pattern=r'^تثبيت$'))
async def _(event):
    if not is_group(event): return
    await event.reply("📌 تم تثبيت الرسالة")

# ╭───❨ 🛡️ 𝐌2 : اوامر الحمايه 🛡️ ❩───╮
@bot.on(events.NewMessage(pattern=r'^قفل الروابط$'))
async def _(event):
    if not is_group(event): return
    await event.reply("🔒 تم قفل الروابط")

@bot.on(events.NewMessage(pattern=r'^فتح الروابط$'))
async def _(event):
    if not is_group(event): return
    await event.reply("🔓 تم فتح الروابط")

# ╭───❨ 👑 𝐌3 : اوامر المطورين 👑 ❩───╮
@bot.on(events.NewMessage(pattern=r'^رفع مطور$'))
async def _(event):
    if event.sender_id != 7488375443: return # ايديك فقط
    await event.reply("👑 تم رفع العضو مطور")

# ╭───❨ 👥 𝐌4 : اوامر الاعضاء 👥 ❩───╮
@bot.on(events.NewMessage(pattern=r'^ايدي$'))
async def _(event):
    if not is_group(event): return
    user = await event.get_sender()
    await event.reply(f"🆔 ايديك : `{user.id}`\n👤 اسمك : {user.first_name}")

# ╭───❨ 📈 𝐌5 : الرفع والتنزيل 📈 ❩───╮
@bot.on(events.NewMessage(pattern=r'^رفع مميز$'))
async def _(event):
    if not is_group(event): return
    await event.reply("⭐ تم رفع العضو مميز")

# ╭───❨ 😂 𝐌6 : اوامر التحشيش 😂 ❩───╮
tia_fun = {
    "تاج": "🤴 هذا تاج الملك 👑",
    "ملك": "🧝‍♂️ انت الملك اليوم",
    "ملكه": "🧝‍♀️ انتي الملكة",
    "اثول": "🤦‍♀️ يمعود اثول",
    "جلب": "👩‍🎤 هوووه جلب",
    "مطي": "🧑‍🦯 مطي رسمي",
    "بوسه": "👩‍❤️‍💋‍👨 موواح 😘",
    "هديه": "🎁 هاي الك هديه"
}

for cmd, reply in tia_fun.items():
    @bot.on(events.NewMessage(pattern=fr'^{cmd}$'))
    async def _(event, r=reply):
        if not is_group(event): return
        await event.reply(r)

@bot.on(events.NewMessage(pattern=r'^نسبه الحب$'))
async def _(event):
    if not is_group(event): return
    await event.reply("✨ نسبة الحب بينكم : 92% ❤️")

# ╭───❨ 🎮 𝐌8 : اوامر التسليه 🎮 ❩───╮
@bot.on(events.NewMessage(pattern=r'^غنيلي$'))
async def _(event):
    if not is_group(event): return
    await event.reply("🎵 اختار اغنيه تريدها")

@bot.on(events.NewMessage(pattern=r'^زواج$'))
async def _(event):
    if not is_group(event): return
    await event.reply("💍 تم زواجكم مبارك")

# ╭───❨ 💰 𝐌9 : اوامر البنك 💰 ❩───╮
@bot.on(events.NewMessage(pattern=r'^انشاء حساب$'))
async def _(event):
    if not is_group(event): return
    await event.reply("💳 تم انشاء حساب بنكي الك")

@bot.on(events.NewMessage(pattern=r'^راتب$'))
async def _(event):
    if not is_group(event): return
    await event.reply("💸 تم استلام الراتب : 500$")

# ╭───❨ 🔒 𝐌10 : القفل والفتح 🔒 ❩───╮
locks = ["الروابط","الكلايش","الكيبورد","الاغاني","الصور","الفيديو"]
for lock in locks:
    @bot.on(events.NewMessage(pattern=fr'^قفل {lock}$'))
    async def _(event, l=lock):
        if not is_group(event): return
        await event.reply(f"🔒 تم قفل {l}")

    @bot.on(events.NewMessage(pattern=fr'^فتح {lock}$'))
    async def _(event, l=lock):
        if not is_group(event): return
        await event.reply(f"🔓 تم فتح {l}")

# ╭───❨ ⚙️ 𝐌11 : التفعيل والتعطيل ⚙️ ❩───╮
toggles = ["الرابط","الترحيب","الايدي","الردود","الرفع","الطرد","الالعاب"]
for t in toggles:
    @bot.on(events.NewMessage(pattern=fr'^تفعيل {t}$'))
    async def _(event, tg=t):
        if not is_group(event): return
        await event.reply(f"✅ تم تفعيل {tg}")

    @bot.on(events.NewMessage(pattern=fr'^تعطيل {t}$'))
    async def _(event, tg=t):
        if not is_group(event): return
        await event.reply(f"❌ تم تعطيل {tg}")

print("✅ تم تحميل ملف اوامر 𝐓𝐢𝐚 بنجاح")
