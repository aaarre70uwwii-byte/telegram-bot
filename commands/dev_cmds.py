from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import os, json, sys

app = Client("MyShieldBot")
OWNER_ID = int(os.getenv("OWNER_ID"))

DB_FILE = "data.json"
with open(DB_FILE,"r", encoding="utf-8") as f: db = json.load(f)

def save():
    with open(DB_FILE,"w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

def is_dev(user_id):
    return user_id == OWNER_ID or user_id in db["ranks"].get("dev", [])

# ========== عرض قائمة م5 - تشتغل في الجروب والخاص ==========
@app.on_callback_query(filters.regex("menu_5"))
async def show_dev_menu(client, query: CallbackQuery):
    if not is_dev(query.from_user.id):
        return await query.answer("❌ هذا الزر للمطورين فقط", show_alert=True)

    text = """**• اهلا بك عزي Dev**
━━━━━━━━━━━━
**- ردود التواصل:**
`اضف رد تواصل` `حذف رد تواصل` `ردود التواصل`

**- العام:**
`حظر عام` `كتم عام` `الغاء عام` `قائمه العام`

**- المطورين:**
`رفع Dev` `تنزيل Dev`

**- الردود العامه:**
`اضف رد عام` `الردود العامه` `مسح الردود العامه`

**- الكلايش:**
`ضع كليشه م1` الى `مسح كليشه م6`

**- النظام:**
`ذيع` `تحديث` `اعاده تشغيل`
━━━━━━━━━━━━"""
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ رجوع", callback_data="back_menu")]])
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

# ========== اهم الاوامر ==========
@app.on_message(filters.command(["رفع Dev","تنزيل Dev"]))
async def dev_rank(client, message: Message):
    if message.from_user.id!= OWNER_ID: return await message.reply("❌ للمالك الاساسي فقط")
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    if "رفع" in message.text:
        db["ranks"].setdefault("dev", []).append(uid); db["ranks"]["dev"] = list(set(db["ranks"]["dev"])); save()
        await message.reply(f"✅ تم رفع {message.reply_to_message.from_user.first_name} مطور ثانوي")
    else:
        if uid in db["ranks"].get("dev", []): db["ranks"]["dev"].remove(uid); save()
        await message.reply(f"✅ تم تنزيل {message.reply_to_message.from_user.first_name}")

@app.on_message(filters.command(["حظر عام","كتم عام"]))
async def gban(client, message: Message):
    if not is_dev(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الشخص")
    uid = message.reply_to_message.from_user.id
    key = "gban" if "حظر" in message.text else "gmute"
    db.setdefault(key, []).append(uid); db[key] = list(set(db[key])); save()
    await message.reply(f"✅ تم {'حظر' if key=='gban' else 'كتم'} عام")

@app.on_message(filters.command("ذيع"))
async def broadcast(client, message: Message):
    if not is_dev(message.from_user.id): return
    if not message.reply_to_message: return await message.reply("❌ رد على الرسالة")
    count=0
    for chat_id in db.get("chats", []):
        try: await client.forward_messages(chat_id, message.chat.id, message.reply_to_message.id); count+=1
        except: pass
    await message.reply(f"✅ تمت الاذاعة الى {count} قروب")

@app.on_message(filters.command(["تحديث","اعاده تشغيل"]))
async def restart(client, message: Message):
    if not is_dev(message.from_user.id): return
    if "تحديث" in message.text:
        global db
        with open(DB_FILE,"r", encoding="utf-8") as f: db = json.load(f)
        await message.reply("✅ تم التحديث")
    else:
        await message.reply("✅ جاري اعادة التشغيل...")
        os.execl(sys.executable, sys.executable, *sys.argv)
