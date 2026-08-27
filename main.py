# -*- coding: utf-8 -*-
import os
import sys
from pyrogram import Client, filters
from pyrogram.types import Message

# 1. جلب متغيرات البيئة
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEV_ID = os.getenv("DEV_ID")

# فحص تأميني
if not all([API_ID, API_HASH, BOT_TOKEN, DEV_ID]):
    print("❌ خطأ حرج: يرجى التأكد من إدخال المتغيرات الأربعة")
    sys.exit(1)

# 2. تهيئة العقل المدبر
app = Client(
    "MyShieldBot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="commands")  # خليته commands زي ما هو عندك
)

# 3. أمر عرض القائمة الرئيسية - يشتغل خاص وجروب
@app.on_message(filters.command(["الاوامر", "help", "اوامري"]) | filters.regex("^(الاوامر|اوامري|help)$"))
async def main_menu_handler(client: Client, message: Message):
    menu_text = """
- ‌‌‏أهلاً بك عزي في قائمة الاوامر :
━━━━━━━━━━━━
◂ م1 : اوامر الادمنيه 👮‍♂️
◂ م2 : اوامر الاعدادات ⚙️
◂ م3 : اوامر القفل - الفتح 🔒
◂ م4 : اوامر التسليه 😂
◂ م5 : اوامر Dev 👑
◂ م6 : الاوامر الخدميه 🛠️
━━━━━━━━━━━━
💡 _لفتح أي قائمة، فقط اكتب الرمز الخاص بها (مثال: م1)_
"""
    await message.reply_text(text=menu_text)

# 4. رد اختبار سريع - يشتغل خاص وجروب
@app.on_message(filters.text & filters.regex("^(تست|test)$"))
async def test_handler(client: Client, message: Message):
    await message.reply_text("✅ البوت شغال 100% ويسمعك")

# 5. تشغيل البوت - الطريقة الصحيحة لـ Railway
print("⚡ جاري تهيئة وفحص ملفات الحماية والـ Plugins...")
app.run()
